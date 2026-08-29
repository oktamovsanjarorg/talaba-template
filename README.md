# 🎓 Talaba AI & HEMIS Assistant (Production Monolith MVP)

Talabalar uchun sun'iy intellekt (Alibaba Cloud Qwen AI) va HEMIS axborot tizimi bilan to'liq integratsiyalashgan, zamonaviy akademik yordamchi ekotizim.

---

## 🌟 Asosiy Imkoniyatlar (Features)

### 1. 📝 Akademik Referat Generator (DOCX)
* O'zbekiston OTMlarining rasmiy talablariga 100% mos format:
  * **Shrift:** Times New Roman 14pt, 1.5 qator oralig'i (line spacing);
  * **Hoshiyalar (Margins):** Chap 3sm, O'ng 1.5sm, Yuqori/Past 2sm;
  * **Struktura:** Rasmiy Titul varag'i (Vazirlik, OTM, Kafedra, Talaba, Toshkent 2026), Reja/Mundarija, Kirish, 3 ta asosiy bob, Xulosa va Foydalanilgan adabiyotlar ro'yxati.

### 2. 📊 Taqdimot & Slayd Generator (PPTX)
* Zamonaviy 16:9 Widescreen PowerPoint taqdimotlari;
* 5 ta, 8 ta yoki 10 ta slayd tanlash imkoniyati;
* Asosiy sarlavhalar va qisqa, ta'sirchan tezislar (bullet points).

### 3. 📑 Mustaqil Ta'lim Ishi Generator (DOCX)
* OTM mustaqil ta'lim talablari bo'yicha:
  * Topshiriqning maqsadi va vazifalari;
  * Nazariy qism;
  * Amaliy tahlil va yondashuv;
  * Xulosa va adabiyotlar.

### 4. 🎯 Testlar va Nazorat Savollari (Quiz)
* Mavzu bo'yicha 4 variantli (A, B, C, D) testlar to'plami;
* Chop etishga tayyor Word (.docx) varianti (Alohida sahifada **Javoblar kaliti va ilmiy izohlari** bilan);
* Telegram ichida to'g'ridan-to'g'ri yechish uchun **Interaktiv Telegram Quiz (Poll)** rejimi.

### 5. 💡 Aqlli Konspekt & Xulosachi
* Katta leksiyalar, maqolalar yoki darslik matnlarini tahlil qilib, eng muhim qoidalarni punktlar ko'rinishida chiqarib beradi.

### 6. 🎓 HEMIS To'liq Integratsiyasi
* O'zbekistondagi 18+ asosiy OTMlar (TATU, O'zMU, SamDU, TDIU, TDTU va boshqalar) ro'yxatdan tanlash yoki qidirish;
* Haftalik va kunlik **Dars jadvali**;
* **Topshiriqlar va Yakunlanish Muddatlari (Deadline)**;
* **Xavfsizlik:** Talaba tokenlari bazada **AES-256** kriptografik algoritmi bilan shifrlanadi.

---

## 🏛 Arxitektura

```
talaba/
├── bot/
│   ├── handlers/
│   │   ├── start.py        # Asosiy menyu, Profil va Yordam
│   │   ├── academic.py     # Referat, Slayd, Mustaqil ish, Quiz, Konspekt
│   │   └── hemis.py        # OTM qidiruvi, Login, Dars jadvali, Topshiriqlar
│   └── main.py             # Aiogram 3 bot kirish nuqtasi
├── core/
│   ├── config.py           # Pydantic sozlamalari
│   ├── database.py         # SQLAlchemy + Asyncpg (PostgreSQL)
│   ├── models.py           # ORM Foydalanuvchi jadvallari
│   └── security.py         # AES-256 shifrlash / de-shifrlash
├── services/
│   ├── ai_service.py       # Alibaba Cloud Qwen AI mijoz
│   ├── docx_generator.py   # Referat Word generatori
│   ├── pptx_generator.py   # PowerPoint taqdimot generatori
│   ├── mustaqil_ish_generator.py # Mustaqil ish Word generatori
│   ├── quiz_generator.py   # Testlar va javoblar kaliti generatori
│   └── hemis/
│       └── universities.py # O'zbekiston OTMlari ma'lumotlar bazasi
├── tests/
│   └── test_core.py        # Avtomatlashtirilgan Pytest to'plami
├── docker/
│   └── Dockerfile          # Non-root xavfsiz konteyner
├── docker-compose.yml      # Bot, PostgreSQL 16 va Redis 7
└── requirements.txt
```

---

## 🚀 Ishga tushirish va Testlash

```bash
# 1. Konteynerlarni ko'tarish
docker compose up -d --build

# 2. Avtomatlashtirilgan testlarni yurgizish
docker compose exec bot pytest tests/ -v

# 3. Loglarni kuzatish
docker compose logs -f bot
```
