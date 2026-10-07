"""Viber tekshiruvchi.

Metod: account.viber.com/en/forgot-password form.

Oracle sifati: ISHONCHSIZ. Eski kodda oxirida `return "NOT_FOUND"` degan
catch-all bor edi — ya'ni signal topilmasa ham "yo'q" deb belgilardi
(false-negative). Buni UNKNOWN ga almashtirdik. reliable=False.
"""

from __future__ import annotations

import re
import urllib.parse

import aiohttp

from ignorant.core.base import BaseChecker, Outcome, found, not_found, rate_limit, unknown
from ignorant.core.http import CHROME_UA, TIMEOUT

_CSRF_RE1 = re.compile(r'name="csrfToken"\s+value="([^"]+)"')
_CSRF_RE2 = re.compile(r'"csrf[^"]*"[:\s]+"([^"]+)"')


class ViberChecker(BaseChecker):
    name = "Viber"
    slug = "viber"
    reliable = False
    status = "⚠️ UNSTABLE"

    async def check(self, session: aiohttp.ClientSession, phone: str) -> Outcome:
        async with session.get(
            "https://account.viber.com/en/forgot-password",
            headers={"User-Agent": CHROME_UA}, timeout=TIMEOUT,
        ) as r:
            text = await r.text()
            m = _CSRF_RE1.search(text) or _CSRF_RE2.search(text)
            csrf = m.group(1) if m else ""

        async with session.post(
            "https://account.viber.com/en/forgot-password",
            data=urllib.parse.urlencode({"phoneNumber": phone, "csrfToken": csrf}),
            headers={
                "User-Agent": CHROME_UA,
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://account.viber.com/en/forgot-password",
                "Origin": "https://account.viber.com",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
            timeout=TIMEOUT, allow_redirects=True,
        ) as r:
            if r.status == 429:
                return rate_limit("429")
            final = str(r.url).lower()
            text = (await r.text()).lower()

            if any(k in final for k in ("check", "sent", "success")):
                return found(f"redirect: {final[:40]}")
            if "we sent" in text or "check your" in text:
                return found("body: sent")
            if "not found" in text or "no account" in text:
                return not_found("body: no account")

            # Eski catch-all `return NOT_FOUND` → endi halol UNKNOWN.
            return unknown("aniq signal yo'q")
