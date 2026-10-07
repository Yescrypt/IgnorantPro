"""TikTok tekshiruvchi.

Metod: /passport/mobile/check_unique/  (POST)
  data.message_code == 2  → raqam band (FOUND)
  data.message_code == 0  → bo'sh (NOT_FOUND)

Eski kodda davlat kodi noto'g'ri ajratilgan edi
(cc = d[:3] if 998 else d[:1]) — endi `split_cc` to'g'ri ajratadi.

Oracle sifati: ISHONCHSIZ. TikTok bu endpointga endi imzolangan parametr
(_signature / X-Argus) talab qiladi; imzosiz so'rov ko'pincha verify/forbidden
sahifa qaytaradi. Shuning uchun reliable=False va aniq signal bo'lmasa UNKNOWN.
"""

from __future__ import annotations

import json
import urllib.parse

import aiohttp

from ignorant.core.base import BaseChecker, Outcome, found, not_found, rate_limit, unknown
from ignorant.utils.phone import split_cc

_UA = (
    "com.zhiliaoapp.musically/2023.100 (Linux; U; Android 13; en_US; "
    "SM-G998B; Build/TP1A.220624.014; Cronet/TTNetVersion:b4d74d38 "
    "3.7.1.0 HeaderSize/20220504-GP CloseGuard/0)"
)

_ENDPOINTS = (
    "https://www.tiktok.com/passport/mobile/check_unique/",
    "https://www.tiktok.com/api/v1/passport/mobile/check_unique/",
)


class TikTokChecker(BaseChecker):
    name = "TikTok"
    slug = "tiktok"
    reliable = False  # imzolangan parametr talab qilinadi — ishonchsiz
    status = "⚠️ GEO_BLOCK"

    async def check(self, session: aiohttp.ClientSession, phone: str) -> Outcome:
        cc, num = split_cc(phone)
        headers = {
            "User-Agent": _UA,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
        }
        post_data = urllib.parse.urlencode({
            "mobile": num,
            "area_code": cc,
            "aid": "1284",
            "account_sdk_source": "tiktok",
            "multi_login": "0",
        })

        last_note = "hech qaysi endpoint javob bermadi"
        for url in _ENDPOINTS:
            try:
                async with session.post(url, data=post_data, headers=headers) as r:
                    if r.status == 429:
                        return rate_limit("429")
                    if r.status in (403, 404, 405):
                        last_note = f"{r.status} (imzo/forbidden)"
                        continue
                    try:
                        j = json.loads(await r.text())
                    except (json.JSONDecodeError, ValueError):
                        last_note = "JSON emas (verify sahifa?)"
                        continue
                    data = j.get("data", {}) or {}
                    mc = data.get("message_code", j.get("message_code", -99))
                    if mc == 2 or data.get("is_unique") == 0:
                        return found("message_code=2")
                    if mc == 0 or data.get("is_unique") == 1:
                        return not_found("message_code=0")
                    if j.get("error_code") in (1000, -1):
                        last_note = f"error_code={j.get('error_code')}"
                        continue
                    last_note = f"noaniq javob mc={mc}"
            except Exception as exc:  # noqa: BLE001 — keyingi endpointga o'tamiz
                last_note = f"{type(exc).__name__}"
                continue

        return unknown(last_note)
