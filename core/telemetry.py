from prometheus_client import Counter, Histogram, Gauge, start_http_server
import logging

logger = logging.getLogger(__name__)

# Metrikalar
TELEGRAM_MESSAGES = Counter(
    "talaba_telegram_messages_total",
    "Jami kelib tushgan Telegram xabarlari soni",
    ["command"]
)

REFERATS_GENERATED = Counter(
    "talaba_referats_generated_total",
    "Generatsiya qilingan referatlar soni",
    ["status"]
)

SLIDES_GENERATED = Counter(
    "talaba_slides_generated_total",
    "Generatsiya qilingan slaydlar soni",
    ["status"]
)

AI_LATENCY = Histogram(
    "talaba_ai_request_latency_seconds",
    "AI modeliga so'rovning bajarilish vaqti (soniyalarda)",
    buckets=[1.0, 2.5, 5.0, 10.0, 15.0, 30.0]
)

ACTIVE_USERS = Gauge(
    "talaba_active_users_current",
    "Faol foydalanuvchilar soni"
)


def start_metrics_server(port: int = 8000):
    try:
        start_http_server(port)
        logger.info(f"📊 Prometheus metrikalari porti ishga tushdi: :{port}")
    except Exception as e:
        logger.warning(f"Metrika serverini ko'tarishda xatolik: {e}")
