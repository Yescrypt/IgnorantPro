"""Telegram tekshiruvchi.

Metod: my.telegram.org/auth/send_password

MUHIM (v4.2 dan ko'chirilgan haqiqiy fix): bu endpoint odatda JSON qaytaradi:
  {"random_hash": "..."}   → raqam Telegram akkauntiga bog'langan (FOUND)
  {"error_message": "..."} → raqam yo'q (NOT_FOUND)
Eski "OK" plain-text ham fallback sifatida qoldirilgan.

OGOHLANTIRISH: muvaffaqiyatli bo'lsa, raqam egasining Telegram ilovasiga
login-kod yuboradi (shovqinli). Beqarorlikka qarshi 2 marta urinadi.

Eslatma: v4.2 da `if len(t) > 10: return FOUND` degan xavfli catch-all bor edi
— u ko'p soxta FOUND berardi. Bu yerda OLIB TASHLANGAN: noaniqda UNKNOWN.
"""

from __future__ import annotations

import asyncio
import json
import urllib.parse

import aiohttp

from ignorant.core.base import BaseChecker, Outcome, found, not_found, rate_limit, unknown
from ignorant.core.http import CHROME_UA, TIMEOUT

_MAX_RETRIES = 2


class TelegramChecker(BaseChecker):
    name = "Telegram"
    slug = "telegram"
    reliable = True
    status = "⚠️ RATE_LIMITED"
    phone_hint = "E.164; muvaffaqiyatda raqam egasiga login-kod yuboriladi"

    async def check(self, session: aiohttp.ClientSession, phone: str) -> Outcome:
        last_exc: Exception | None = None
        for attempt in range(_MAX_RETRIES):
            try:
                return await self._attempt(session, phone)
            except (asyncio.TimeoutError, aiohttp.ClientError) as exc:
                last_exc = exc
                if attempt < _MAX_RETRIES - 1:
                    await asyncio.sleep(0.5)  # qisqa kutish, keyin qayta urinish
        if isinstance(last_exc, asyncio.TimeoutError):
            raise last_exc
        return unknown(f"ulanish xatosi: {type(last_exc).__name__}")

    async def _attempt(self, session: aiohttp.ClientSession, phone: str) -> Outcome:
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

            # 1) JSON javob (hozirgi format)
            try:
                j = json.loads(text)
                if isinstance(j, dict):
                    if "random_hash" in j or j.get("status") == "ok":
                        return found("random_hash")
                    if "error_message" in j:
                        return not_found("error_message")
            except (json.JSONDecodeError, ValueError):
                pass

            # 2) Plain-text fallback (eski format)
            if any(x in low for x in ("flood", "too many", "try again later")):
                return rate_limit("FLOOD")
            if text == "OK" or "sent" in low:
                return found("plain: OK")
            if "invalid" in low or ("not" in low and "exist" in low):
                return not_found("invalid/not exist")

            # Xavfli `len(t) > 10 → FOUND` OLIB TASHLANGAN → halol UNKNOWN.
            return unknown(f"noaniq javob: {text[:40]!r}")
