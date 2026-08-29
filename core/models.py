from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, Integer, Boolean, DateTime
from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)  # Telegram ID
    full_name = Column(String(255), nullable=False)
    username = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # HEMIS ma'lumotlari (Shifrlangan)
    hemis_domain = Column(String(255), nullable=True)
    hemis_token = Column(Text, nullable=True)  # Shifrlangan holda
    hemis_student_name = Column(String(255), nullable=True)
    hemis_university = Column(String(255), nullable=True)
    hemis_group = Column(String(100), nullable=True)

    # Foydalanish statistikasi (Limits & Analytics)
    referats_count = Column(Integer, default=0)
    slides_count = Column(Integer, default=0)

    # Xabarnomalar
    notify_schedule = Column(Boolean, default=True)
    notify_deadline = Column(Boolean, default=True)

    def __repr__(self):
        return f"<User {self.id} ({self.full_name})>"
