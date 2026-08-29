import json
from openai import AsyncOpenAI
from core.config import settings


class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_BASE_URL
        )
        self.model = settings.QWEN_MODEL

    async def generate_referat_structure(self, topic: str, subject: str = "") -> dict:
        """
        Referat uchun O'zbekiston OTMlari standartidagi to'liq tuzilma (Kirish, 3 ta asosiy bob, Xulosa, Adabiyotlar) tayyorlaydi.
        """
        system_prompt = (
            "Sen O'zbekiston oliy ta'lim muassasalari standartlari bo'yicha akademik referat va ilmiy ishlar yozuvchi professiorsan. "
            "Javobingni FAQAT toza JSON formatida qaytar. Hech qanday markdown belgisi (masalan ```json) qo'shma."
        )
        user_prompt = f"""Mavzu: "{topic}". Fan: "{subject}".
Quyidagi JSON formatda referat matnini to'liq o'zbek tilida tayyorlab ber:
{{
  "title": "{topic}",
  "subject": "{subject}",
  "plan": ["Kirish", "1-bob ...", "2-bob ...", "3-bob ...", "Xulosa", "Foydalanilgan adabiyotlar"],
  "introduction": "Mavzuning dolzarbligi, maqsadi va vazifalari (kamida 200 so'z)...",
  "chapters": [
    {{"title": "1-bob nomi", "content": "1-bobning to'liq akademik matni (kamida 300 so'z)..."}},
    {{"title": "2-bob nomi", "content": "2-bobning to'liq akademik matni (kamida 300 so'z)..."}},
    {{"title": "3-bob nomi", "content": "3-bobning to'liq akademik matni (kamida 300 so'z)..."}}
  ],
  "conclusion": "Referat bo'yicha umumiy ilmiy xulosalar...",
  "references": [
    "1. Adabiyot nomi...",
    "2. Adabiyot nomi..."
  ]
}}"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )

        content = response.choices[0].message.content.strip()
        # Clean potential markdown wrapping
        if content.startswith("```"):
            content = content.split("```", 2)[1]
            if content.startswith("json"):
                content = content[4:]
        return json.loads(content.strip())

    async def generate_slides_data(self, topic: str, slide_count: int = 6) -> list:
        """
        Taqdimot (Prezentatsiya) slaydlari uchun sarlavha va asosiy tezislarni generatsiya qiladi.
        """
        system_prompt = (
            "Sen professional prezentatsiya mutaxassisisan. Javobni FAQAT toza JSON array formatida qaytar."
        )
        user_prompt = f"""Mavzu: "{topic}". Slaydlar soni: {slide_count}.
Quyidagi formatdagi JSON massiv qaytar:
[
  {{
    "slide_number": 1,
    "title": "Slayd sarlavhasi",
    "bullets": ["1-asosiy fikr", "2-asosiy fikr", "3-asosiy fikr"]
  }}
]"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )

        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```", 2)[1]
            if content.startswith("json"):
                content = content[4:]
        return json.loads(content.strip())


ai_service = AIService()
