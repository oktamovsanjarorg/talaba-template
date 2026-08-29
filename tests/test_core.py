import os
import pytest
from core.security import encrypt_data, decrypt_data
from services.docx_generator import create_referat_docx
from services.pptx_generator import create_presentation_pptx
from services.mustaqil_ish_generator import create_mustaqil_ish_docx
from services.quiz_generator import create_quiz_docx
from services.hemis.universities import search_university


def test_encryption_roundtrip():
    secret = "my_secret_hemis_token_12345"
    encrypted = encrypt_data(secret)
    assert encrypted != secret
    decrypted = decrypt_data(encrypted)
    assert decrypted == secret


def test_university_search():
    results = search_university("tuit")
    assert len(results) > 0
    assert "tuit.uz" in results[0]["domain"]

    results_samdu = search_university("Samarqand")
    assert len(results_samdu) > 0
    assert "samdu.uz" in results_samdu[0]["domain"]


def test_docx_referat_creation(tmp_path):
    data = {
        "title": "Test Referat",
        "plan": ["Kirish", "1-bob", "Xulosa"],
        "introduction": "Bu kirish qismi matni...",
        "chapters": [{"title": "1-bob", "content": "1-bob matni..."}],
        "conclusion": "Xulosa matni...",
        "references": ["1. Manba 1"]
    }
    out_file = str(tmp_path / "test_referat.docx")
    res = create_referat_docx(data, out_file)
    assert os.path.exists(res)
    assert os.path.getsize(res) > 0


def test_pptx_creation(tmp_path):
    slides = [
        {"slide_number": 1, "title": "Slayd 1", "bullets": ["Nuqta 1", "Nuqta 2"]}
    ]
    out_file = str(tmp_path / "test_slide.pptx")
    res = create_presentation_pptx(slides, "Mavzu", out_file)
    assert os.path.exists(res)
    assert os.path.getsize(res) > 0


def test_mustaqil_ish_creation(tmp_path):
    data = {
        "title": "Test Mustaqil Ish",
        "plan": ["Maqsad", "Nazariya", "Amaliyot", "Xulosa"],
        "goal": "Maqsad...",
        "theoretical_part": "Nazariya...",
        "practical_part": "Amaliyot...",
        "conclusion": "Xulosa...",
        "references": ["1. Adabiyot..."]
    }
    out_file = str(tmp_path / "test_mustaqil.docx")
    res = create_mustaqil_ish_docx(data, out_file)
    assert os.path.exists(res)
    assert os.path.getsize(res) > 0


def test_quiz_creation(tmp_path):
    quiz = [
        {
            "question": "Savol 1?",
            "options": ["A", "B", "C", "D"],
            "correct_index": 0,
            "explanation": "Izoh..."
        }
    ]
    out_file = str(tmp_path / "test_quiz.docx")
    res = create_quiz_docx(quiz, "Mavzu", out_file)
    assert os.path.exists(res)
    assert os.path.getsize(res) > 0
