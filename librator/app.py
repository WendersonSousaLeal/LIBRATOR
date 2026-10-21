"""
app.py
=====================================================================
Librator MVP - Tradutor de Datilologia em Libras em tempo real
com montagem de frases, síntese de voz e histórico acessível.
"""

import base64
import datetime
import os
import sys
import threading
import time
from collections import Counter, deque

import cv2
import joblib
import numpy as np
from flask import Flask, Response, jsonify, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from hand_utils import HandTracker, draw_landmarks

MODEL_PATH = os.path.join(BASE_DIR, "models", "libras_rf_model.pkl")

# --- Configurações Padrão ---
CAMERA_INDEX = 2
CONFIDENCE_THRESHOLD = 0.65
SMOOTHING_WINDOW = 8
STABILITY_MIN_RATIO = 0.5
HOLD_SECONDS = 1.0
MODE_MIN_MASS = 0.25   # probabilidade mínima que o grupo do modo (letras/números) precisa ter

app = Flask(__name__)

# --- Carrega o Modelo Treinado ---
if not os.path.isfile(MODEL_PATH):
    raise FileNotFoundError(
        f"Modelo não encontrado em '{MODEL_PATH}'. Rode train_model.py antes de iniciar o app."
    )

bundle = joblib.load(MODEL_PATH)
model = bundle["model"]
label_encoder = bundle["label_encoder"]
tracker = HandTracker()

# --- Modos: LETRAS (A-Z) e NÚMEROS (0-9) ---
# O mesmo modelo guarda as duas famílias de sinais. Em cada modo, só as classes
# daquele grupo são consideradas, o que evita confundir, por exemplo, V com 2 ou O com 0.
CLASS_NAMES = [str(c) for c in label_encoder.classes_]
LETTER_MASK = np.array([len(c) == 1 and c.isalpha() for c in CLASS_NAMES], dtype=float)
NUMBER_MASK = np.array([len(c) == 1 and c.isdigit() for c in CLASS_NAMES], dtype=float)
current_mode = "letters"


def mode_mask(mode):
    return NUMBER_MASK if mode == "numbers" else LETTER_MASK


def mode_ready(mode):
    """True se o modelo tem classes treinadas para o modo."""
    return bool(mode_mask(mode).sum() > 0)


# --- Gerenciador de Câmera em Thread Dedicada (Zero Latência e Não-Bloqueante) ---
class CameraThread:
    """Thread dedicada que captura continuamente frames da câmera em segundo plano.
    Elimina travamentos no Flask, previne contenção de locks e suporta reconexão rápida."""
    def __init__(self, initial_index=CAMERA_INDEX):
        self.lock = threading.Lock()
        self.index = initial_index
        self.cap = None
        self.current_frame = None
        self.is_opened = False
        self.running = True
        self.change_requested = False
        self.new_index = initial_index

        self.worker = threading.Thread(target=self._capture_loop, daemon=True)
        self.worker.start()

    def _open_device(self, idx):
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None

        print(f"[CameraThread] Tentando abrir câmera no índice {idx}...")
        # Tenta com DirectShow
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if not cap.isOpened():
            # Fallback para backend padrão
            cap = cv2.VideoCapture(idx)

        # Só vale se a câmera realmente entregar imagem (tenta por ~1 s)
        works = False
        if cap.isOpened():
            for _ in range(10):
                ok, _frame = cap.read()
                if ok and _frame is not None:
                    works = True
                    break
                time.sleep(0.1)

        if works:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap = cap
            self.index = idx
            self.is_opened = True
            print(f"[CameraThread] Câmera no índice {idx} conectada com sucesso!")
            return True

        try:
            cap.release()
        except Exception:
            pass
        self.cap = None
        self.is_opened = False
        print(f"[CameraThread] Câmera no índice {idx} não entregou imagem.")
        return False

    def switch_camera(self, new_index):
        with self.lock:
            self.new_index = new_index
            self.change_requested = True

    def get_latest_frame(self):
        with self.lock:
            if self.current_frame is not None:
                return True, self.current_frame.copy()
            return False, None

    def _capture_loop(self):
        # Tenta o índice inicial
        opened = self._open_device(self.index)
        if not opened:
            # Tenta auto-scan dos outros índices (o 0 fica por último)
            for fallback_idx in [2, 3, 1, 0]:
                if fallback_idx != self.index:
                    if self._open_device(fallback_idx):
                        break

        fail_count = 0
        while self.running:
            # Troca de câmera sob demanda
            with self.lock:
                if self.change_requested:
                    self._open_device(self.new_index)
                    self.change_requested = False
                    fail_count = 0

            if self.cap is not None and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    fail_count = 0
                    with self.lock:
                        self.current_frame = frame
                        self.is_opened = True
                    time.sleep(0.015)  # ~30-50 fps
                else:
                    fail_count += 1
                    if fail_count > 40:
                        # Auto-recuperação
                        print("[CameraThread] Reconectando à câmera...")
                        self._open_device(self.index)
                        fail_count = 0
                    time.sleep(0.05)
            else:
                time.sleep(0.2)

    def release(self):
        self.running = False
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass

