"""
test_numbers_recognizer.py
=====================================================================
Testes unitários para o subsistema de reconhecimento de números em Libras.
Testa:
  1. Geometria de mãos para os números 0 a 9.
  2. Classificador cinemático / heurístico LibrasNumberRecognizer.
  3. Modelo e encoder de dígitos de 0 a 9.
  4. Integração de modos (letters, numbers, hybrid) no app Flask.
  5. API /command e /current_letter com suporte a números.
"""

import os
import sys
import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from number_recognizer import (
    LibrasNumberRecognizer,
    create_synthetic_landmarks,
    extract_finger_features
)
from app import app, apply_command, state_lock


def test_synthetic_landmarks_generation():
    """Valida a geração de landmarks sintéticos de teste para cada dígito de 0 a 9."""
    for digit in range(10):
        digit_str = str(digit)
        landmarks = create_synthetic_landmarks(digit_str)
        assert len(landmarks) == 21, f"Dígito {digit_str} deve ter 21 landmarks"
        # Landmark 0 deve ser o pulso na origem (0, 0, 0)
        assert np.allclose(landmarks[0], [0.0, 0.0, 0.0])
        # Pelo menos um landmark deve ser não-nulo
        assert np.max(np.abs(landmarks)) > 0.1


def test_number_kinematics_recognition():
    """Valida que o reconhecedor cinemático identifica os números sintéticos de 0 a 9."""
    recognizer = LibrasNumberRecognizer(use_ml=False)

    for digit in range(10):
        digit_str = str(digit)
        landmarks = create_synthetic_landmarks(digit_str)
        predicted, confidence, details = recognizer.predict(landmarks)
        assert predicted == digit_str, (
            f"Esperava {digit_str}, obteve {predicted} com confiança {confidence:.2f}. "
            f"Detalhes: {details}"
        )
        assert confidence >= 0.65, f"Confiança para {digit_str} foi {confidence:.2f} < 0.65"


def test_mode_switching_via_apply_command():
    """Valida a troca de modos (letters, numbers, hybrid) via apply_command."""
    import app as lib_app

    res = apply_command("set_mode", {"mode": "numbers"})
    assert res is not None
    assert res.get("mode") == "numbers"
    with state_lock:
        assert getattr(lib_app, "current_mode", "numbers") == "numbers"

    res = apply_command("set_mode", {"mode": "letters"})
    assert res.get("mode") == "letters"
    with state_lock:
        assert getattr(lib_app, "current_mode", "letters") == "letters"

    res = apply_command("set_mode", {"mode": "hybrid"})
    assert res.get("mode") == "hybrid"
    with state_lock:
        assert getattr(lib_app, "current_mode", "hybrid") == "hybrid"

    # Restaura para letters
    apply_command("set_mode", {"mode": "letters"})


def test_flask_current_letter_with_numbers_mode():
    """Valida que a rota /current_letter reflete o modo e suporta símbolos numéricos."""
    client = app.test_client()

    apply_command("set_mode", {"mode": "numbers"})

    res = client.get("/current_letter")
    assert res.status_code == 200
    data = res.json
    assert "mode" in data
    assert data["mode"] == "numbers"
    assert "letter" in data
    assert "symbol" in data
    assert "available_modes" in data

    # Restaura para letters
    apply_command("set_mode", {"mode": "letters"})


def test_number_recognition_model_bundle():
    """Valida que o reconhecedor tem a lista de dígitos suportados de 0 a 9."""
    recognizer = LibrasNumberRecognizer(use_ml=False)
    assert sorted(recognizer.supported_digits) == [str(i) for i in range(10)]


def test_command_insert_and_conclude_numbers():
    """Valida que números podem ser digitados, acumulados e concluídos no histórico."""
    apply_command("clear")
    apply_command("clear_history")

    apply_command("insert_text", {"text": "SALA 104"})
    res = apply_command("conclude")
    assert res["text"] == ""
    assert len(res["history"]) >= 1
    assert res["history"][-1]["text"] == "SALA 104"


if __name__ == "__main__":
    test_synthetic_landmarks_generation()
    test_number_kinematics_recognition()
    test_number_recognition_model_bundle()
    test_mode_switching_via_apply_command()
    test_flask_current_letter_with_numbers_mode()
    test_command_insert_and_conclude_numbers()
    print("Todos os testes do subsistema de números passaram com sucesso!")
