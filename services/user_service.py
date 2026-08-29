from datetime import datetime, timezone
from sqlalchemy import select
from core.database import AsyncSessionLocal
from core.models import User, GenerationHistory
from core.security import encrypt_data, decrypt_data


def get_now():
    return datetime.now(timezone.utc)


class UserService:
    async def get_or_create(self, telegram_id: int, full_name: str, username: str = None) -> User:
        async with AsyncSessionLocal() as session:
            stmt = select(User).where(User.id == telegram_id)
            res = await session.execute(stmt)
            user = res.scalar_one_or_none()

            if not user:
                user = User(
                    id=telegram_id,
                    full_name=full_name,
                    username=username,
                    created_at=get_now(),
                    last_active=get_now()
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
            else:
                user.last_active = get_now()
                if full_name:
                    user.full_name = full_name
                if username:
                    user.username = username
                await session.commit()
            return user

    async def link_hemis(self, telegram_id: int, domain: str, token: str, info: dict = None) -> bool:
        async with AsyncSessionLocal() as session:
            stmt = select(User).where(User.id == telegram_id)
            res = await session.execute(stmt)
            user = res.scalar_one_or_none()

            if user:
                user.hemis_domain = domain
                user.hemis_token = encrypt_data(token) if token else None
                if info:
                    user.hemis_student_name = info.get("name") or info.get("full_name")
                    user.hemis_university = info.get("university", {}).get("name") if isinstance(info.get("university"), dict) else str(info.get("university", ""))
                    user.hemis_group = info.get("group", {}).get("name") if isinstance(info.get("group"), dict) else str(info.get("group", ""))
                elif not token:
                    user.hemis_student_name = None
                    user.hemis_university = None
                    user.hemis_group = None
                await session.commit()
                return True
            return False

    async def get_hemis_credentials(self, telegram_id: int):
        async with AsyncSessionLocal() as session:
            stmt = select(User).where(User.id == telegram_id)
            res = await session.execute(stmt)
            user = res.scalar_one_or_none()

            if user and user.hemis_token and user.hemis_domain:
                return {
                    "domain": user.hemis_domain,
                    "token": decrypt_data(user.hemis_token),
                    "name": user.hemis_student_name,
                    "university": user.hemis_university,
                    "group": user.hemis_group
                }
            return None

    async def record_generation(self, telegram_id: int, doc_type: str, topic: str, status: str = "success"):
        async with AsyncSessionLocal() as session:
            stmt = select(User).where(User.id == telegram_id)
            res = await session.execute(stmt)
            user = res.scalar_one_or_none()

            if user:
                if status == "success":
                    if doc_type == "referat":
                        user.referats_count += 1
                    elif doc_type == "slide":
                        user.slides_count += 1
                    elif doc_type == "mustaqil":
                        user.mustaqil_count += 1
                    elif doc_type == "quiz":
                        user.quizzes_count += 1

                history = GenerationHistory(
                    user_id=telegram_id,
                    doc_type=doc_type,
                    topic=topic[:490],
                    status=status,
                    created_at=get_now()
                )
                session.add(history)
                await session.commit()


user_service = UserService()
