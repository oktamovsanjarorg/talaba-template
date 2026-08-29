import os
import pytest
from services.user_service import user_service
from services.docx_generator import create_referat_docx
from services.pptx_generator import create_presentation_pptx
from services.mustaqil_ish_generator import create_mustaqil_ish_docx
from services.quiz_generator import create_quiz_docx
from core.database import engine, Base


@pytest.mark.asyncio
async def test_e2e_user_lifecycle_and_audit():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    test_user_id = 999888777
    user = await user_service.get_or_create(test_user_id, "E2E Test User", "e2e_user")
    assert user.id == test_user_id
    assert user.full_name == "E2E Test User"

    # HEMIS link
    ok = await user_service.link_hemis(test_user_id, "student.tuit.uz", "dummy_token_xyz", {"name": "Test Talaba", "university": "TATU", "group": "941-21"})
    assert ok is True

    creds = await user_service.get_hemis_credentials(test_user_id)
    assert creds is not None
    assert creds["token"] == "dummy_token_xyz"
    assert creds["domain"] == "student.tuit.uz"

    # Record generations
    await user_service.record_generation(test_user_id, "referat", "Cloud Computing", "success")
    await user_service.record_generation(test_user_id, "slide", "AI in Healthcare", "success")
    await user_service.record_generation(test_user_id, "mustaqil", "Economics 101", "success")
    await user_service.record_generation(test_user_id, "quiz", "Python Basics", "success")

    updated_user = await user_service.get_or_create(test_user_id, "E2E Test User")
    assert updated_user.referats_count >= 1
    assert updated_user.slides_count >= 1
    assert updated_user.mustaqil_count >= 1
    assert updated_user.quizzes_count >= 1


def test_e2e_academic_document_pipeline(tmp_path):
    # 1. Referat pipeline
    referat_data = {
        "title": "E2E Referat",
        "plan": ["Kirish", "1-bob", "Xulosa"],
        "introduction": "Kirish matni...",
        "chapters": [{"title": "1-bob", "content": "Bob matni..."}],
        "conclusion": "Xulosa...",
        "references": ["1. Adabiyot 1"]
    }
    referat_path = str(tmp_path / "e2e_referat.docx")
    res_ref = create_referat_docx(referat_data, referat_path, student_name="E2E Student")
    assert os.path.exists(res_ref)
    assert os.path.getsize(res_ref) > 2000

    # 2. Slayd pipeline
    slides_data = [
        {"slide_number": 1, "title": "Slayd 1", "bullets": ["B1", "B2"]}
    ]
    slide_path = str(tmp_path / "e2e_slide.pptx")
    res_slide = create_presentation_pptx(slides_data, "E2E Slide", slide_path, student_name="E2E Student")
    assert os.path.exists(res_slide)
    assert os.path.getsize(res_slide) > 5000

    # 3. Mustaqil ish pipeline
    mustaqil_data = {
        "title": "E2E Mustaqil",
        "plan": ["Maqsad", "Nazariya", "Amaliyot", "Xulosa"],
        "goal": "Maqsad...",
        "theoretical_part": "Nazariya...",
        "practical_part": "Amaliyot...",
        "conclusion": "Xulosa...",
        "references": ["1. Adabiyot..."]
    }
    mustaqil_path = str(tmp_path / "e2e_mustaqil.docx")
    res_must = create_mustaqil_ish_docx(mustaqil_data, mustaqil_path, student_name="E2E Student")
    assert os.path.exists(res_must)
    assert os.path.getsize(res_must) > 2000

    # 4. Quiz pipeline
    quiz_data = [
        {"question": "Q1?", "options": ["A", "B", "C", "D"], "correct_index": 0, "explanation": "Exp"}
    ]
    quiz_path = str(tmp_path / "e2e_quiz.docx")
    res_quiz = create_quiz_docx(quiz_data, "E2E Quiz", quiz_path)
    assert os.path.exists(res_quiz)
    assert os.path.getsize(res_quiz) > 2000
