"""
number_recognizer.py
=====================================================================
Módulo responsável pelo reconhecimento de numerais em Libras (0 a 9)
baseado na extração e cinemática dos 21 landmarks 3D da mão.

Princípios Biomecânicos em Libras:
  - 0: Dedos curvados com as pontas unidas à ponta do polegar ("O").
  - 1: Indicador estendido para cima; médio, anelar e mínimo dobrados na palma.
  - 2: Indicador e médio estendidos para cima ("V"); anelar e mínimo dobrados.
  - 3: Variação cardinal: Polegar, indicador e médio estendidos; anelar e mínimo dobrados.
       Variação quantitativa: Indicador, médio e anelar estendidos; mínimo fechado com polegar.
  - 4: Quatro dedos estendidos (indicador a mínimo); polegar cruzado na palma.
  - 5: Indicador e médio curvados/dobrados para a frente (~90° gancho/garra); anelar e mínimo dobrados.
  - 6: Polegar estendido para cima; indicador curvado tocando o polegar (laço de 6); outros dedos dobrados.
  - 7: Polegar e indicador abertos em ângulo de "7" (indicador para frente/lado, polegar para cima).
  - 8: Punho fechado com os quatro dedos dobrados e o polegar sobre os dedos (semelhante ao S).
  - 9: Indicador curvado para baixo (inverso do 6); outros dedos fechados na palma.
"""

import os
import joblib
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NUMBERS_MODEL_PATH = os.path.join(BASE_DIR, "models", "libras_numbers_rf_model.pkl")


def dist_3d(p1, p2):
    """Calcula a distância euclidiana 3D entre dois pontos."""
    return float(np.linalg.norm(np.array(p1) - np.array(p2)))


def extract_finger_features(landmarks_3d):
    """
    Analisa a pose dos dedos a partir dos 21 landmarks (x, y, z):
      0: Pulso
      Polegar: 1(CMC), 2(MCP), 3(IP), 4(TIP)
      Indicador: 5(MCP), 6(PIP), 7(DIP), 8(TIP)
      Médio: 9(MCP), 10(PIP), 11(DIP), 12(TIP)
      Anelar: 13(MCP), 14(PIP), 15(DIP), 16(TIP)
      Mínimo: 17(MCP), 18(PIP), 19(DIP), 20(TIP)
    """
    pts = np.array(landmarks_3d, dtype=np.float32)
    wrist = pts[0]
    middle_mcp = pts[9]
    palm_size = dist_3d(wrist, middle_mcp)
    if palm_size < 1e-5:
        palm_size = 1.0

    # Normalização em relação ao pulso e tamanho da palma
    norm_pts = (pts - wrist) / palm_size

    # Spans (distância direta da ponta do dedo à sua junta MCP correspondente)
    idx_span = dist_3d(norm_pts[8], norm_pts[5])
    mid_span = dist_3d(norm_pts[12], norm_pts[9])
    ring_span = dist_3d(norm_pts[16], norm_pts[13])
    pinky_span = dist_3d(norm_pts[20], norm_pts[17])
    thumb_span = dist_3d(norm_pts[4], norm_pts[2])

    # Estados de extensão
    index_ext = idx_span >= 0.45
    middle_ext = mid_span >= 0.45
    ring_ext = ring_span >= 0.45
    pinky_ext = pinky_span >= 0.45

    # Dobra parcial / gancho (hook) para indicador e médio
    index_hooked = (0.20 <= idx_span < 0.45)
    middle_hooked = (0.20 <= mid_span < 0.45)

    # Polegar
    thumb_dist_wrist = dist_3d(norm_pts[4], norm_pts[0])
    thumb_to_index_tip = dist_3d(norm_pts[4], norm_pts[8])
    thumb_y = norm_pts[4][1]
    thumb_ext = thumb_dist_wrist >= 0.80

    return {
        "palm_size": palm_size,
        "norm_pts": norm_pts,
        "idx_span": idx_span,
        "mid_span": mid_span,
        "ring_span": ring_span,
        "pinky_span": pinky_span,
        "thumb_span": thumb_span,
        "thumb_dist_wrist": thumb_dist_wrist,
        "thumb_y": thumb_y,
        "thumb_ext": thumb_ext,
        "index_ext": index_ext,
        "middle_ext": middle_ext,
        "ring_ext": ring_ext,
        "pinky_ext": pinky_ext,
        "index_hooked": index_hooked,
        "middle_hooked": middle_hooked,
        "thumb_to_index_tip": thumb_to_index_tip,
    }


