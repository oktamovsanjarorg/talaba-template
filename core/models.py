from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)  # Telegram ID
    full_name = Column(String(255), nullable=False)
    username = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # HEMIS ma'lumotlari (Shifrlangan)
    hemis_domain = Column(String(255), nullable=True)
    hemis_token = Column(Text, nullable=True)
    hemis_student_name = Column(String(255), nullable=True)
    hemis_university = Column(String(255), nullable=True)
    hemis_group = Column(String(100), nullable=True)

    # Statistik hisoblagichlar
    referats_count = Column(Integer, default=0)
    slides_count = Column(Integer, default=0)
    mustaqil_count = Column(Integer, default=0)
    quizzes_count = Column(Integer, default=0)

    # Aloqa
    generations = relationship("GenerationHistory", back_populates="user", cascade="all, delete-orphan")


class GenerationHistory(Base):
    __tablename__ = "generation_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    doc_type = Column(String(50), nullable=False)  # referat, slide, mustaqil, quiz, summary
    topic = Column(String(500), nullable=False)
    status = Column(String(50), default="success") # success, failed
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="generations")
