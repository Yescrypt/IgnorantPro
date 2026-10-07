"""Instagram tekshiruvchi.

Metod: web signup/lookup oqimi.
  1. GET /accounts/emailsignup/  → csrftoken
  2. POST /api/v1/users/lookup_phone_with_count/  → {user_id|count|obfuscated_phone}
  3. Fallback: account_recovery_send_ajax

Oracle sifati: o'rtacha-yaxshi, lekin Instagram so'rovlarni tez-tez
rate-limit qiladi. Aniq signal bo'lmasa — UNKNOWN qaytaramiz.
"""

from __future__ import annotations

import json
import re
import urllib.parse

import aiohttp

from ignorant.core.base import (
    BaseChecker, Outcome, error, found, not_found, rate_limit, unknown,
)
from ignorant.core.http import CHROME_UA, TIMEOUT

_CSRF_RE = re.compile(r'"csrf_token":"([^"]+)"')


class InstagramChecker(BaseChecker):
    name = "Instagram"
    slug = "instagram"
    reliable = True
    status = "❌ API_DOWN"

    async def check(self, session: aiohttp.ClientSession, phone: str) -> Outcome:
        # 1-qadam: csrf token
        async with session.get(
            "https://www.instagram.com/accounts/emailsignup/",
            headers={"User-Agent": CHROME_UA, "Accept-Language": "en-US,en;q=0.9"},
            timeout=TIMEOUT,
        ) as r:
            if r.status >= 500:
                # Instagram API ishlamayapti (v4.2 da kuzatilgan 2024-12 holati).
                return error(f"IG {r.status} (API down)")
            csrf = r.cookies.get("csrftoken")
            csrf = csrf.value if csrf else ""
            if not csrf:
                m = _CSRF_RE.search(await r.text())
                csrf = m.group(1) if m else ""

        if not csrf:
            return unknown("csrf token olinmadi")

        headers = {
            "User-Agent": CHROME_UA,
            "X-CSRFToken": csrf,
            "X-Instagram-AJAX": "1",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://www.instagram.com/accounts/emailsignup/",
            "Origin": "https://www.instagram.com",
            "Accept-Language": "en-US,en;q=0.9",
        }

        # 2-qadam: lookup endpoint
        async with session.post(
            "https://www.instagram.com/api/v1/users/lookup_phone_with_count/",
            data=urllib.parse.urlencode({"phone_number": phone}),
            headers=headers, timeout=TIMEOUT,
        ) as r:
            if r.status == 429:
                return rate_limit("lookup 429")
            try:
                j = json.loads(await r.text())
            except (json.JSONDecodeError, ValueError):
                j = None
            if isinstance(j, dict):
                if j.get("user_id") or j.get("count", 0) > 0 or j.get("obfuscated_phone"):
                    return found("lookup: user_id/count")
                if j.get("message") == "No users found":
                    return not_found("lookup: No users found")

        # 3-qadam: fallback — account recovery (bir nechta endpoint, v4.2 dan)
        fallback_endpoints = (
            "https://www.instagram.com/accounts/account_recovery_send_ajax/",
            "https://www.instagram.com/api/v1/accounts/send_recovery_flow_email/",
        )
        for endpoint in fallback_endpoints:
            try:
                async with session.post(
                    endpoint,
                    data=urllib.parse.urlencode({
                        "phone_number": phone,
                        "phone_or_email": phone,
                        "user_id": "",
                    }),
                    headers=headers, timeout=TIMEOUT,
                ) as r:
                    if r.status == 429:
                        return rate_limit("recovery 429")
                    text = await r.text()
            except Exception:  # noqa: BLE001 — keyingi endpointga o'tamiz
                continue

            # "ok" status + obfuscated/contact_point bo'lsagina FOUND.
            # v4.2 dagi "har qanday 'sent'/'success' matni → FOUND" kengroq edi;
            # obfuscated kontakt ko'rsatilgandagina ishonamiz.
            try:
                j = json.loads(text)
                if isinstance(j, dict) and j.get("status") == "ok" and (
                    "obfuscated" in text or j.get("contact_point")
                ):
                    return found("recovery: ok + obfuscated")
            except (json.JSONDecodeError, ValueError):
                pass
            if "No users found" in text or "no users found" in text.lower():
                return not_found("recovery: No users found")

        return unknown("aniq signal yo'q (endpoint o'zgargan bo'lishi mumkin)")
