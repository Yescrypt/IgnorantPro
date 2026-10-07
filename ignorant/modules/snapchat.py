"""Snapchat tekshiruvchi.

Metod: accounts.snapchat.com parol-tiklash oqimi.

Oracle sifati: ISHONCHSIZ (enumeration-hardened). Eski kodda
`if status == 302: return FOUND` degan xavfli catch-all bor edi — Snapchat
ham muvaffaqiyat, ham xatoda redirect qiladi, shuning uchun bu har raqamni
FOUND qilardi. Bu olib tashlandi: faqat aniq matn/redirect signali hisobga
olinadi, aks holda UNKNOWN. reliable=False.
"""

from __future__ import annotations

import re

import aiohttp

from ignorant.core.base import BaseChecker, Outcome, found, not_found, rate_limit, unknown
from ignorant.core.http import CHROME_UA, TIMEOUT

_XTS_RE = re.compile(r'name="xts"\s+value="([^"]+)"')


class SnapchatChecker(BaseChecker):
    name = "Snapchat"
    slug = "snapchat"
    reliable = False

    async def check(self, session: aiohttp.ClientSession, phone: str) -> Outcome:
        import urllib.parse

        async with session.get(
            "https://accounts.snapchat.com/accounts/password_reset",
            headers={"User-Agent": CHROME_UA}, timeout=TIMEOUT,
        ) as r:
            m = _XTS_RE.search(await r.text())
            xts = m.group(1) if m else ""

        async with session.post(
            "https://accounts.snapchat.com/accounts/password_reset_request",
            data=urllib.parse.urlencode({"forgot_password_field": phone, "xts": xts}),
            headers={
                "User-Agent": CHROME_UA,
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://accounts.snapchat.com/accounts/password_reset",
                "Origin": "https://accounts.snapchat.com",
                "Accept": "text/html,application/xhtml+xml",
            },
            timeout=TIMEOUT, allow_redirects=False,
        ) as r:
            if r.status == 429:
                return rate_limit("429")
            location = r.headers.get("Location", "").lower()
            if any(k in location for k in ("confirmation", "success", "sent")):
                return found(f"redirect: {location[:40]}")
            if any(k in location for k in ("error", "invalid", "not_found")):
                return not_found(f"redirect: {location[:40]}")

            text = (await r.text()).lower()
            if "we found" in text or "we sent" in text or "verify your" in text:
                return found("body: confirmation")
            if "no account" in text or "couldn't find" in text or "not found" in text:
                return not_found("body: no account")

            # Eski xavfli `302 → FOUND` olib tashlandi.
            return unknown("aniq signal yo'q (hardened)")
