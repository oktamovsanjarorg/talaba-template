# 🎓 Talaba AI & HEMIS Assistant (Production-Ready Architecture)

Ushbu loyiha O'zbekiston OTM talabalari uchun sun'iy intellekt (Alibaba Cloud Qwen) va HEMIS axborot tizimi bilan integratsiyalashgan ekotizimdir. 100k+ foydalanuvchi yuklamasiga moslashgan DevOps standartlari asosida yaratilgan.

---

## 🏗️ Arxitektura va Modullar

```
talaba/
├── bot/
│   ├── handlers/
│   │   ├── start.py        # /start buyrug'i va menyu
│   │   └── academic.py     # Referat va Slayd (PPTX/DOCX) yaratish oqimi (FSM)
│   └── main.py             # Aiogram 3 bot kirish nuqtasi
├── core/
│   └── config.py           # Pydantic orqali .env konfiguratsiyalarini yuklash
├── services/
│   ├── ai_service.py       # Alibaba Cloud Qwen AI mijozi
│   ├── docx_generator.py   # OTM standartlaridagi akademik Word generatori
│   ├── pptx_generator.py   # 16:9 zamonaviy PowerPoint taqdimot generatori
│   └── hemis_service.py    # HEMIS REST API (Dars jadvali, topshiriqlar)
├── docker/
│   └── Dockerfile          # Xavfsiz non-root Python 3.12 konteyner
├── docker-compose.yml      # Bot, PostgreSQL va Redis orkestratsiyasi
├── requirements.txt        # Barcha zamonaviy asinxron kutubxonalar
└── .env                    # Maxfiy kalitlar va sozlamalar
```

---

## 🚀 Ishga tushirish (2 qadam)

### 1. Telegram Bot Tokenini qo'yish
Telegramda [@BotFather](https://t.me/BotFather) orqali yangi bot oching va olingan tokenni `.env` faylidagi `BOT_TOKEN` qatoriga joylang:
```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 2. Docker orqali ishga tushirish
Loyihani bitta buyruq bilan to'liq orqa fonda ko'taring:
```bash
docker compose up -d --build
```

Konteynerlar holatini tekshirish:
```bash
docker compose ps
docker compose logs -f bot
```
