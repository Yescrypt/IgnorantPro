"""Amazon tekshiruvchi.

Metod: /ap/forgotpassword — raqamni identifikator sifatida yuborish.

Oracle sifati: ISHONCHSIZ (enumeration-hardened). Amazon odatda hisob bor-yo'q
ligidan qat'i nazar bir xil umumiy javob ko'rsatadi. Faqat aniq
"We found your account" yoki "We cannot find" matni bo'lsagina qaror qilamiz;
aks holda UNKNOWN. reliable=False.
"""

from __future__ import annotations

import re
import urllib.parse

import aiohttp

from ignorant.core.base import BaseChecker, Outcome, not_found, rate_limit, unknown
from ignorant.core.http import CHROME_UA, TIMEOUT

_TOK_RE = re.compile(r'name="appActionToken"\s+value="([^"]+)"')
_META_RE = re.compile(r'name="metadata1"\s+value="([^"]+)"')


class AmazonChecker(BaseChecker):
    name = "Amazon"
    slug = "amazon"
    reliable = False
    status = "❌ soxta-positive"

    async def check(self, session: aiohttp.ClientSession, phone: str) -> Outcome:
        async with session.get(
            "https://www.amazon.com/ap/forgotpassword",
            headers={"User-Agent": CHROME_UA, "Accept-Language": "en-US,en;q=0.9"},
            timeout=TIMEOUT,
        ) as r:
            text = await r.text()
            tm = _TOK_RE.search(text)
            mm = _META_RE.search(text)
            tok = tm.group(1) if tm else ""
            meta = mm.group(1) if mm else ""

        async with session.post(
            "https://www.amazon.com/ap/forgotpassword",
            data=urllib.parse.urlencode({
                "appActionToken": tok,
                "appAction": "FORGOT_PASSWORD",
                "openid.assoc_handle": "usflex",
                "metadata1": meta,
                "email": phone,
            }),
            headers={
                "User-Agent": CHROME_UA,
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://www.amazon.com/ap/forgotpassword",
                "Accept-Language": "en-US,en;q=0.9",
            },
            timeout=TIMEOUT,
        ) as r:
            if r.status == 429:
                return rate_limit("429")
            if r.status >= 500:
                return unknown(f"Amazon {r.status} (bot-block)")
            text = await r.text()
            low = text.lower()
            # MUHIM: Amazon forgot-password KIRITILGAN identifikator uchun
            # maskalangan tiklash variantlarini ko'rsatadi — hisob bor-yo'qligidan
            # qat'i nazar "We found your account" chiqishi mumkin. Shuning uchun
            # bu matn ISHONCHLI signal EMAS (ikki xil raqamga ham FOUND bergan).
            # FOUND ni butunlay olib tashladik — faqat aniq inkor signalini olamiz.
            if "we cannot find" in low or "no account associated" in low:
                return not_found("Amazon: cannot find")
            return unknown("Amazon ishonchli existence-signal bermaydi")
