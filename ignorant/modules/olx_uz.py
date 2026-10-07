"""OLX.uz tekshiruvchi (O'zbekiston).

Metod: /api/open/auth/otp/ — login OTP yuborish endpointi.
  javobda isRegistered: true/false bo'lsa — aniq signal.

Oracle sifati: o'rtacha. Eski kodda `if status == 200: return FOUND` degan
xavfli catch-all bor edi — OLX yangi raqamga ham OTP yuborib 200 qaytarishi
mumkin (false-positive). Endi faqat isRegistered maydoniga tayanadi, aks holda
UNKNOWN.
"""

from __future__ import annotations

import json

import aiohttp

from ignorant.core.base import BaseChecker, Outcome, found, not_found, rate_limit, unknown
from ignorant.core.http import CHROME_UA, TIMEOUT
from ignorant.utils.phone import to_e164


class OlxUzChecker(BaseChecker):
    name = "OLX UZ"
    slug = "olx_uz"
    reliable = True
    status = "❌ endpoint o'zgargan"
    phone_hint = "E.164, odatda +998XXXXXXXXX"

    async def check(self, session: aiohttp.ClientSession, phone: str) -> Outcome:
        async with session.post(
            "https://www.olx.uz/api/open/auth/otp/",
            json={"phone": to_e164(phone)},
            headers={
                "User-Agent": CHROME_UA,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Referer": "https://www.olx.uz/",
                "Origin": "https://www.olx.uz",
            },
            timeout=TIMEOUT,
        ) as r:
            if r.status == 429:
                return rate_limit("429")
            try:
                j = json.loads(await r.text())
            except (json.JSONDecodeError, ValueError):
                j = None

            if isinstance(j, dict):
                reg = j.get("isRegistered", j.get("user_exists"))
                if reg is True:
                    return found("isRegistered=true")
                if reg is False:
                    return not_found("isRegistered=false")

            # 404 = endpoint yo'li o'zgargan. Buni NOT_FOUND deb belgilash
            # soxta-negative bo'lardi (barcha raqam "yo'q" chiqadi). Halol UNKNOWN.
            if r.status == 404:
                return unknown("endpoint 404 — yo'l o'zgargan (DevTools bilan yangilash kerak)")
            # Eski `200 → FOUND` olib tashlandi (OTP yangi raqamga ham ketadi).
            return unknown("isRegistered maydoni yo'q")
