"""
app.py
=====================================================================
Aplicação web (Flask) que lê o alfabeto manual de Libras pela webcam e
monta FRASES.

Como a frase é montada:
    - Segure um sinal por HOLD_SECONDS (padrão 1 s): a letra é confirmada
      e entra no texto. Um anel na tela mostra o progresso.
    - Depois de confirmada, a mesma letra só entra de novo se você trocar
      de sinal ou tirar a mão do quadro (evita "AAAAA" sem querer).
    - Comandos (pelo teclado ou pelos botões da página):
          ESPAÇO     -> espaço entre palavras
          ENTER      -> encerra a linha e vai para a de baixo
          BACKSPACE  -> apaga o último caractere
          botão Limpar -> apaga tudo

Uso:
    python app.py
Depois acesse http://localhost:5000 no navegador.
"""

import os
import threading
import time
from collections import Counter, deque

import cv2
import joblib
import numpy as np
from flask import Flask, Response, jsonify, render_template, request

from hand_utils import HandTracker, draw_landmarks

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "libras_rf_model.pkl")

CAMERA_INDEX = 2             # índice da câmera (celular). Troque para 3 se o 2 não funcionar.
CONFIDENCE_THRESHOLD = 0.65  # predições abaixo disso são descartadas
SMOOTHING_WINDOW = 8         # nº de predições recentes usadas na votação por maioria
STABILITY_MIN_RATIO = 0.5    # fração mínima de votos para considerar uma letra
HOLD_SECONDS = 1.0           # tempo segurando o sinal para a letra entrar no texto

app = Flask(__name__)

# --- Carrega o modelo treinado (gerado por train_model.py) ---
if not os.path.isfile(MODEL_PATH):
    raise FileNotFoundError(
        f"Modelo não encontrado em '{MODEL_PATH}'. Rode train_model.py antes de iniciar o app."
    )
bundle = joblib.load(MODEL_PATH)
model = bundle["model"]
label_encoder = bundle["label_encoder"]

tracker = HandTracker()
camera = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
if not camera.isOpened():
    raise RuntimeError(f"Não foi possível acessar a câmera (índice {CAMERA_INDEX}).")

prediction_buffer = deque(maxlen=SMOOTHING_WINDOW)

# Estado compartilhado entre o loop de vídeo e as rotas do Flask (threads diferentes)
state_lock = threading.Lock()
text_buffer = ""
current_state = {"letter": "-", "confidence": 0.0, "hand_visible": False, "progress": 0.0}
hold = {"letter": None, "start": 0.0, "locked": False}


def predict_letter(feature_vector: np.ndarray):
    """Retorna (letra, confiança). Abaixo do limiar, a letra é None."""
    probs = model.predict_proba([feature_vector])[0]
    best_idx = int(np.argmax(probs))
    confidence = float(probs[best_idx])

    if confidence < CONFIDENCE_THRESHOLD:
        return None, confidence

    letter = label_encoder.inverse_transform([best_idx])[0]
    return letter, confidence


def update_hold(candidate, hand_visible):
    """Controla a confirmação da letra e devolve o progresso (0 a 1).

    candidate: letra estável do frame atual, ou None (sem confiança).
    """
    global text_buffer
    now = time.monotonic()

    with state_lock:
        if not hand_visible:
            # mão fora do quadro: libera a mesma letra para ser digitada de novo
            hold.update(letter=None, locked=False)
            return 0.0

        if candidate is None:
            if not hold["locked"]:
                hold["letter"] = None
                return 0.0
            return 1.0  # continua "travada" na letra já confirmada

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


def apply_command(action):
    """Aplica um comando de edição ao texto. Devolve o texto novo, ou None se a ação for inválida."""
    global text_buffer
    with state_lock:
        if action == "space":
            # ignora espaço no começo, depois de espaço ou no começo de uma linha
            if text_buffer and not text_buffer.endswith((" ", "\n")):
                text_buffer += " "
        elif action == "newline":
            if text_buffer:
                text_buffer = text_buffer.rstrip(" ") + "\n"
        elif action == "backspace":
            text_buffer = text_buffer[:-1]
        elif action == "clear":
            text_buffer = ""
        else:
            return None
        return text_buffer


def generate_frames():
    """Lê a webcam, processa, desenha overlays e produz os frames JPEG (MJPEG)."""
    global current_state

    while True:
        ok, frame = camera.read()
        if not ok:
            break

        frame = cv2.flip(frame, 1)
        feature_vector, raw_landmarks = tracker.process(frame)
        hand_visible = raw_landmarks is not None

        if not hand_visible:
            prediction_buffer.clear()
            update_hold(None, False)
            current_state = {"letter": "-", "confidence": 0.0, "hand_visible": False, "progress": 0.0}
            cv2.putText(frame, "Nenhuma mao detectada", (20, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        else:
            draw_landmarks(frame, raw_landmarks)
            letter, confidence = predict_letter(feature_vector)

            if letter is not None:
                prediction_buffer.append(letter)

            # Letra "candidata": só vale se este frame teve confiança e a votação é estável
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
                "progress": progress,
            }

            # --- Overlay no próprio vídeo ---
            cv2.rectangle(frame, (10, 10), (280, 75), (0, 0, 0), -1)
            cv2.putText(frame, current_state["letter"], (20, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 255, 0), 3)
            cv2.putText(frame, f"{confidence * 100:.0f}%", (120, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 200, 200), 2)
            cv2.rectangle(frame, (10, 80), (10 + int(270 * progress), 86), (0, 200, 0), -1)

        ok, buffer = cv2.imencode(".jpg", frame)
        if not ok:
            continue

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/current_letter")
def current_letter():
    """Letra atual, progresso de confirmação e o texto completo."""
    with state_lock:
        text = text_buffer
    return jsonify({**current_state, "text": text})


@app.route("/command", methods=["POST"])
def command():
    """Recebe {"action": "space" | "newline" | "backspace" | "clear"}."""
    data = request.get_json(silent=True) or {}
    result = apply_command(data.get("action"))
    if result is None:
        return jsonify({"error": "ação inválida"}), 400
    return jsonify({"text": result})


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
    finally:
        camera.release()
        tracker.close()