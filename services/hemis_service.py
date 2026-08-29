import httpx
from typing import Optional, Dict, Any


class HemisService:
    def __init__(self):
        self.timeout = 15.0

    def _get_base_url(self, university_domain: str) -> str:
        # Masalan: "tuit" -> "https://student.tuit.uz" yoki to'liq domen berilsa
        domain = university_domain.strip().lower()
        if not domain.startswith("http"):
            if not domain.startswith("student."):
                domain = f"student.{domain}"
            if not domain.endswith(".uz"):
                domain = f"{domain}.uz"
            return f"https://{domain}"
        return domain

    async def login(self, university_domain: str, login_id: str, password: str) -> Optional[str]:
        """
        HEMIS tizimiga kirish va Bearer tokenni qaytarish.
        """
        base_url = self._get_base_url(university_domain)
        url = f"{base_url}/rest/v1/auth/login"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json={"login": login_id, "password": password})
                if response.status_code == 200:
                    data = response.json()
                    # HEMIS odatda token yoki data.token qaytaradi
                    return data.get("data", {}).get("token") or data.get("token")
                return None
            except Exception:
                return None

    async def get_account_info(self, university_domain: str, token: str) -> Optional[Dict[str, Any]]:
        """
        Talaba shaxsiy profili (F.I.SH, ID, guruh, fakultet).
        """
        base_url = self._get_base_url(university_domain)
        url = f"{base_url}/rest/v1/account/me"
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    return response.json().get("data", {})
                return None
            except Exception:
                return None

    async def get_schedule(self, university_domain: str, token: str) -> Optional[list]:
        """
        Dars jadvalini olish.
        """
        base_url = self._get_base_url(university_domain)
        url = f"{base_url}/rest/v1/education/schedule"
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    return response.json().get("data", [])
                return None
            except Exception:
                return None

    async def get_tasks(self, university_domain: str, token: str) -> Optional[list]:
        """
        Topshiriqlar va deadlinelarni olish.
        """
        base_url = self._get_base_url(university_domain)
        url = f"{base_url}/rest/v1/education/tasks"
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    return response.json().get("data", [])
                return None
            except Exception:
                return None


hemis_service = HemisService()
