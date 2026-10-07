"""Google tekshiruvchi.

Metod: accounts.google.com signin identifier (batchexecute) oqimi.

Oracle sifati: ISHONCHSIZ — Google deyarli har doim reCAPTCHA / JS-challenge
talab qiladi, server-tomon so'rov ko'pincha bloklanadi. Eski kodda
`if status == 200 and len(text) > 100: return FOUND` degan juda xavfli
catch-all bor edi (reCAPTCHA sahifasini ham FOUND deb olardi). Olib tashlandi:
faqat aniq profil signali FOUND, reCAPTCHA/INVALID → UNKNOWN. reliable=False.
"""

from __future__ import annotations

import json
import re

import aiohttp

from ignorant.core.base import BaseChecker, Outcome, found, not_found, rate_limit, unknown
from ignorant.core.http import CHROME_UA, TIMEOUT

_AT_RE = re.compile(r'"at":"([^"]+)"')


class GoogleChecker(BaseChecker):
    name = "Google"
    slug = "google"
    reliable = False

    async def check(self, session: aiohttp.ClientSession, phone: str) -> Outcome:
        async with session.get(
            "https://accounts.google.com/v3/signin/identifier?"
            "flowName=GlifWebSignIn&flowEntry=ServiceLogin",
            headers={"User-Agent": CHROME_UA, "Accept-Language": "en-US,en;q=0.9"},
            timeout=TIMEOUT,
        ) as r:
            text = await r.text()
        am = _AT_RE.search(text)
        at_tok = am.group(1) if am else ""
        if not at_tok:
            return unknown("at token olinmadi (JS-challenge)")

        import urllib.parse

        async with session.post(
            "https://accounts.google.com/v3/signin/_/AccountsSignInUi/data/batchexecute",
            data=urllib.parse.urlencode({
                "f.req": json.dumps([[["nKjvib",
                    json.dumps([phone, 1, [], None, []]), None, "generic"]]]),
                "at": at_tok,
            }),
            headers={
                "User-Agent": CHROME_UA,
                "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
                "Referer": "https://accounts.google.com/v3/signin/identifier",
                "Origin": "https://accounts.google.com",
                "X-Same-Domain": "1",
            },
            timeout=TIMEOUT,
        ) as r:
            if r.status == 429:
                return rate_limit("429")
            text = await r.text()
            low = text.lower()
            if "recaptcha" in low or "invalid" in low:
                return unknown("reCAPTCHA / INVALID")
            # Google oqimida keyingi (parol) qadamga o'tish signali.
            if '"gf.sis"' in text or "password" in low and "challenge" in low:
                return found("next step signal")
            # Eski xavfli `200 and len>100 → FOUND` olib tashlandi.
            return unknown("aniq signal yo'q")
