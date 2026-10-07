"""Telegram tekshiruvchi.

Metod: my.telegram.org/auth/send_password
  Javob "OK"  → raqam Telegram akkauntiga bog'langan (FOUND)
  "Invalid phone number" → NOT_FOUND
  "...FLOOD..." → rate limit

OGOHLANTIRISH: bu endpoint muvaffaqiyatli bo'lsa, raqam egasining Telegram
ilovasiga login-kod yuboradi (shovqinli). Shuning uchun Telegram ishonchli
oracle bo'lsa-da, uni ehtiyotkorlik bilan ishlatish kerak.
"""

from __future__ import annotations

import urllib.parse

import aiohttp

from ignorant.core.base import BaseChecker, Outcome, found, not_found, rate_limit, unknown
from ignorant.core.http import CHROME_UA, TIMEOUT


class TelegramChecker(BaseChecker):
    name = "Telegram"
    slug = "telegram"
    reliable = True
    phone_hint = "E.164; muvaffaqiyatda raqam egasiga login-kod yuboriladi"

    async def check(self, session: aiohttp.ClientSession, phone: str) -> Outcome:
        async with session.post(
            "https://my.telegram.org/auth/send_password",
            data=urllib.parse.urlencode({"phone": phone}),
            headers={
                "User-Agent": CHROME_UA,
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://my.telegram.org/auth",
                "Origin": "https://my.telegram.org",
                "X-Requested-With": "XMLHttpRequest",
            },
            timeout=TIMEOUT,
        ) as r:
            if r.status == 429:
                return rate_limit("429")
            text = (await r.text()).strip()
            low = text.lower()

            if "flood" in low:
                return rate_limit("FLOOD")
            if text == "OK" or "random_hash" in low or "sent" in low:
                return found("send_password: OK")
            if "invalid" in low or "not" in low and "exist" in low:
                return not_found("invalid/not exist")
            # Eski kodda bu yerda xavfli "status==200 va qisqa → FOUND" bor edi.
            # Uni olib tashladik: noaniq javob → UNKNOWN.
            return unknown(f"noaniq javob: {text[:40]!r}")
