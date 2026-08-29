import os
import pytest
from core.security import encrypt_data, decrypt_data
from services.docx_generator import create_referat_docx
from services.pptx_generator import create_presentation_pptx
from services.mustaqil_ish_generator import create_mustaqil_ish_docx
from services.quiz_generator import create_quiz_docx
from services.hemis.universities import search_universities, get_paginated_universities
from services.ai_service import ai_service


def test_encryption_roundtrip():
    secret = "my_secret_hemis_token_12345"
    encrypted = encrypt_data(secret)
    assert encrypted != secret
    decrypted = decrypt_data(encrypted)
    assert decrypted == secret


def test_university_search_and_pagination():
    results = search_universities("tuit")
    assert len(results) > 0
    assert "tuit.uz" in results[0]["domain"]

    items, page, total_pages = get_paginated_universities(page=1, page_size=5)
    assert len(items) == 5
    assert page == 1
    assert total_pages > 1


def test_docx_referat_creation(tmp_path):
    data = {
        "title": "Sun'iy Intellekt va Kiberxavfsizlik",
        "plan": ["Kirish", "1-bob. Asosiy tushunchalar", "2-bob. Tahlil", "Xulosa", "Adabiyotlar"],
        "introduction": "Bu kirish qismi matni bo'lib, dolzarblikni ochib beradi...",
        "chapters": [
            {"title": "1-bob. Asosiy tushunchalar", "content": "1-bob matni..."},
            {"title": "2-bob. Tahlil", "content": "2-bob matni..."}
        ],
        "conclusion": "Xulosa va ilmiy tavsiyalar matni...",
        "references": ["1. O'zbekiston Respublikasi Qonuni", "2. Darslik 2024"]
    }
    out_file = str(tmp_path / "test_referat.docx")
    res = create_referat_docx(data, out_file, student_name="Sanjar O'ktamov")
    assert os.path.exists(res)
    assert os.path.getsize(res) > 2000 # To'liq hujjat hajmi


def test_pptx_creation(tmp_path):
    slides = [
        {"slide_number": 1, "title": "DevOps Arxitekturasi", "bullets": ["CI/CD Quvurlari", "Kubernetes klasteri", "Monitoring tizimi"]},
        {"slide_number": 2, "title": "Xavfsizlik choralari", "bullets": ["AES-256 shifrlash", "Konteyner izolyatsiyasi"]}
    ]
    out_file = str(tmp_path / "test_slide.pptx")
    res = create_presentation_pptx(slides, "DevOps Asoslari", out_file, student_name="Sanjar O'ktamov")
    assert os.path.exists(res)
    assert os.path.getsize(res) > 5000


def test_mustaqil_ish_creation(tmp_path):
    data = {
        "title": "Iqtisodiy Tahlil",
        "plan": ["Topshiriq maqsadi", "Nazariy qism", "Amaliyot", "Xulosa"],
        "goal": "Maqsad...",
        "theoretical_part": "Nazariya...",
        "practical_part": "Amaliy tahlil...",
        "conclusion": "Xulosa...",
        "references": ["1. Manba..."]
    }
    out_file = str(tmp_path / "test_mustaqil.docx")
    res = create_mustaqil_ish_docx(data, out_file, student_name="Sanjar O'ktamov")
    assert os.path.exists(res)
    assert os.path.getsize(res) > 2000


def test_quiz_creation(tmp_path):
    quiz = [
        {
            "question": "Python'da asinxron dasturlash qaysi kutubxona orqali amalga oshiriladi?",
            "options": ["asyncio", "math", "os", "sys"],
            "correct_index": 0,
            "explanation": "asyncio Python'ning standart asinxronlik kutubxonasidir."
        }
    ]
    out_file = str(tmp_path / "test_quiz.docx")
    res = create_quiz_docx(quiz, "Python Asoslari", out_file)
    assert os.path.exists(res)
    assert os.path.getsize(res) > 2000


def test_ai_service_clean_json():
    raw = "```json\n{\"test\": 123}\n```"
    cleaned = ai_service._clean_json_response(raw)
    assert cleaned == "{\"test\": 123}"