def classify_libras_number(landmarks_3d):
    """
    Classifica a configuração da mão em um dos numerais de Libras (0 a 9)
    com base nas regras cinemáticas oficiais de datilologia numérica.
    """
    f = extract_finger_features(landmarks_3d)
    pts = f["norm_pts"]

    ext_count = sum([f["index_ext"], f["middle_ext"], f["ring_ext"], f["pinky_ext"]])

    # 4 (Quatro): Quatro dedos estendidos para cima, polegar recolhido
    if ext_count == 4:
        return "4", 0.96, "Quatro (4 dedos estendidos)"

    # 3 (Três):
    # Forma A (Libras cardinal): Polegar, Indicador e Médio estendidos
    if f["thumb_ext"] and f["index_ext"] and f["middle_ext"] and not f["ring_ext"] and not f["pinky_ext"]:
        return "3", 0.94, "Três (Polegar, Indicador e Médio estendidos)"
    # Forma B (Quantitativa/Variante): Indicador, Médio e Anelar estendidos
    if f["index_ext"] and f["middle_ext"] and f["ring_ext"] and not f["pinky_ext"]:
        return "3", 0.92, "Três (Indicador, Médio e Anelar estendidos)"

    # 2 (Dois): Indicador e médio estendidos (sem polegar)
    if f["index_ext"] and f["middle_ext"] and not f["ring_ext"] and not f["pinky_ext"] and not f["thumb_ext"]:
        return "2", 0.95, "Dois (Indicador e Médio em V)"

    # 6 (Seis): Polegar alto estendido e indicador tocando a ponta formando laço
    if f["thumb_y"] >= 1.25 and f["thumb_to_index_tip"] < 0.25 and not f["middle_ext"] and not f["ring_ext"] and not f["pinky_ext"]:
        return "6", 0.92, "Seis (Polegar estendido, indicador em laço)"

    # 7 (Sete): Polegar e indicador abertos em ângulo de 7 (afastados)
    if f["thumb_ext"] and f["index_ext"] and f["thumb_to_index_tip"] >= 0.40 and not f["middle_ext"] and not f["ring_ext"] and not f["pinky_ext"]:
        return "7", 0.93, "Sete (Polegar e indicador em formato de 7)"

    # 1 (Um): Apenas indicador estendido (médio, anelar, mínimo dobrados)
    if f["index_ext"] and not f["middle_ext"] and not f["ring_ext"] and not f["pinky_ext"] and not f["thumb_ext"]:
        return "1", 0.94, "Um (Indicador estendido)"

    # 0 (Zero): Pontas em círculo formando "O", polegar na altura média
    if f["thumb_to_index_tip"] < 0.20 and f["thumb_y"] < 1.20 and ext_count == 0:
        conf = max(0.75, 1.0 - (f["thumb_to_index_tip"] * 0.8))
        return "0", min(conf, 0.98), "Zero (Dedos em O)"

    # 5 (Cinco): Indicador e médio curvados para a frente em gancho (~90°)
    if f["index_hooked"] and f["middle_hooked"] and not f["ring_ext"] and not f["pinky_ext"] and not f["thumb_ext"]:
        return "5", 0.90, "Cinco (Indicador e Médio em gancho)"

    # 9 (Nove): Indicador curvado para baixo (inverso do 6, sem tocar polegar)
    if pts[8][1] < pts[6][1] and f["idx_span"] >= 0.22 and f["thumb_to_index_tip"] >= 0.25 and not f["middle_ext"] and not f["ring_ext"] and not f["pinky_ext"]:
        return "9", 0.88, "Nove (Indicador curvado para baixo)"

    # 8 (Oito): Punho fechado (todos os dedos dobrados na palma, polegar cruzado)
    if ext_count == 0 and not f["thumb_ext"]:
        return "8", 0.89, "Oito (Mão em punho fechado)"

    return None, 0.0, "Sinal não reconhecido"


