import json
import re
import logging
from openai import AsyncOpenAI
from core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_BASE_URL,
            timeout=30.0
        )
        self.model = settings.QWEN_MODEL

    def _extract_and_parse_json(self, content: str, default_data: dict) -> dict:
        content = content.strip()
        # Markdown bloklarini tozalash
        if content.startswith("```"):
            lines = content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()

        try:
            return json.loads(content)
        except Exception:
            # Regex orqali JSON qismini qidirish
            match = re.search(r'(\{.*\}|\[.*\])', content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except Exception:
                    pass
            logger.warning(f"JSON parse qilib bo'lmadi, standart strukturadan foydalaniladi.")
            return default_data

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
  "introduction": "Mavzuning dolzarbligi, maqsadi, vazifalari va predmeti haqida to'liq ilmiy kirish qismi (kamida 200 so'z)...",
  "chapters": [
    {{"title": "1-bob. Mavzuning nazariy asoslari va tushunchasi", "content": "1-bobning chuqur tahliliy ilmiy matni (kamida 300 so'z)..."}},
    {{"title": "2-bob. Amaliy tahlil va hozirgi kundagi holati", "content": "2-bobning amaliy, statistik va taqqoslama ma'lumotlarga boy matni (kamida 300 so'z)..."}},
    {{"title": "3-bob. Rivojlantirish istiqbollari va muammolar yechimi", "content": "3-bobning takliflar va yechimlarga bag'ishlangan matni (kamida 300 so'z)..."}}
  ],
  "conclusion": "Referatdan kelib chiqqan asosiy 4-5 ta ilmiy xulosa va amaliy tavsiyalar...",
  "references": [
    "1. O'zbekiston Respublikasi Prezidentining tegishli Farmon va Qarorlari.",
    "2. OTM darsliklari va ilmiy qo'llanmalar (2020-2025 yillar).",
    "3. Xalqaro ilmiy jurnallar va rasmiy axborot manbalari.",
    "4. Internet manbalari va statistik to'plamlar."
  ]
}}"""

        default_data = {
            "title": topic,
            "subject": subject,
            "plan": ["Kirish", "1-bob. Nazariy asoslar", "2-bob. Amaliy tahlil", "Xulosa", "Adabiyotlar"],
            "introduction": f"{topic} mavzusi hozirgi kunda ta'lim va ilmiy taraqqiyotda muhim ahamiyat kasb etadi.",
            "chapters": [
                {"title": "1-bob. Nazariy asoslar", "content": f"{topic} mavzusining nazariy tushunchalari va rivojlanish bosqichlari."},
                {"title": "2-bob. Amaliy tahlil", "content": f"{topic} sohasidagi amaliy tajribalar va tahlillar."}
            ],
            "conclusion": f"{topic} mavzusi bo'yicha olib borilgan tahlillar sohani rivojlantirish muhimligini ko'rsatadi.",
            "references": ["1. O'zbekiston Respublikasi qonunchilik hujjatlari.", "2. Ilmiy darsliklar to'plami."]
        }

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.6
            )
            raw = response.choices[0].message.content
            return self._extract_and_parse_json(raw, default_data)
        except Exception as e:
            logger.error(f"Referat generatsiya xatosi: {e}")
            return default_data

    async def generate_mustaqil_ish_structure(self, topic: str, subject: str = "") -> dict:
        system_prompt = "Sen talabalar uchun mustaqil ish topshiriqlarini OTM talablariga mos shakllantiruvchi mutaxassissan. FAQAT toza JSON formatida javob ber."
        user_prompt = f"""Mavzu: "{topic}". Fan: "{subject}".
JSON format:
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
        default_data = {
            "title": topic, "subject": subject,
            "plan": ["Topshiriq maqsadi", "Nazariy qism", "Amaliy tahlil", "Xulosa"],
            "goal": f"{topic} bo'yicha bilimlarni mustahkamlash.",
            "theoretical_part": f"{topic} nazariyasi.",
            "practical_part": f"{topic} amaliyoti.",
            "conclusion": "Xulosalar.",
            "references": ["1. Manbalar."]
        }
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.6
            )
            return self._extract_and_parse_json(response.choices[0].message.content, default_data)
        except Exception as e:
            logger.error(f"Mustaqil ish xatosi: {e}")
            return default_data

    async def generate_slides_data(self, topic: str, slide_count: int = 6) -> list:
        system_prompt = "Sen taqdimotlar dizaynerisan. Har bir slayd uchun 3-4 ta qisqa tezis tayyorla. JSON obyekt qaytar: {\"slides\": [{\"slide_number\": 1, \"title\": \"...\", \"bullets\": [\"...\"]}]}"
        user_prompt = f"Mavzu: \"{topic}\". Slaydlar soni: {slide_count}."
        default_slides = [
            {"slide_number": i, "title": f"{topic} - {i}-qism", "bullets": ["Asosiy tushuncha", "Tahliliy qarash", "Kelajak istiqboli"]}
            for i in range(1, slide_count + 1)
        ]
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.6
            )
            data = self._extract_and_parse_json(response.choices[0].message.content, {"slides": default_slides})
            return data.get("slides", default_slides)
        except Exception as e:
            logger.error(f"Slayd xatosi: {e}")
            return default_slides

    async def generate_quiz_data(self, topic: str, count: int = 5) -> list:
        system_prompt = "Sen OTM o'qituvchisisan. 4 variantli testlar tuz. JSON obyekt qaytar: {\"quizzes\": [{\"question\": \"...\", \"options\": [\"A\", \"B\", \"C\", \"D\"], \"correct_index\": 0, \"explanation\": \"...\"}]}"
        user_prompt = f"Mavzu: \"{topic}\". Savollar soni: {count}."
        default_quizzes = [
            {
                "question": f"{topic} bo'yicha asosiy tushuncha nima?",
                "options": ["A variant", "B variant", "C variant", "D variant"],
                "correct_index": 0,
                "explanation": "To'g'ri javob A varianti."
            }
        ]
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.5
            )
            data = self._extract_and_parse_json(response.choices[0].message.content, {"quizzes": default_quizzes})
            return data.get("quizzes", default_quizzes)
        except Exception as e:
            logger.error(f"Quiz xatosi: {e}")
            return default_quizzes

    async def summarize_text(self, text: str) -> str:
        system_prompt = "Sen talabalar uchun konspekt tayyorlovchi aqlli yordamchisan. Berilgan matndan eng muhim xulosalar va qoidalarni punktlar bilan konspekt qilib ber."
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Matn:\n{text[:4000]}"}
                ],
                temperature=0.5
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Matn konspekti: {text[:200]}..."


ai_service = AIService()
