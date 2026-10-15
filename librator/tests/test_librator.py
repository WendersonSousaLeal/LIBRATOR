"""
test_librator.py
=====================================================================
Testes de unidade automatizados do Librator MVP.
Valida o pipeline de visão computacional, o modelo e as rotas Flask.
"""

import os
import sys
import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from hand_utils import normalize_landmarks, feature_column_names
from app import app, model, label_encoder, apply_command, CameraManager


def test_normalize_landmarks_translation_and_scale():
    points = np.zeros((21, 3), dtype=np.float32)
    points[0] = [10.0, 20.0, 5.0]  # Pulso
    points[9] = [10.0, 24.0, 5.0]  # Dedo médio (distância = 4.0)
    points[12] = [10.0, 28.0, 5.0] # Ponta do dedo médio

    norm = normalize_landmarks(points)
    assert norm.shape == (63,)
    reshaped = norm.reshape((21, 3))

    assert np.allclose(reshaped[0], [0.0, 0.0, 0.0])
    assert np.isclose(np.linalg.norm(reshaped[9]), 1.0)
    assert np.isclose(np.linalg.norm(reshaped[12]), 2.0)


def test_feature_column_names():
    cols_vel = feature_column_names(include_velocity=True)
    assert len(cols_vel) == 126
    assert cols_vel[0] == "x0"
    assert cols_vel[63] == "vx0"


def test_model_classes_and_prediction():
    assert len(label_encoder.classes_) == 26
    expected = [chr(c) for c in range(ord('A'), ord('Z') + 1)]
    assert list(label_encoder.classes_) == expected

    dummy = np.random.randn(126).astype(np.float32)
    probs = model.predict_proba([dummy])[0]
    assert len(probs) == 26
    assert np.isclose(np.sum(probs), 1.0)


def test_flask_index_and_state():
    client = app.test_client()
    res = client.get("/")
    assert res.status_code == 200
    assert b"Librator" in res.data
    assert b"MVP" in res.data

    res_st = client.get("/current_letter")
    assert res_st.status_code == 200
    data = res_st.json
    assert "letter" in data
    assert "confidence" in data
    assert "text" in data
    assert "history" in data


def test_command_conclude_and_history():
    apply_command("clear")
    apply_command("clear_history")

    # Adiciona letra
    import app as lib_app
    with lib_app.state_lock:
        lib_app.text_buffer = "BOM DIA"

    res = apply_command("conclude")
    assert res["text"] == ""
    assert len(res["history"]) == 1
    assert res["history"][0]["text"] == "BOM DIA"


def test_download_history():
    client = app.test_client()
    res = client.get("/download_history")
    assert res.status_code == 200
    assert res.mimetype == "text/plain"
    assert b"HIST" in res.data or b"LIBRATOR" in res.data


if __name__ == "__main__":
    test_normalize_landmarks_translation_and_scale()
    test_feature_column_names()
    test_model_classes_and_prediction()
    test_flask_index_and_state()
    test_command_conclude_and_history()
    test_download_history()
    print("Todos os testes unitários foram executados e passaram com 100% de sucesso!")
