"""Twitter / X tekshiruvchi.

Metod: onboarding "forgot-password" flow.
  guest token → flow init → EnterUserIdentifier (phone yuborish)
  Keyingi subtask (SelectAuthMethod / PasswordReset ...) chiqsa → FOUND
  errors[].code in (141, 32) → NOT_FOUND

Oracle sifati: ISHONCHSIZ. X 2024+ da ko'p so'rovlarga
x-client-transaction-id va JS-challenge talab qiladi; guest-token oqimi
tez-tez buziladi. Shuning uchun reliable=False, noaniqda UNKNOWN.
Bearer token — bu Twitter web ilovasining ommaviy (public) tokeni.
"""

from __future__ import annotations

import json

import aiohttp

from ignorant.core.base import BaseChecker, Outcome, found, not_found, rate_limit, unknown
from ignorant.core.http import CHROME_UA, SHORT_TIMEOUT, TIMEOUT

# Twitter web-app ning commonly-known public bearer tokeni.
_BEARER = (
    "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
    "%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
)

_NEXT_SUBTASKS = {"SelectAuthMethod", "ChooseIdentifier", "PasswordReset", "EnterPassword"}


class TwitterChecker(BaseChecker):
    name = "Twitter/X"
    slug = "twitter"
    reliable = False

    async def check(self, session: aiohttp.ClientSession, phone: str) -> Outcome:
        # 1) Guest token
        async with session.post(
            "https://api.twitter.com/1.1/guest/activate.json",
            headers={
                "Authorization": f"Bearer {_BEARER}",
                "User-Agent": CHROME_UA,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=SHORT_TIMEOUT,
        ) as r:
            if r.status != 200:
                return unknown(f"guest token {r.status}")
            gtok = (await r.json()).get("guest_token", "")
        if not gtok:
            return unknown("guest token bo'sh")

        headers = {
            "Authorization": f"Bearer {_BEARER}",
            "X-Guest-Token": gtok,
            "User-Agent": CHROME_UA,
            "Content-Type": "application/json",
            "Accept": "*/*",
            "X-Twitter-Active-User": "yes",
            "X-Twitter-Client-Language": "en",
        }

        # 2) Flow init
        async with session.post(
            "https://api.twitter.com/1.1/onboarding/task.json?flow_name=forgot-password",
            json={"flow_token": None, "input_flow_data": {}},
            headers=headers, timeout=TIMEOUT,
        ) as r:
            if r.status == 429:
                return rate_limit("flow init 429")
            flow_token = (await r.json()).get("flow_token", "")
        if not flow_token:
            return unknown("flow_token olinmadi")

        # 3) Raqamni yuborish
        payload = {
            "flow_token": flow_token,
            "subtask_inputs": [{
                "subtask_id": "EnterUserIdentifier",
                "enter_text": {"text": phone, "link": "next_link"},
            }],
        }
        async with session.post(
            "https://api.twitter.com/1.1/onboarding/task.json",
            json=payload, headers=headers, timeout=TIMEOUT,
        ) as r:
            if r.status == 429:
                return rate_limit("task 429")
            try:
                j = json.loads(await r.text())
            except (json.JSONDecodeError, ValueError):
                return unknown("JSON emas")

            for st in j.get("subtasks", []):
                if st.get("subtask_id") in _NEXT_SUBTASKS:
                    return found(f"subtask={st.get('subtask_id')}")
            for e in j.get("errors", []):
                if e.get("code") in (141, 32):
                    return not_found(f"error code={e.get('code')}")

            # Eski kodda `subtasks and not errors → FOUND` catch-all bor edi;
            # u false-positive berardi. Olib tashlandi.
            return unknown("keyingi subtask aniqlanmadi")
