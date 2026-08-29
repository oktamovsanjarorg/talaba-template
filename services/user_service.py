from sqlalchemy import select
from core.database import AsyncSessionLocal
from core.models import User
from core.security import encrypt_data, decrypt_data


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
                    username=username
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
            return user

    async def link_hemis(self, telegram_id: int, domain: str, token: str, info: dict = None) -> bool:
        async with AsyncSessionLocal() as session:
            stmt = select(User).where(User.id == telegram_id)
            res = await session.execute(stmt)
            user = res.scalar_one_or_none()

            if user:
                user.hemis_domain = domain
                user.hemis_token = encrypt_data(token)
                if info:
                    user.hemis_student_name = info.get("name") or info.get("full_name")
                    user.hemis_university = info.get("university", {}).get("name") if isinstance(info.get("university"), dict) else str(info.get("university", ""))
                    user.hemis_group = info.get("group", {}).get("name") if isinstance(info.get("group"), dict) else str(info.get("group", ""))
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
                    "group": user.hemis_group
                }
            return None


user_service = UserService()
