"""WhatsApp tekshiruvchi.

PRINTSIPIAL CHEKLOV: WhatsApp da raqam ro'yxatdan o'tganini aniqlaydigan
ochiq, ishonchli oracle YO'Q. api.whatsapp.com/send deyarli har doim bir xil
"Continue to Chat" sahifasini qaytaradi — raqam bor-yo'qligidan qat'i nazar.
Eski kod aynan shu sahifani ko'rib har raqamni FOUND deb belgilardi
(katta false-positive manbai).

Shuning uchun bu modul:
  - raqam ANIQ yaroqsiz deb belgilansagina NOT_FOUND qaytaradi;
  - FOUND HECH QACHON qaytarmaydi (ishonchli signal yo'q);
  - aks holda halol UNKNOWN qaytaradi.
reliable=False.
"""

from __future__ import annotations

import aiohttp

from ignorant.core.base import BaseChecker, Outcome, not_found, rate_limit, unknown
from ignorant.core.http import CHROME_UA, TIMEOUT
from ignorant.utils.phone import digits_only


class WhatsAppChecker(BaseChecker):
    name = "WhatsApp"
    slug = "whatsapp"
    reliable = False  # ochiq existence-oracle mavjud emas
    status = "❌ oracle yo'q"

    async def check(self, session: aiohttp.ClientSession, phone: str) -> Outcome:
        d = digits_only(phone)
        url = (
            f"https://api.whatsapp.com/send/?phone={d}"
            "&text&type=phone_number&app_absent=0"
        )
        async with session.get(
            url,
            headers={
                "User-Agent": CHROME_UA,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
            allow_redirects=True, timeout=TIMEOUT,
        ) as r:
            if r.status == 429:
                return rate_limit("429")
            text = (await r.text()).lower()
            final = str(r.url).lower()

            # Faqat aniq "yaroqsiz raqam" signali NOT_FOUND beradi.
            if "phone number shared via url is invalid" in text or "invalid" in final:
                return not_found("WhatsApp: invalid number")

            # "Continue to Chat" sahifasi hech narsani isbotlamaydi —
            # WhatsApp uni mavjud bo'lmagan raqamlarga ham ko'rsatadi.
            return unknown("WhatsApp ochiq existence-oracle bermaydi")