def create_synthetic_landmarks(digit_str: str) -> np.ndarray:
    """
    Gera as 21 coordenadas 3D para um determinado dígito (0 a 9)
    usado para testes unitários, validação e calibração de modelos.
    """
    pts = np.zeros((21, 3), dtype=np.float32)

    # Base da mão (Pulso e MCPs)
    pts[0] = [0.0, 0.0, 0.0]       # Pulso
    pts[1] = [-0.2, 0.2, 0.0]      # Polegar CMC
    pts[2] = [-0.35, 0.35, 0.0]    # Polegar MCP
    pts[3] = [-0.45, 0.5, 0.0]     # Polegar IP
    pts[4] = [-0.55, 0.65, 0.0]    # Polegar TIP (padrão)

    pts[5] = [-0.25, 0.8, 0.0]     # Indicador MCP
    pts[6] = [-0.28, 1.1, 0.0]     # Indicador PIP
    pts[7] = [-0.30, 1.3, 0.0]     # Indicador DIP
    pts[8] = [-0.32, 1.5, 0.0]     # Indicador TIP (estendido)

    pts[9] = [0.0, 0.85, 0.0]      # Médio MCP
    pts[10] = [0.0, 1.2, 0.0]      # Médio PIP
    pts[11] = [0.0, 1.45, 0.0]     # Médio DIP
    pts[12] = [0.0, 1.7, 0.0]      # Médio TIP (estendido)

    pts[13] = [0.25, 0.8, 0.0]     # Anelar MCP
    pts[14] = [0.28, 1.1, 0.0]     # Anelar PIP
    pts[15] = [0.30, 1.3, 0.0]     # Anelar DIP
    pts[16] = [0.32, 1.5, 0.0]     # Anelar TIP (estendido)

    pts[17] = [0.45, 0.7, 0.0]     # Mínimo MCP
    pts[18] = [0.50, 0.95, 0.0]    # Mínimo PIP
    pts[19] = [0.53, 1.15, 0.0]    # Mínimo DIP
    pts[20] = [0.55, 1.35, 0.0]    # Mínimo TIP (estendido)

    def fold_finger(mcp_idx):
        pts[mcp_idx + 1] = pts[mcp_idx] + [0.0, 0.15, 0.1]
        pts[mcp_idx + 2] = pts[mcp_idx] + [0.0, 0.10, 0.18]
        pts[mcp_idx + 3] = pts[mcp_idx] + [0.0, 0.02, 0.15]

    def hook_finger(mcp_idx):
        pts[mcp_idx + 1] = pts[mcp_idx] + [0.0, 0.20, 0.0]
        pts[mcp_idx + 2] = pts[mcp_idx] + [0.0, 0.20, 0.18]
        pts[mcp_idx + 3] = pts[mcp_idx] + [0.0, 0.10, 0.22]

    def fold_thumb():
        pts[3] = [-0.15, 0.40, 0.10]
        pts[4] = [-0.05, 0.45, 0.15]

    if digit_str == "0":
        fold_thumb()
        pts[4] = [-0.16, 0.90, 0.10]
        pts[6] = [-0.20, 0.92, 0.08]
        pts[7] = [-0.18, 0.92, 0.10]
        pts[8] = [-0.16, 0.91, 0.10]
        fold_finger(9)
        fold_finger(13)
        fold_finger(17)

    elif digit_str == "1":
        fold_thumb()
        fold_finger(9)
        fold_finger(13)
        fold_finger(17)

    elif digit_str == "2":
        fold_thumb()
        fold_finger(13)
        fold_finger(17)

    elif digit_str == "3":
        fold_finger(13)
        fold_finger(17)

    elif digit_str == "4":
        fold_thumb()

    elif digit_str == "5":
        fold_thumb()
        hook_finger(5)
        hook_finger(9)
        fold_finger(13)
        fold_finger(17)

    elif digit_str == "6":
        pts[3] = [-0.35, 0.90, 0.0]
        pts[4] = [-0.35, 1.25, 0.0]
        pts[6] = [-0.30, 1.20, 0.0]
        pts[7] = [-0.33, 1.22, 0.0]
        pts[8] = [-0.35, 1.23, 0.0]
        fold_finger(9)
        fold_finger(13)
        fold_finger(17)

    elif digit_str == "7":
        pts[4] = [-0.40, 0.80, 0.0]
        pts[8] = [0.35, 0.85, 0.0]
        fold_finger(9)
        fold_finger(13)
        fold_finger(17)

    elif digit_str == "8":
        fold_thumb()
        fold_finger(5)
        fold_finger(9)
        fold_finger(13)
        fold_finger(17)

    elif digit_str == "9":
        fold_thumb()
        pts[6] = [-0.25, 0.95, 0.0]
        pts[7] = [-0.25, 0.90, 0.15]
        pts[8] = [-0.25, 0.70, 0.20]  # y do TIP menor que y do PIP
        fold_finger(9)
        fold_finger(13)
        fold_finger(17)

    return pts


