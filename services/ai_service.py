import json
import asyncio
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
            timeout=45.0
        )
        self.model = settings.QWEN_MODEL


    async def _call_ai_with_retry(self, messages: list, temperature: float = 0.6, use_json: bool = True, max_retries: int = 2) -> str:
        """AI modeliga so'rov yuborish (retry bilan)"""
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                }
                if use_json:
                    kwargs["response_format"] = {"type": "json_object"}
                response = await self.client.chat.completions.create(**kwargs)
                return response.choices[0].message.content
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    wait_time = (attempt + 1) * 2  # 2s, 4s
                    logger.warning(f"AI so'rov xatosi (urinish {attempt + 1}/{max_retries + 1}): {e}. {wait_time}s kutilmoqda...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"AI so'rov yakuniy xatosi: {e}")
                    raise last_error

    def _extract_and_parse_json(self, content: str, default_data: dict) -> dict:
        content = content.strip()
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
            match = re.search(r'(\{.*\}|\[.*\])', content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except Exception:
                    pass
            logger.warning("JSON parse qilib bo'lmadi, standart strukturadan foydalaniladi.")
            return default_data

    async def generate_referat_structure(self, topic: str, subject: str = "") -> dict:
        """
        Referat uchun O'zbekiston OTMlari standartidagi to'liq, boy va ilmiy akademik matn tayyorlaydi.
        """
        system_prompt = (
            "Sen O'zbekiston oliy ta'lim tizimi bo'yicha akademik referat va dissertatsiyalar yozuvchi professiorsan. "
            "Matn chuqur ilmiy, statistik ma'lumotlar, qonuniy asoslar, xorijiy tajriba va amaliy takliflarga boy bo'lishi shart. "
            "Javobingni FAQAT toza JSON formatida qaytar."
        )
        user_prompt = f"""Mavzu: "{topic}". Fan: "{subject}".
Quyidagi JSON formatda to'liq referat matnini tayyorlab ber:
{{
  "title": "{topic}",
  "subject": "{subject}",
  "plan": [
    "Kirish",
    "I BOB. {topic} ning nazariy-uslubiy asoslari va tushunchasi",
    "II BOB. Hozirgi holat tahlili va amaliy muammolar",
    "III BOB. Rivojlantirish istiqbollari, xorij tajribasi va innovatsion yechimlar",
    "Xulosa va amaliy tavsiyalar",
    "Foydalanilgan adabiyotlar ro'yxati"
  ],
  "introduction": "Mavzuning dolzarbligi: bugungi kunda ushbu sohaning ahamiyati. Tadqiqotning maqsadi va vazifalari. Tadqiqot obyekti va predmeti. Amaliy ahamiyati (kamida 250 so'z, to'liq ilmiy matn)...",
  "chapters": [
    {{
      "title": "I BOB. {topic} ning nazariy-uslubiy asoslari",
      "sections": [
        {{"subtitle": "1.1. Asosiy tushunchalar, tasnif va rivojlanish tarixi", "text": "Chuqur ilmiy tahlil, olimlarning qarashlari va ta'riflar (kamida 200 so'z)..."}},
        {{"subtitle": "1.2. Huquqiy va me'yoriy asoslar", "text": "O'zbekiston Respublikasi qonunlari, farmonlari va xalqaro standartlar tahlili (kamida 200 so'z)..."}}
      ]
    }},
    {{
      "title": "II BOB. Hozirgi holat tahlili va amaliy muammolar",
      "sections": [
        {{"subtitle": "2.1. Sohadagi mavjud holat va statistik ko'rsatkichlar", "text": "Amaliy tahlil, raqamlar, statistik ma'lumotlar va tendensiyalar (kamida 200 so'z)..."}},
        {{"subtitle": "2.2. Tizimdagi asosiy muammolar va to'siqlar", "text": "Mavjud kamchiliklar, texnologik va tashkiliy muammolar (kamida 200 so'z)..."}}
      ]
    }},
    {{
      "title": "III BOB. Rivojlantirish istiqbollari va innovatsion yechimlar",
      "sections": [
        {{"subtitle": "3.1. Rivojlangan xorijiy davlatlar tajribasi", "text": "AQSH, Yevropa va Osiyo mamlakatlari tajribasini O'zbekistonga tatbiq etish (kamida 200 so'z)..."}},
        {{"subtitle": "3.2. Muammolarni bartaraf etish bo'yicha ilmiy va amaliy takliflar", "text": "Konkret qadamlar, iqtisodiy va texnologik samaradorlik (kamida 200 so'z)..."}}
      ]
    }}
  ],
  "conclusion": "Referatdan kelib chiqqan 5 ta asosiy ilmiy xulosa va amaliy tavsiyalar punktlar bilan...",
  "references": [
    "1. O'zbekiston Respublikasi Prezidentining tegishli Farmon va Qarorlari to'plami. Toshkent, 2023-2025 yy.",
    "2. Karimov I.A., Mirziyoyev Sh.M. Asarlari va nutqlari.",
    "3. OTM professor-o'qituvchilari tomonidan chop etilgan sohaviy darsliklar va o'quv qo'llanmalari (2022-2025).",
    "4. Xalqaro nufuzli Scopus va Web of Science bazasidagi ilmiy maqolalar.",
    "5. Davlat statistika agentligi va rasmiy portallar ma'lumotlari."
  ]
}}"""

        default_data = {
            "title": topic,
            "subject": subject,
            "plan": [
                "Kirish",
                f"I BOB. {topic} ning nazariy asoslari",
                f"II BOB. {topic} ning amaliy tahlili",
                "Xulosa va tavsiyalar",
                "Foydalanilgan adabiyotlar ro'yxati"
            ],
            "introduction": f"{topic} mavzusi hozirgi kunda ilmiy, texnologik va ijtimoiy-iqtisodiy sohalarda dolzarb ahamiyat kasb etadi. Mazkur referatning maqsadi sohani har tomonlama o'rganish va ilmiy xulosalar ishlab chiqishdan iborat.",
            "chapters": [
                {
                    "title": f"I BOB. {topic} ning nazariy asoslari",
                    "sections": [
                        {"subtitle": "1.1. Nazariy tushunchalar va tamoyillar", "text": f"{topic} bo'yicha nazariy qarashlar va asosiy qoidalar o'rganildi."},
                        {"subtitle": "1.2. Rivojlanish bosqichlari", "text": f"{topic} rivojlanishining asosiy bosqichlari va xususiyatlari."}
                    ]
                },
                {
                    "title": f"II BOB. {topic} ning amaliy tahlili",
                    "sections": [
                        {"subtitle": "2.1. Amaliyotdagi mavjud holat", "text": f"{topic} sohasidagi real misollar va amaliy tahlillar."},
                        {"subtitle": "2.2. Takliflar va yechimlar", "text": f"Sohani rivojlantirish bo'yicha ilg'or takliflar."}
                    ]
                }
            ],
            "conclusion": f"{topic} bo'yicha olib borilgan tahlillar natijasida sohani yanada takomillashtirish zarurligi aniqlandi.",
            "references": [
                "1. O'zbekiston Respublikasi qonunchilik hujjatlari.",
                "2. Sohaviy zamonaviy darsliklar (2024-yil)."
            ]
        }

        try:
            raw = await self._call_ai_with_retry(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6
            )
            return self._extract_and_parse_json(raw, default_data)
        except Exception as e:
            logger.error(f"Referat generatsiya xatosi: {e}")
            return default_data

    async def generate_slides_data(self, topic: str, slide_count: int = 6) -> list:
        """
        Zamonaviy taqdimot dizayni uchun boyitilgan, kartochkali slaydlar kontentini yaratadi.
        """
        system_prompt = (
            "Sen professional taqdimotlar va infographic mutaxassisisan (Pitch/Gamma darajasida). "
            "Har bir slayd uchun jozibador sarlavha (title), asosiy tezis/shior (subtitle), va 3-4 ta aniq kartochka (cards) tayyorla. "
            "Har bir kartochkada: card_title (Qisqa va jarangdor nom) va card_text (Aniq fakt, tushuntirish yoki raqam) bo'lishi shart! "
            "FAQAT toza JSON formatida: {\"slides\": [{\"slide_number\": 1, \"title\": \"...\", \"subtitle\": \"...\", \"cards\": [{\"card_title\": \"...\", \"card_text\": \"...\"}]}]}"
        )
        user_prompt = f"Mavzu: \"{topic}\". Slaydlar soni: {slide_count}."

        default_slides = [
            {
                "slide_number": i,
                "title": f"{topic} - {i}-bosqich",
                "subtitle": f"{topic} bo'yicha asosiy tushunchalar va strategik tahlil",
                "cards": [
                    {"card_title": "Nazariy Asos", "card_text": "Sohaning fundamental qoidalari va xalqaro standartlari tahlili."},
                    {"card_title": "Amaliy Tajriba", "card_text": "Zamonaviy vositalar va texnologiyalarning amaliyotda qo'llanilishi."},
                    {"card_title": "Asosiy Samaradorlik", "card_text": "Jarayonlarni 2-3 barobarga tezlashtirish va xarajatlarni optimallashtirish."}
                ]
            }
            for i in range(1, slide_count + 1)
        ]

        try:
            raw = await self._call_ai_with_retry(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6
            )
            data = self._extract_and_parse_json(raw, {"slides": default_slides})
            return data.get("slides", default_slides)
        except Exception as e:
            logger.error(f"Slayd xatosi: {e}")
            return default_slides

    async def generate_mustaqil_ish_structure(self, topic: str, subject: str = "") -> dict:
        system_prompt = "Sen talabalar uchun mustaqil ta'lim ishlarini OTM talablariga mos, to'liq ilmiy asosda shakllantiruvchi mutaxassissan. FAQAT toza JSON formatida javob ber."
        user_prompt = f"""Mavzu: "{topic}". Fan: "{subject}".
JSON format:
{{
  "title": "{topic}",
  "subject": "{subject}",
  "plan": ["Topshiriq maqsadi va vazifalari", "Nazariy-uslubiy qism", "Amaliy tahlil va misollar", "Xulosa va takliflar"],
  "goal": "Mustaqil ishning maqsadi, dolzarbligi va hal etilishi lozim bo'lgan vazifalar (kamida 150 so'z)...",
  "theoretical_part": "Mavzu bo'yicha nazariy tushunchalar, qonuniyatlar va formulalar (kamida 300 so'z)...",
  "practical_part": "Amaliy tahlil, taqqoslash, misollar va hisob-kitoblar (kamida 300 so'z)...",
  "conclusion": "Umumiy xulosa, erishilgan natijalar va amaliy tavsiyalar (kamida 150 so'z)...",
  "references": ["1. OTM darsliklari (2024).", "2. Ilmiy jurnallar va maqolalar."]
}}"""
        default_data = {
            "title": topic, "subject": subject,
            "plan": ["Topshiriq maqsadi", "Nazariy qism", "Amaliy tahlil", "Xulosa"],
            "goal": f"{topic} bo'yicha bilimlarni mustahkamlash va amaliy tahlil qilish.",
            "theoretical_part": f"{topic} nazariy asoslari va muhim ilmiy qarashlar.",
            "practical_part": f"{topic} sohasidagi amaliy misollar va tahliliy natijalar.",
            "conclusion": f"Mustaqil ish davomida {topic} mavzusi to'liq o'rganildi va xulosalar shakllantirildi.",
            "references": ["1. Sohaviy darsliklar to'plami."]
        }
        try:
            raw = await self._call_ai_with_retry(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6
            )
            return self._extract_and_parse_json(raw, default_data)
        except Exception as e:
            logger.error(f"Mustaqil ish xatosi: {e}")
            return default_data

    async def generate_quiz_data(self, topic: str, count: int = 5) -> list:
        system_prompt = "Sen OTM o'qituvchisisan. 4 variantli mantiqiy va sifatli testlar tuz. Har bir savolga chuqur tushuntirish ber. JSON: {\"quizzes\": [{\"question\": \"...\", \"options\": [\"A\", \"B\", \"C\", \"D\"], \"correct_index\": 0, \"explanation\": \"...\"}]}"
        user_prompt = f"Mavzu: \"{topic}\". Savollar soni: {count}."
        default_quizzes = [
            {
                "question": f"{topic} bo'yicha asosiy tushuncha qaysi javobda to'g'ri berilgan?",
                "options": ["To'g'ri ta'rif", "Noto'g'ri ta'rif 1", "Noto'g'ri ta'rif 2", "Noto'g'ri ta'rif 3"],
                "correct_index": 0,
                "explanation": "Ushbu savolda A varianti fanning fundamental tamoyillariga to'liq mos keladi."
            }
        ]
        try:
            raw = await self._call_ai_with_retry(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5
            )
            data = self._extract_and_parse_json(raw, {"quizzes": default_quizzes})
            return data.get("quizzes", default_quizzes)
        except Exception as e:
            logger.error(f"Quiz xatosi: {e}")
            return default_quizzes

    async def summarize_text(self, text: str) -> str:
        system_prompt = "Sen talabalar uchun konspekt tayyorlovchi professional mutaxassissan. Matnni asosiy sarlavhalar, ta'riflar, qoidalar va xulosalarga bo'lib, tartibli konspekt qil."
        try:
            raw = await self._call_ai_with_retry(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Matn:\n{text[:6000]}"}
                ],
                temperature=0.5,
                use_json=False
            )
            return raw.strip()
        except Exception as e:
            return f"Matn konspekti: {text[:200]}..."


ai_service = AIService()