camera_thread = CameraThread(CAMERA_INDEX)
CameraManager = CameraThread

# --- Estado Compartilhado ---
state_lock = threading.Lock()

text_buffer = ""
phrase_history = []
history_counter = 1

prediction_buffer = deque(maxlen=SMOOTHING_WINDOW)
current_state = {
    "letter": "-",
    "confidence": 0.0,
    "hand_visible": False,
    "progress": 0.0,
}
hold = {"letter": None, "start": 0.0, "locked": False}


def predict_letter(feature_vector: np.ndarray):
    """Retorna (letra, confiança). Abaixo do limiar, a letra é None."""
    probs = model.predict_proba([feature_vector])[0]
    masked = probs * mode_mask(current_mode)   # só as classes do modo atual
    total = float(masked.sum())

    # O modelo não tem esse grupo treinado, ou o sinal não parece nada deste modo
    if total < MODE_MIN_MASS:
        return None, float(masked.max()) if masked.size else 0.0

    masked = masked / total
    best_idx = int(np.argmax(masked))
    confidence = float(masked[best_idx])

    if confidence < CONFIDENCE_THRESHOLD:
        return None, confidence

    symbol = str(label_encoder.inverse_transform([best_idx])[0])
    return symbol, confidence


def update_hold(candidate, hand_visible):
    """Controla a confirmação da letra com base no tempo de permanência estável."""
    global text_buffer
    now = time.monotonic()

    with state_lock:
        if not hand_visible:
            hold.update(letter=None, locked=False)
            return 0.0

        if candidate is None:
            if not hold["locked"]:
                hold["letter"] = None
                return 0.0
            return 1.0

        if candidate != hold["letter"]:
            hold.update(letter=candidate, start=now, locked=False)
            return 0.0

        if hold["locked"]:
            return 1.0

        progress = min((now - hold["start"]) / HOLD_SECONDS, 1.0)
        if progress >= 1.0:
            text_buffer += candidate
            hold["locked"] = True
        return progress


def apply_command(action, payload=None):
    """Aplica comandos de edição e gerenciamento do histórico."""
    global text_buffer, history_counter, current_mode
    payload = payload or {}

    with state_lock:
        if action == "space":
            if text_buffer and not text_buffer.endswith(" "):
                text_buffer += " "

        elif action == "insert_text":
            new_text = payload.get("text", "").strip()
            is_autocomplete = payload.get("is_autocomplete", False)
            if new_text:
                if is_autocomplete:
                    words = text_buffer.rstrip().split(" ")
                    if words:
                        words[-1] = new_text
                        text_buffer = " ".join(words) + " "
                    else:
                        text_buffer = new_text + " "
                else:
                    if text_buffer and not text_buffer.endswith(" "):
                        text_buffer += " "
                    text_buffer += new_text + " "

        elif action == "conclude" or action == "newline":
            phrase = text_buffer.strip()
            if phrase:
                phrase_history.append({
                    "id": history_counter,
                    "text": phrase,
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
                })
                history_counter += 1
                text_buffer = ""

        elif action == "backspace":
            text_buffer = text_buffer[:-1]

        elif action == "clear":
            text_buffer = ""

        elif action == "clear_history":
            phrase_history.clear()

        elif action == "set_mode":
            mode = payload.get("mode")
            if mode in ("letters", "numbers"):
                current_mode = mode
                prediction_buffer.clear()
                hold.update(letter=None, locked=False)

        elif action == "set_camera":
            idx_str = str(payload.get("index", "0"))
            if idx_str.isdigit():
                camera_thread.switch_camera(int(idx_str))

        else:
            return None

        return {
            "text": text_buffer,
            "history": list(phrase_history),
            "mode": current_mode
        }


def process_single_frame(frame):
    """Processa um frame de vídeo através do MediaPipe e do RandomForest."""
    global current_state

    feature_vector, raw_landmarks = tracker.process(frame)
    hand_visible = raw_landmarks is not None

    if not hand_visible:
        prediction_buffer.clear()
        update_hold(None, False)
        current_state = {
            "letter": "-",
            "confidence": 0.0,
            "hand_visible": False,
            "progress": 0.0
        }
        return current_state, None
    else:
        letter, confidence = predict_letter(feature_vector)
        if letter is not None:
            prediction_buffer.append(letter)

        candidate = None
        if letter is not None and prediction_buffer:
            voted_letter, votes = Counter(prediction_buffer).most_common(1)[0]
            if votes / len(prediction_buffer) >= STABILITY_MIN_RATIO:
                candidate = voted_letter

        progress = update_hold(candidate, True)
        current_state = {
            "letter": candidate if candidate else "?",
            "confidence": confidence,
            "hand_visible": True,
            "progress": progress
        }
        return current_state, raw_landmarks