class LibrasNumberRecognizer:
    """
    Reconhecedor de números em Libras (0 a 9) com arquitetura híbrida
    (Cinemática 3D + Modelo Machine Learning quando disponível).
    """

    def __init__(self, model_path: str = NUMBERS_MODEL_PATH, use_ml: bool = True):
        self.supported_digits = [str(i) for i in range(10)]
        self.use_ml = use_ml
        self.model = None
        self.label_encoder = None

        if self.use_ml:
            import tempfile
            temp_path = os.path.join(tempfile.gettempdir(), "libras_numbers_rf_model.pkl")
            candidates = [model_path, temp_path]
            for p in candidates:
                if os.path.isfile(p):
                    try:
                        bundle = joblib.load(p)
                        self.model = bundle.get("model")
                        self.label_encoder = bundle.get("label_encoder")
                        break
                    except Exception:
                        pass

            if self.model is None:
                self._train_calibrated_model()

    def _train_calibrated_model(self):
        """Treina e calibra em memória um classificador RandomForest para os 10 dígitos."""
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.preprocessing import LabelEncoder
            from hand_utils import normalize_landmarks

            X, y = [], []
            for d in range(10):
                base_pts = create_synthetic_landmarks(str(d))
                for _ in range(30):
                    noise = np.random.normal(0, 0.02, base_pts.shape).astype(np.float32)
                    scale = np.random.uniform(0.85, 1.15)
                    perturbed = (base_pts + noise) * scale
                    norm = normalize_landmarks(perturbed)
                    vel = np.random.normal(0, 0.005, norm.shape).astype(np.float32)
                    X.append(np.concatenate([norm, vel]))
                    y.append(str(d))

            X = np.array(X)
            le = LabelEncoder()
            y_enc = le.fit_transform(y)
            rf = RandomForestClassifier(n_estimators=40, max_depth=10, random_state=42)
            rf.fit(X, y_enc)
            self.model = rf
            self.label_encoder = le
        except Exception as e:
            print(f"[NumberRecognizer] Calibração de modelo ML em memória falhou ({e}). Usando cinemática.")

    def predict(self, raw_landmarks, feature_vector: np.ndarray = None):
        """
        Recebe os 21 landmarks brutos da mão e opcionalmente o vetor de features.
        Retorna:
          predicted_digit : str | None ("0" a "9")
          confidence      : float (0.0 a 1.0)
          details         : str
        """
        if raw_landmarks is None:
            return None, 0.0, "Sem mão detectada"

        if hasattr(raw_landmarks[0], "x"):
            pts = np.array([[lm.x, lm.y, lm.z] for lm in raw_landmarks], dtype=np.float32)
        else:
            pts = np.array(raw_landmarks, dtype=np.float32)

        # 1. Avaliação cinemática
        k_digit, k_conf, k_desc = classify_libras_number(pts)

        # 2. Avaliação ML (se disponível)
        if self.model is not None and feature_vector is not None:
            try:
                probs = self.model.predict_proba([feature_vector])[0]
                ml_idx = int(np.argmax(probs))
                ml_conf = float(probs[ml_idx])
                ml_digit = self.label_encoder.inverse_transform([ml_idx])[0]

                if ml_digit == k_digit:
                    final_conf = min(0.99, max(k_conf, ml_conf) + 0.05)
                    return ml_digit, final_conf, f"{k_desc} (Confirmado por ML: {ml_conf*100:.0f}%)"
                elif k_conf >= 0.88:
                    return k_digit, k_conf, k_desc
                elif ml_conf >= 0.85:
                    return ml_digit, ml_conf, f"Número {ml_digit} (Predição ML)"
            except Exception:
                pass

        return k_digit, k_conf, k_desc
