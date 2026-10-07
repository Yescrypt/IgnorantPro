"""Microsoft tekshiruvchi.

Metod: login.live.com/GetCredentialType.srf
  IfExistsResult: 0 = mavjud, 1 = yo'q, 5 = throttled, 6 = federated (mavjud)

Oracle sifati: YAXSHI — bu Microsoft hisobi uchun ishonchli existence oracle.
Eslatma: GetCredentialType odatda email/username kutadi; faqat telefon raqami
har doim ham hisobga bog'lanmasligi mumkin. reliable=True.
"""

from __future__ import annotations

import json
import re

import aiohttp

from ignorant.core.base import (
    BaseChecker, Outcome, error, found, not_found, rate_limit, unknown,
)
from ignorant.core.http import CHROME_UA, TIMEOUT

_UAID_RE = re.compile(r'"uaid":"([^"]+)"')
_SCTX_RE = re.compile(r'"sCtx":"([^"]+)"')
_SFT_RE = re.compile(r'"sFT":"([^"]+)"')


class MicrosoftChecker(BaseChecker):
    name = "Microsoft"
    slug = "microsoft"
    reliable = True
    status = "⚠️ ERROR_RESPONSE"

    async def check(self, session: aiohttp.ClientSession, phone: str) -> Outcome:
        async with session.get(
            "https://login.live.com/login.srf",
            headers={"User-Agent": CHROME_UA}, timeout=TIMEOUT,
        ) as r:
            text = await r.text()
            um = _UAID_RE.search(text)
            uaid = um.group(1) if um else "61b8eed8e4c84a80ac55e1ea"
            sm = _SCTX_RE.search(text)
            sctx = sm.group(1) if sm else ""
            fm = _SFT_RE.search(text)
            flow_tok = fm.group(1) if fm else ""

        payload = {
            "username": phone,
            "uaid": uaid,
            "isOtherIdpSupported": True,
            "checkPhoneNumberAvailability": False,
            "isCookieBannerShown": False,
            "isFidoSupported": True,
            "forceotclogin": False,
            "isRemoteNGCSupported": True,
            "isAccessPassSupported": True,
            "sCtx": sctx,
            "flowToken": flow_tok,
        }
        async with session.post(
            "https://login.live.com/GetCredentialType.srf?mkt=en-US",
            json=payload,
            headers={
                "User-Agent": CHROME_UA,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Referer": "https://login.live.com/",
                "Origin": "https://login.live.com",
                "hpgid": "33",
                "hpgact": "1900",
                "client-request-id": uaid,
            },
            timeout=TIMEOUT,
        ) as r:
            if r.status == 429:
                return rate_limit("429")
            try:
                j = json.loads(await r.text())
            except (json.JSONDecodeError, ValueError):
                return unknown("JSON emas")
            # ErrorHR bo'lsa — Microsoft so'rovni qayta ishlay olmadi.
            ehr = j.get("ErrorHR")
            if ehr:
                # 80046703 = kiritilgan identifikator noto'g'ri formatda.
                # Consumer login telefon raqamni qabul qilmaydi — faqat email/username.
                if str(ehr).lower() in ("80046703", "0x80046703"):
                    return unknown("telefon qo'llab-quvvatlanmaydi (email kerak)")
                return error(f"ErrorHR={ehr}")
            ier = j.get("IfExistsResult", -1)
            if ier in (0, 6):
                return found(f"IfExistsResult={ier}")
            if ier == 1:
                return not_found("IfExistsResult=1")
            if ier == 5:
                return rate_limit("IfExistsResult=5 (throttled)")
            return unknown(f"IfExistsResult={ier}")