def make_fallback_frame():
    canvas = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(canvas, "Librator MVP", (210, 190),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (232, 163, 61), 2)
    cv2.putText(canvas, "Aguardando camera...", (180, 240),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
    cv2.putText(canvas, "Selecione o indice ou use a Camera do Navegador", (90, 290),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (79, 209, 197), 1)
    ok, buffer = cv2.imencode(".jpg", canvas)
    return buffer.tobytes() if ok else b""


def generate_frames():
    """Lê frames do CameraThread, processa landmarks e renderiza o overlay."""
    while True:
        ok, frame = camera_thread.get_latest_frame()
        if not ok or frame is None:
            buf = make_fallback_frame()
            if buf:
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + buf + b"\r\n")
            time.sleep(0.1)
            continue

        frame = cv2.flip(frame, 1)
        state, raw_landmarks = process_single_frame(frame)

        if not state["hand_visible"]:
            cv2.putText(frame, "Nenhuma mao detectada", (20, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        else:
            draw_landmarks(frame, raw_landmarks)
            # Overlay visual superior esquerdo
            cv2.rectangle(frame, (10, 10), (280, 75), (0, 0, 0), -1)
            cv2.putText(frame, state["letter"], (20, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 255, 0), 3)
            cv2.putText(frame, f"{state['confidence'] * 100:.0f}%", (120, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
            if state["progress"] > 0:
                cv2.rectangle(frame, (10, 75), (10 + int(270 * state["progress"]), 80), (0, 220, 0), -1)

        ok, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not ok:
            continue

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")


# --- Rotas HTTP ---

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/current_letter")
def current_letter():
    """Estado em tempo real da letra, progresso e frase atual."""
    with state_lock:
        text = text_buffer
        hist = list(phrase_history)
    return jsonify({
        **current_state,
        "text": text,
        "history": hist,
        "mode": current_mode,
        "mode_ready": mode_ready(current_mode),
        "camera_index": camera_thread.index,
        "camera_opened": camera_thread.is_opened
    })


@app.route("/process_frame", methods=["POST"])
def process_client_frame():
    """Permite que o navegador envie frames capturados via HTML5 getUserMedia."""
    data = request.get_json(silent=True) or {}
    image_data = data.get("image")
    if not image_data:
        return jsonify({"error": "Nenhuma imagem fornecida"}), 400

    try:
        if "," in image_data:
            image_data = image_data.split(",")[1]
        raw_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(raw_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            return jsonify({"error": "Falha na decodificação"}), 400

        state, _ = process_single_frame(frame)
        with state_lock:
            text = text_buffer
            hist = list(phrase_history)

        return jsonify({
            **state,
            "text": text,
            "history": hist,
            "mode": current_mode,
            "mode_ready": mode_ready(current_mode)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/command", methods=["POST"])
def command():
    data = request.get_json(silent=True) or {}
    action = data.get("action")
    payload = data.get("payload", {})
    result = apply_command(action, payload)
    if result is None:
        return jsonify({"error": "Ação inválida"}), 400
    return jsonify(result)


@app.route("/history")
def get_history():
    with state_lock:
        return jsonify(list(phrase_history))


@app.route("/download_history")
def download_history():
    """Download das frases salvas no histórico em formato .txt."""
    with state_lock:
        hist = list(phrase_history)

    lines = [
        "============================================================",
        "  LIBRATOR MVP - HISTÓRICO DE FRASES TRADUZIDAS",
        f"  Exportado em: {datetime.datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}",
        "============================================================\n"
    ]

    if not hist:
        lines.append("Nenhuma frase registrada no histórico.\n")
    else:
        for idx, item in enumerate(hist, 1):
            lines.append(f"{idx}. [{item['timestamp']}] {item['text']}")

    lines.append("\n============================================================")
    content = "\n".join(lines)

    return Response(
        content,
        mimetype="text/plain; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=historico_librator.txt"}
    )


@app.route("/cameras")
def get_cameras():
    """Retorna lista de opções de câmera disponíveis."""
    return jsonify([
        {"index": 0, "name": "Índice 0 (Webcam padrão)"},
        {"index": 1, "name": "Índice 1 (Câmera secundária / Celular)"},
        {"index": 2, "name": "Índice 2 (DroidCam / Iriun)"},
        {"index": 3, "name": "Índice 3 (Virtual / USB)"},
        {"index": "browser", "name": "🌐 Câmera do Navegador (HTML5)"}
    ])


if __name__ == "__main__":
    try:
        print("[Librator MVP] Servidor rodando em http://localhost:5000")
        app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
    finally:
        camera_thread.release()
        tracker.close()