"""LinkedIn tekshiruvchi.

Metod: /uas/request-password-reset — raqam bilan.

Oracle sifati: ISHONCHSIZ (enumeration-hardened). LinkedIn odatda umumiy
javob beradi. Eski kodda `if "request-password-reset" in final: NOT_FOUND`
degan catch-all bor edi (sahifada qolish = yo'q deb o'ylash) — bu noto'g'ri,
chunki xato/validatsiyada ham sahifada qoladi. Olib tashlandi → UNKNOWN.
reliable=False.
"""

from __future__ import annotations

import re
import urllib.parse

import aiohttp

from ignorant.core.base import BaseChecker, Outcome, found, not_found, rate_limit, unknown
from ignorant.core.http import CHROME_UA, TIMEOUT

_CSRF_RE = re.compile(r'csrfToken=([^&"\']+)')
_PI_RE = re.compile(r'"pageInstance":"([^"]+)"')


class LinkedInChecker(BaseChecker):
    name = "LinkedIn"
    slug = "linkedin"
    reliable = False

    async def check(self, session: aiohttp.ClientSession, phone: str) -> Outcome:
        async with session.get(
            "https://www.linkedin.com/uas/request-password-reset",
            headers={"User-Agent": CHROME_UA, "Accept-Language": "en-US,en;q=0.9"},
            timeout=TIMEOUT,
        ) as r:
            text = await r.text()
            cm = _CSRF_RE.search(text)
            pm = _PI_RE.search(text)
            csrf = cm.group(1) if cm else ""
            pi = pm.group(1) if pm else ""

        async with session.post(
            "https://www.linkedin.com/uas/request-password-reset",
            data=urllib.parse.urlencode({
                "csrfToken": csrf,
                "pageInstance": pi,
                "resendUrl": "",
                "email": phone,
                "btn-primary": "",
            }),
            headers={
                "User-Agent": CHROME_UA,
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://www.linkedin.com/uas/request-password-reset",
                "Origin": "https://www.linkedin.com",
            },
            timeout=TIMEOUT, allow_redirects=True,
        ) as r:
            if r.status == 429:
                return rate_limit("429")
            final = str(r.url).lower()
            text = (await r.text()).lower()
            if "checkyouremail" in final or "check_your_email" in final:
                return found(f"redirect: {final[:40]}")
            if "we sent" in text or "check your email" in text:
                return found("body: sent")
            if "doesn't match" in text or "no account" in text:
                return not_found("body: no match")
            return unknown("umumiy javob (hardened)")
