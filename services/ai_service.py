import json
import logging
from openai import AsyncOpenAI
from core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_BASE_URL
        )
        self.model = settings.QWEN_MODEL

    def _clean_json_response(self, content: str) -> str:
        content = content.strip()
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()
        return content

    async def generate_referat_structure(self, topic: str, subject: str = "") -> dict:
        """
        Referat uchun O'zbekiston OTMlari standartidagi to'liq akademik matn tayyorlaydi.
        """
        system_prompt = (
            "Sen O'zbekiston oliy ta'lim tizimi bo'yicha akademik referat va ilmiy ishlar yozuvchi professiorsan. "
            "Referat boy, ilmiy va tushunarli tilda bo'lishi shart. "
            "Javobingni FAQAT toza JSON formatida qaytar."
        )
        user_prompt = f"""Mavzu: "{topic}". Fan: "{subject}".
Quyidagi JSON formatda to'liq referat matnini tayyorlab ber:
{{
  "title": "{topic}",
  "subject": "{subject}",
  "plan": [
    "Kirish",
    "1-bob. Mavzuning nazariy asoslari va tushunchasi",
    "2-bob. Amaliy tahlil va hozirgi kundagi holati",
    "3-bob. Rivojlantirish istiqbollari va muammolar yechimi",
    "Xulosa",
    "Foydalanilgan adabiyotlar ro'yxati"
  ],
  "introduction": "Mavzuning dolzarbligi, maqsadi, vazifalari va predmeti haqida to'liq ilmiy kirish qismi (kamida 250 so'z)...",
  "chapters": [
    {{"title": "1-bob. Mavzuning nazariy asoslari va tushunchasi", "content": "1-bobning chuqur tahliliy ilmiy matni (kamida 350 so'z)..."}},
    {{"title": "2-bob. Amaliy tahlil va hozirgi kundagi holati", "content": "2-bobning amaliy, statistik va taqqoslama ma'lumotlarga boy matni (kamida 350 so'z)..."}},
    {{"title": "3-bob. Rivojlantirish istiqbollari va muammolar yechimi", "content": "3-bobning takliflar va yechimlarga bag'ishlangan matni (kamida 350 so'z)..."}}
  ],
  "conclusion": "Referatdan kelib chiqqan asosiy 4-5 ta ilmiy xulosa va amaliy tavsiyalar...",
  "references": [
    "1. O'zbekiston Respublikasi Prezidentining tegishli Farmon va Qarorlari.",
    "2. OTM darsliklari va ilmiy qo'llanmalar (2020-2025 yillar).",
    "3. Xalqaro ilmiy jurnallar va rasmiy axborot manbalari.",
    "4. Internet manbalari va statistik to'plamlar."
  ]
}}"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.65
        )
        raw = response.choices[0].message.content
        cleaned = self._clean_json_response(raw)
        return json.loads(cleaned)

    async def generate_mustaqil_ish_structure(self, topic: str, subject: str = "") -> dict:
        """
        Mustaqil ish (Mustaqil ta'lim topshirig'i) formati.
        """
        system_prompt = (
            "Sen talabalar uchun mustaqil ish topshiriqlarini OTM talablariga mos shakllantiruvchi mutaxassissan. "
            "Javobni FAQAT toza JSON formatida qaytar."
        )
        user_prompt = f"""Mavzu: "{topic}". Fan: "{subject}".
Quyidagi JSON formatda mustaqil ish tayyorlab ber:
{{
  "title": "{topic}",
  "subject": "{subject}",
  "plan": ["Topshiriqning maqsadi", "Nazariy qism", "Amaliy yondashuv / Tahlil", "Xulosa va takliflar"],
  "goal": "Mustaqil ishning maqsadi va qo'yilgan vazifalari...",
  "theoretical_part": "Nazariy tushunchalar va asosiy qoidalar...",
  "practical_part": "Amaliy tahlil, misollar va yechimlar...",
  "conclusion": "Umumiy xulosa va natijalar...",
  "references": ["1. Adabiyot...", "2. Manba..."]
}}"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.65
        )
        cleaned = self._clean_json_response(response.choices[0].message.content)
        return json.loads(cleaned)

    async def generate_slides_data(self, topic: str, slide_count: int = 6) -> list:
        """
        PowerPoint slaydlari uchun sarlavha va asosiy punktlar.
        """
        system_prompt = (
            "Sen taqdimotlar va slaydlar dizayneri hamda ssenariynavisisan. "
            "Har bir slayd uchun qisqa, lo'nda va ta'sirchan 3-4 ta tezis (bullet point) tayyorla. "
            "Javobni FAQAT toza JSON massiv qaytar."
        )
        user_prompt = f"""Mavzu: "{topic}". Slaydlar soni: {slide_count}.
Format:
[
  {{
    "slide_number": 1,
    "title": "Slayd nomi",
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
        cleaned = self._clean_json_response(response.choices[0].message.content)
        return json.loads(cleaned)

    async def generate_quiz_data(self, topic: str, count: int = 5) -> list:
        """
        Mavzu bo'yicha interaktiv 4 variantli testlar (Quiz).
        """
        system_prompt = (
            "Sen OTM o'qituvchisisan. Berilgan mavzu bo'yicha bilimlarni tekshirish uchun 4 ta variantli (A, B, C, D) "
            "sifatli test savollari tuz. Javobni FAQAT toza JSON massiv formatida qaytar."
        )
        user_prompt = f"""Mavzu: "{topic}". Savollar soni: {count}.
Format:
[
  {{
    "question": "Savol matni?",
    "options": ["A variant", "B variant", "C variant", "D variant"],
    "correct_index": 0,
    "explanation": "Nima uchun bu javob to'g'riligi haqida qisqa izoh."
  }}
]"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5
        )
        cleaned = self._clean_json_response(response.choices[0].message.content)
        return json.loads(cleaned)

    async def summarize_text(self, text: str) -> str:
        """
        Matnni tahlil qilib, undan asosiy konspekt va xulosalarni chiqarish.
        """
        system_prompt = (
            "Sen talabalar uchun konspekt tayyorlovchi aqlli yordamchisan. "
            "Berilgan matnning eng muhim qoidalarini, ta'riflarini va xulosalarini punktlar ko'rinishida konspekt qilib ber."
        )
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Matn:\n{text[:4000]}"}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()


ai_service = AIService()
