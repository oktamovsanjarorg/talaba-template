# 🎓 Talaba AI & HEMIS Assistant

Talabalar uchun sun'iy intellekt (Alibaba Cloud Qwen AI) va HEMIS axborot tizimi bilan integratsiyalashgan akademik yordamchi Telegram bot.

---

## 🌟 Asosiy Imkoniyatlar

### 📝 Akademik Referat Generator (DOCX)
* O'zbekiston OTMlarining rasmiy talablariga mos format
* Times New Roman 14pt, 1.5 qator oralig'i
* Titul varag'i, Mundarija, 3 bob, Xulosa va Adabiyotlar

### 📊 Taqdimot Generator (PPTX)
* 16:9 Widescreen PowerPoint taqdimotlar
* 5, 8, yoki 10 slayd tanlash imkoniyati
* Zamonaviy card-grid dizayn

### 📑 Mustaqil Ta'lim Ishi Generator (DOCX)
* Maqsad, Nazariy qism, Amaliy tahlil, Xulosa

### 🎯 Test va Nazorat Savollari (Quiz)
* 4 variantli testlar to'plami (DOCX)
* Javoblar kaliti va ilmiy izohlar
* Telegram Quiz (Poll) rejimi

### 💡 Aqlli Konspekt
* Katta matnlardan asosiy xulosalarni chiqarish

### 🎓 HEMIS Integratsiyasi
* 50+ O'zbekiston OTMlari bilan ishlash
* Dars jadvali va topshiriqlar/deadline
* Token shifrlash (Fernet/AES)

---

## 🏛 Arxitektura

```
talaba/
├── bot/
│   ├── handlers/
│   │   ├── start.py        # Asosiy menyu, Profil va Yordam
│   │   ├── academic.py     # Referat, Slayd, Mustaqil ish, Quiz, Konspekt
│   │   └── hemis.py        # OTM qidiruvi, Login, Dars jadvali, Topshiriqlar
│   ├── commands.py         # Telegram buyruqlar menyusi
│   └── main.py             # Aiogram 3 bot kirish nuqtasi
├── core/
│   ├── config.py           # Pydantic sozlamalari
│   ├── database.py         # SQLAlchemy + Asyncpg (PostgreSQL)
│   ├── models.py           # ORM modellari
│   ├── security.py         # Fernet shifrlash / deshifrlash
│   └── telemetry.py        # Prometheus metrikalari
├── services/
│   ├── ai_service.py       # Qwen AI mijoz (retry bilan)
│   ├── docx_generator.py   # Referat Word generatori
│   ├── pptx_generator.py   # PowerPoint generatori
│   ├── mustaqil_ish_generator.py
│   ├── quiz_generator.py   # Testlar generatori
│   ├── hemis_service.py    # HEMIS API mijoz
│   ├── user_service.py     # Foydalanuvchi CRUD
│   ├── storage_cleaner.py  # Vaqtinchalik fayllarni tozalash
│   └── hemis/
│       └── universities.py # O'zbekiston OTMlari bazasi
├── apps/
│   └── workers/
│       ├── celery_app.py   # Celery konfiguratsiyasi
│       └── tasks.py        # Fon vazifalari
├── tests/
│   ├── conftest.py         # Test fixture'lar
│   ├── test_core.py        # Unit testlar
│   ├── test_e2e.py         # E2E testlar
│   └── test_ai_service.py  # AI service testlar
├── docker/
│   └── Dockerfile
├── infra/
│   ├── k8s/                # Kubernetes manifest'lar
│   ├── monitoring/         # Prometheus konfiguratsiyasi
│   └── terraform/          # IaC konfiguratsiyasi
├── docker-compose.yml      # Bot, Worker, PostgreSQL, Redis
└── requirements.txt
```

---

## 🚀 Ishga tushirish

### 1. Environment sozlash
```bash
cp .env.example .env
# .env faylini to'ldiring: BOT_TOKEN, QWEN_API_KEY, ENCRYPTION_KEY
```

### 2. Docker bilan ishga tushirish
```bash
docker compose up -d --build
```

Bu quyidagilarni ko'taradi:
- **bot** — Telegram bot (Aiogram 3 + Redis FSM)
- **worker** — Celery fon ishlari
- **db** — PostgreSQL 16
- **redis** — Redis 7 (FSM + Celery broker)

### 3. Testlarni yurgizish
```bash
# Lokal
pytest tests/test_core.py tests/test_ai_service.py -v

# Docker ichida
docker compose exec bot pytest tests/test_core.py -v
```

### 4. Loglarni kuzatish
```bash
docker compose logs -f bot worker
```

---

## 📋 Texnologiyalar

| Texnologiya | Versiya | Maqsad |
|---|---|---|
| Python | 3.12 | Asosiy til |
| Aiogram | 3.14+ | Telegram Bot Framework |
| SQLAlchemy | 2.0+ | ORM (PostgreSQL) |
| Redis | 7 | FSM Storage + Celery Broker |
| Celery | 5.4+ | Background Tasks |
| Qwen AI | turbo | Matn generatsiyasi |
| python-docx | 1.1+ | Word hujjat generatsiyasi |
| python-pptx | 1.0+ | PowerPoint generatsiyasi |
| Prometheus | - | Monitoring metrikalari |
