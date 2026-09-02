import pytest


@pytest.fixture
def sample_referat_data():
    return {
        "title": "Test Referat Mavzusi",
        "subject": "Informatika",
        "plan": ["Kirish", "I BOB. Nazariy asoslar", "II BOB. Amaliy tahlil", "Xulosa", "Adabiyotlar"],
        "introduction": "Bu kirish qismi matni bo'lib, test maqsadida yozilgan.",
        "chapters": [
            {
                "title": "I BOB. Nazariy asoslar",
                "sections": [
                    {"subtitle": "1.1. Asosiy tushunchalar", "text": "Nazariy tushunchalar matni."},
                    {"subtitle": "1.2. Rivojlanish tarixi", "text": "Tarixiy ma'lumotlar."}
                ]
            },
            {
                "title": "II BOB. Amaliy tahlil",
                "sections": [
                    {"subtitle": "2.1. Hozirgi holat", "text": "Amaliy tahlil matni."},
                    {"subtitle": "2.2. Takliflar", "text": "Takliflar matni."}
                ]
            }
        ],
        "conclusion": "Xulosa va tavsiyalar matni.",
        "references": ["1. Darslik 2024.", "2. Ilmiy maqola."]
    }


@pytest.fixture
def sample_quiz_data():
    return [
        {
            "question": "Python dasturlash tilida 'list' nima?",
            "options": ["Tartibli to'plam", "Lug'at", "To'plam", "String"],
            "correct_index": 0,
            "explanation": "List — bu Python'da tartibli, o'zgartiriladigan to'plam turi."
        },
        {
            "question": "SQL'da SELECT buyrug'i nima uchun ishlatiladi?",
            "options": ["Ma'lumot o'qish", "Ma'lumot o'chirish", "Jadval yaratish", "Index qo'shish"],
            "correct_index": 0,
            "explanation": "SELECT — SQL'da ma'lumotlar bazasidan ma'lumot olish uchun asosiy buyruq."
        }
    ]


@pytest.fixture
def sample_slides_data():
    return [
        {
            "slide_number": 1,
            "title": "Kirish",
            "subtitle": "Mavzuning dolzarbligi",
            "cards": [
                {"card_title": "Nazariy asos", "card_text": "Fundamental tushunchalar."},
                {"card_title": "Amaliy qo'llanma", "card_text": "Texnologiyalar tahlili."}
            ]
        },
        {
            "slide_number": 2,
            "title": "Xulosa",
            "subtitle": "Yakuniy natijalar",
            "cards": [
                {"card_title": "Natija", "card_text": "Erishilgan yutuqlar."}
            ]
        }
    ]
