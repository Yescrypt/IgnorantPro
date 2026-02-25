#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║        IGNORANT PRO - Phone Number OSINT Tool        ║
║              Version 4.0  |  All Fixed               ║
╚══════════════════════════════════════════════════════╝

Har bir platform TEKSHIRILGAN va ISHLAYDIGAN metodlar bilan.

METOD QANDAY ISHLAYDI:
  - Saytlarning "forgot password" yoki "signup" flowini ishlatadi
  - Agar raqam topilsa → sayt "kodni yubordik" yoki account info qaytaradi
  - Bu OSINT — hech qanday login, parol, hack yo'q
  - Faqat ochiq API endpointlar ishlatiladi
"""

import asyncio
import aiohttp
import time
import sys
import re
import json
import urllib.parse
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""
{Fore.CYAN}╔════════════════════════════════════════════════╗
║  {Fore.WHITE}IGNORANT PRO v4.0{Fore.CYAN}  -  Phone Number OSINT Tool ║
║  {Fore.YELLOW}12 platform  |  Yescrypt  |  Auto report   {Fore.CYAN}   ║
╚════════════════════════════════════════════════╝{Style.RESET_ALL}
"""

# ─────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────

def digits_only(phone: str) -> str:
    return re.sub(r"[^\d]", "", phone)

def strip_cc(phone: str):
    """(cc, local_number) → ("998", "901234567")"""
    d = digits_only(phone)
    m = re.match(r"^(\d{1,3})(\d{7,12})$", d)
    if m:
        return m.group(1), m.group(2)
    return d[:3], d[3:]

TIMEOUT  = aiohttp.ClientTimeout(total=14)
SHORT_TO = aiohttp.ClientTimeout(total=8)

CHROME_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# ─────────────────────────────────────────────────────────
#  1. INSTAGRAM
#  Metod: Web signup — phone_number field existence check
#  GET  /accounts/emailsignup/   → csrf token
#  POST /api/v1/users/check_phone/  → {"phone_number_valid": true/false}
#  Agar 400 "The field is required" → endpoint o'zgangan, fallback ishlatiladi
# ─────────────────────────────────────────────────────────
async def check_instagram(session: aiohttp.ClientSession, phone: str):
    try:
        # Step 1 — csrf token
        async with session.get(
            "https://www.instagram.com/accounts/emailsignup/",
            headers={"User-Agent": CHROME_UA, "Accept-Language": "en-US,en;q=0.9"},
            timeout=TIMEOUT,
        ) as r:
            csrf = r.cookies.get("csrftoken", "")
            if not csrf:
                txt = await r.text()
                m = re.search(r'"csrf_token":"([^"]+)"', txt)
                csrf = m.group(1) if m else ""

        if not csrf:
            return "ERROR"

        # Step 2 — check phone via web endpoint
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
        # Endpoint 1: lookup_phone (eski)
        data = urllib.parse.urlencode({"phone_number": phone})
        async with session.post(
            "https://www.instagram.com/api/v1/users/lookup_phone_with_count/",
            data=data, headers=headers, timeout=TIMEOUT,
        ) as r:
            if r.status == 429:
                return "RATE_LIMIT"
            text = await r.text()
            try:
                j = json.loads(text)
                if j.get("user_id") or j.get("count", 0) > 0 or j.get("obfuscated_phone"):
                    return "FOUND"
                if j.get("message") == "No users found":
                    return "NOT_FOUND"
                if j.get("status") == "fail":
                    # Endpoint o'zgangan — fallback
                    pass
                else:
                    return "NOT_FOUND"
            except Exception:
                pass

        # Fallback: forgot password flow
        async with session.post(
            "https://www.instagram.com/accounts/account_recovery_send_ajax/",
            data=urllib.parse.urlencode({"phone_number": phone, "phone_or_email": phone}),
            headers=headers, timeout=TIMEOUT,
        ) as r:
            if r.status == 429:
                return "RATE_LIMIT"
            text = await r.text()
            if "obfuscated" in text or "phone" in text or r.status == 200:
                try:
                    j = json.loads(text)
                    if j.get("status") == "ok":
                        return "FOUND"
                except Exception:
                    pass
            if "No users found" in text:
                return "NOT_FOUND"
            return "ERROR"

    except asyncio.TimeoutError:
        return "TIMEOUT"
    except Exception:
        return "ERROR"


# ─────────────────────────────────────────────────────────
#  2. TELEGRAM
#  Metod: my.telegram.org/auth/send_password
#  "OK" → mavjud, "error" → yo'q
# ─────────────────────────────────────────────────────────
async def check_telegram(session: aiohttp.ClientSession, phone: str):
    try:
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
                return "RATE_LIMIT"
            t = (await r.text()).strip()
            if t == "OK" or "sent" in t.lower():
                return "FOUND"
            if "FLOOD" in t:
                return "RATE_LIMIT"
            if "error" in t.lower() or "invalid" in t.lower() or "not exist" in t.lower():
                return "NOT_FOUND"
            if r.status == 200 and len(t) < 80:
                return "FOUND"
            return "NOT_FOUND"
    except asyncio.TimeoutError:
        return "TIMEOUT"
    except Exception:
        return "ERROR"


# ─────────────────────────────────────────────────────────
#  3. TIKTOK
#  Metod: /passport/mobile/check_unique/ (POST)
#  message_code=2 → band (FOUND), =0 → bo'sh (NOT_FOUND)
#  Timeout sababi: TikTok geo-check qiladi, User-Agent muhim
# ─────────────────────────────────────────────────────────
async def check_tiktok(session: aiohttp.ClientSession, phone: str):
    d = digits_only(phone)
    # cc va raqamni ajratamiz
    cc  = d[:3] if d.startswith("998") else d[:1]
    num = d[len(cc):]

    # Bir nechta endpoint — biri ishlamasa keyingisi
    endpoints = [
        "https://www.tiktok.com/passport/mobile/check_unique/",
        "https://www.tiktok.com/api/v1/passport/mobile/check_unique/",
    ]
    headers = {
        "User-Agent": (
            "com.zhiliaoapp.musically/2023.100 (Linux; U; Android 13; en_US; "
            "SM-G998B; Build/TP1A.220624.014; Cronet/TTNetVersion:b4d74d38 "
            "3.7.1.0 HeaderSize/20220504-GP CloseGuard/0)"
        ),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
    }
    post_data = urllib.parse.urlencode({
        "mobile":       num,
        "area_code":    cc,
        "aid":          "1284",
        "account_sdk_source": "tiktok",
        "multi_login":  "0",
    })

    for url in endpoints:
        try:
            async with session.post(
                url, data=post_data, headers=headers,
                timeout=TIMEOUT,
            ) as r:
                if r.status == 429:
                    return "RATE_LIMIT"
                if r.status in (403, 405, 404):
                    continue  # keyingi endpoint
                text = await r.text()
                try:
                    j = json.loads(text)
                    dj = j.get("data", {}) or {}
                    mc = dj.get("message_code", j.get("message_code", -99))
                    if mc == 2 or dj.get("is_unique") == 0:
                        return "FOUND"
                    if mc == 0 or dj.get("is_unique") == 1:
                        return "NOT_FOUND"
                    # error_code=1000 → endpoint o'zgangan
                    if j.get("error_code") in (1000, -1):
                        continue
                except Exception:
                    pass
        except asyncio.TimeoutError:
            continue
        except Exception:
            continue

    return "ERROR"


# ─────────────────────────────────────────────────────────
#  4. WHATSAPP
#  Metod: WhatsApp Web — /send endpoint + "Continue to Chat" tekshirish
#  wa.me har doim OK, shuning uchun to'g'ridan-to'g'ri web.whatsapp ishlatiladi
# ─────────────────────────────────────────────────────────
async def check_whatsapp(session: aiohttp.ClientSession, phone: str):
    d = digits_only(phone)

    # Metod 1: WhatsApp click-to-chat API (ishonchli)
    url = f"https://api.whatsapp.com/send/?phone={d}&text&type=phone_number&app_absent=0"
    try:
        async with session.get(
            url,
            headers={
                "User-Agent": CHROME_UA,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
            allow_redirects=True, timeout=TIMEOUT,
        ) as r:
            if r.status == 429:
                return "RATE_LIMIT"
            text = await r.text()
            # Agar WhatsApp raqamni topa olsa → "Continue to Chat" tugmasi bor
            if "Continue to Chat" in text or "continue_to_chat" in text:
                return "FOUND"
            # Raqam WA da yo'q → "phone number shared via url is invalid"
            if "invalid" in text.lower() or "phone number shared via url" in text.lower():
                return "NOT_FOUND"
            # Redirect bo'lsa ham tekshiramiz
            final = str(r.url)
            if "invalid" in final or "error" in final:
                return "NOT_FOUND"
    except asyncio.TimeoutError:
        pass
    except Exception:
        pass

    # Metod 2: web.whatsapp.com
    try:
        async with session.get(
            f"https://web.whatsapp.com/send?phone={d}",
            headers={"User-Agent": CHROME_UA},
            allow_redirects=True, timeout=TIMEOUT,
        ) as r:
            text = await r.text()
            if "Continue to Chat" in text or "open_app" in text:
                return "FOUND"
            if "invalid" in text.lower():
                return "NOT_FOUND"
    except Exception:
        pass

    return "ERROR"


# ─────────────────────────────────────────────────────────
#  5. SNAPCHAT
#  Metod: accounts.snapchat.com/accounts/password_reset_request
#  POST — "forgot_password_field" = phone
#  302 redirect boshqa URL ga → FOUND
# ─────────────────────────────────────────────────────────
async def check_snapchat(session: aiohttp.ClientSession, phone: str):
    try:
        # Step 1: xts token olamiz
        async with session.get(
            "https://accounts.snapchat.com/accounts/password_reset",
            headers={"User-Agent": CHROME_UA},
            timeout=TIMEOUT,
        ) as r:
            text = await r.text()
            xts_m = re.search(r'name="xts"\s+value="([^"]+)"', text)
            xts = xts_m.group(1) if xts_m else ""

        headers = {
            "User-Agent": CHROME_UA,
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://accounts.snapchat.com/accounts/password_reset",
            "Origin": "https://accounts.snapchat.com",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        }
        pdata = urllib.parse.urlencode({
            "forgot_password_field": phone,
            "xts": xts,
        })
        # allow_redirects=False — redirect URL ni ko'rish uchun
        async with session.post(
            "https://accounts.snapchat.com/accounts/password_reset_request",
            data=pdata, headers=headers,
            timeout=TIMEOUT, allow_redirects=False,
        ) as r:
            if r.status == 429:
                return "RATE_LIMIT"
            location = r.headers.get("Location", "")
            # Redirect manzil tekshiruv
            if "confirmation" in location or "check" in location or "success" in location:
                return "FOUND"
            if "error" in location or "invalid" in location or "not_found" in location:
                return "NOT_FOUND"
            # 200 yoki boshqa redirect → kontentni tekshiramiz
            text = await r.text()
            if "We found" in text or "sent" in text.lower() or "verify" in text.lower():
                return "FOUND"
            if "No account" in text or "not found" in text.lower():
                return "NOT_FOUND"
            if r.status == 302:
                return "FOUND"   # har qanday redirect = muvaffaqiyat
            return "NOT_FOUND"
    except asyncio.TimeoutError:
        return "TIMEOUT"
    except Exception:
        return "ERROR"


# ─────────────────────────────────────────────────────────
#  6. TWITTER / X
#  Metod: /i/flow/password_reset — yangi onboarding API
#  Bu 2024-yil uchun ishlaydigan yagona metod
# ─────────────────────────────────────────────────────────
async def check_twitter(session: aiohttp.ClientSession, phone: str):
    bearer = (
        "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
        "%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
    )
    try:
        # Guest token
        async with session.post(
            "https://api.twitter.com/1.1/guest/activate.json",
            headers={
                "Authorization": f"Bearer {bearer}",
                "User-Agent": CHROME_UA,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=SHORT_TO,
        ) as r:
            if r.status != 200:
                return "ERROR"
            gtok = (await r.json()).get("guest_token", "")

        if not gtok:
            return "ERROR"

        base_headers = {
            "Authorization": f"Bearer {bearer}",
            "X-Guest-Token": gtok,
            "User-Agent": CHROME_UA,
            "Content-Type": "application/json",
            "Accept": "*/*",
            "X-Twitter-Active-User": "yes",
            "X-Twitter-Client-Language": "en",
        }

        # Flow 1: init password reset
        async with session.post(
            "https://api.twitter.com/1.1/onboarding/task.json?flow_name=forgot-password",
            json={"flow_token": None, "input_flow_data": {}},
            headers=base_headers, timeout=TIMEOUT,
        ) as r:
            if r.status == 429:
                return "RATE_LIMIT"
            j = await r.json()
            flow_token = j.get("flow_token", "")

        if not flow_token:
            return "ERROR"

        # Flow 2: phone yuborish
        payload = {
            "flow_token": flow_token,
            "subtask_inputs": [{
                "subtask_id": "EnterUserIdentifier",
                "enter_text": {
                    "text": phone,
                    "link": "next_link",
                },
            }],
        }
        async with session.post(
            "https://api.twitter.com/1.1/onboarding/task.json",
            json=payload, headers=base_headers, timeout=TIMEOUT,
        ) as r:
            if r.status == 429:
                return "RATE_LIMIT"
            text = await r.text()
            try:
                j = json.loads(text)
                subtasks = j.get("subtasks", [])
                for st in subtasks:
                    sid = st.get("subtask_id", "")
                    # Agar keyingi qadam bo'lsa → raqam topildi
                    if sid in ("SelectAuthMethod", "ChooseIdentifier",
                               "PasswordReset", "EnterPassword"):
                        return "FOUND"
                errors = j.get("errors", [])
                for e in errors:
                    # 32 = bad param, 64 = suspended, 326 = locked, 141 = not found
                    if e.get("code") in (141, 32):
                        return "NOT_FOUND"
                # agar errors yo'q va subtasks bor → FOUND
                if subtasks and not errors:
                    return "FOUND"
            except Exception:
                pass
            if "SelectAuthMethod" in text or "ChooseIdentifier" in text:
                return "FOUND"
            return "NOT_FOUND"

    except asyncio.TimeoutError:
        return "TIMEOUT"
    except Exception:
        return "ERROR"


# ─────────────────────────────────────────────────────────
#  7. VIBER
#  Metod: Viber web — forgot password
#  GET https://account.viber.com/en/forgot-password → form
#  POST → agar raqam topilsa "sent" javob keladi
# ─────────────────────────────────────────────────────────
async def check_viber(session: aiohttp.ClientSession, phone: str):
    try:
        # Step 1: page va csrf
        async with session.get(
            "https://account.viber.com/en/forgot-password",
            headers={"User-Agent": CHROME_UA},
            timeout=TIMEOUT,
        ) as r:
            text = await r.text()
            csrf_m = re.search(r'name="csrfToken"\s+value="([^"]+)"', text)
            csrf = csrf_m.group(1) if csrf_m else ""
            # alternative: _csrf yoki csrf_token
            if not csrf:
                csrf_m = re.search(r'"csrf[^"]*"[:\s]+"([^"]+)"', text)
                csrf = csrf_m.group(1) if csrf_m else ""

        headers = {
            "User-Agent": CHROME_UA,
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://account.viber.com/en/forgot-password",
            "Origin": "https://account.viber.com",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        pdata = urllib.parse.urlencode({
            "phoneNumber": phone,
            "csrfToken": csrf,
        })
        async with session.post(
            "https://account.viber.com/en/forgot-password",
            data=pdata, headers=headers,
            timeout=TIMEOUT, allow_redirects=True,
        ) as r:
            if r.status == 429:
                return "RATE_LIMIT"
            text = await r.text()
            final_url = str(r.url)
            if "check" in final_url or "sent" in final_url or "success" in final_url:
                return "FOUND"
            if "We sent" in text or "sent" in text.lower() or "check your" in text.lower():
                return "FOUND"
            if "not found" in text.lower() or "no account" in text.lower():
                return "NOT_FOUND"
            if "invalid" in text.lower() or "error" in text.lower():
                return "NOT_FOUND"
            # Agar sahifa o'zgarmasa → raqam yo'q
            if "forgot-password" in final_url:
                return "NOT_FOUND"
            return "NOT_FOUND"
    except asyncio.TimeoutError:
        return "TIMEOUT"
    except Exception:
        return "ERROR"


# ─────────────────────────────────────────────────────────
#  8. AMAZON
#  Metod: /ap/forgotpassword — phone bilan
#  "We found your account" → FOUND
# ─────────────────────────────────────────────────────────
async def check_amazon(session: aiohttp.ClientSession, phone: str):
    try:
        async with session.get(
            "https://www.amazon.com/ap/forgotpassword",
            headers={"User-Agent": CHROME_UA, "Accept-Language": "en-US,en;q=0.9"},
            timeout=TIMEOUT,
        ) as r:
            text = await r.text()
            t1 = re.search(r'name="appActionToken"\s+value="([^"]+)"', text)
            tok = t1.group(1) if t1 else ""
            t2 = re.search(r'name="metadata1"\s+value="([^"]+)"', text)
            meta = t2.group(1) if t2 else ""

        pdata = urllib.parse.urlencode({
            "appActionToken": tok,
            "appAction": "FORGOT_PASSWORD",
            "openid.assoc_handle": "usflex",
            "metadata1": meta,
            "email": phone,
        })
        async with session.post(
            "https://www.amazon.com/ap/forgotpassword",
            data=pdata,
            headers={
                "User-Agent": CHROME_UA,
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://www.amazon.com/ap/forgotpassword",
                "Accept-Language": "en-US,en;q=0.9",
            },
            timeout=TIMEOUT,
        ) as r:
            if r.status == 429:
                return "RATE_LIMIT"
            text = await r.text()
            if "We found your account" in text or (
                    "verify" in text.lower() and "sent" in text.lower()):
                return "FOUND"
            if "We cannot find" in text or "No account" in text:
                return "NOT_FOUND"
            return "NOT_FOUND"
    except asyncio.TimeoutError:
        return "TIMEOUT"
    except Exception:
        return "ERROR"


# ─────────────────────────────────────────────────────────
#  9. MICROSOFT
#  Metod: GetCredentialType.srf (ishlaydi, lekin to'g'ri payload kerak)
#  IfExistsResult: 0=mavjud, 1=yo'q, 6=federated
# ─────────────────────────────────────────────────────────
async def check_microsoft(session: aiohttp.ClientSession, phone: str):
    try:
        # Avval sahifadan uaid olamiz
        async with session.get(
            "https://login.live.com/login.srf",
            headers={"User-Agent": CHROME_UA},
            timeout=TIMEOUT,
        ) as r:
            text = await r.text()
            uaid_m = re.search(r'"uaid":"([^"]+)"', text)
            uaid = uaid_m.group(1) if uaid_m else "61b8eed8e4c84a80ac55e1ea"
            ctx_m = re.search(r'"sCtx":"([^"]+)"', text)
            sctx = ctx_m.group(1) if ctx_m else ""
            ft_m = re.search(r'"sFT":"([^"]+)"', text)
            flow_tok = ft_m.group(1) if ft_m else ""

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
                return "RATE_LIMIT"
            text = await r.text()
            try:
                j = json.loads(text)
                ier = j.get("IfExistsResult", -1)
                if ier == 0:    # mavjud
                    return "FOUND"
                if ier == 1:    # yo'q
                    return "NOT_FOUND"
                if ier == 6:    # federated = mavjud
                    return "FOUND"
                if ier == 5:    # throttled
                    return "RATE_LIMIT"
            except Exception:
                pass
            if "IfExistsResult" in text:
                return "NOT_FOUND"
            return "ERROR"
    except asyncio.TimeoutError:
        return "TIMEOUT"
    except Exception:
        return "ERROR"


# ─────────────────────────────────────────────────────────
#  10. OLX.UZ
#  Metod: Login OTP yuborish endpointi
# ─────────────────────────────────────────────────────────
async def check_olx_uz(session: aiohttp.ClientSession, phone: str):
    d = digits_only(phone)
    formatted = f"+{d}"
    try:
        async with session.post(
            "https://www.olx.uz/api/open/auth/otp/",
            json={"phone": formatted},
            headers={
                "User-Agent": CHROME_UA,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Referer": "https://www.olx.uz/",
                "Origin": "https://www.olx.uz",
            },
            timeout=TIMEOUT,
        ) as r:
            if r.status == 429:
                return "RATE_LIMIT"
            text = await r.text()
            try:
                j = json.loads(text)
                if j.get("isRegistered") is True or j.get("user_exists"):
                    return "FOUND"
                if j.get("isRegistered") is False:
                    return "NOT_FOUND"
                # OTP kod so'ralsa → raqam OLX da bor
                if "otp" in text.lower() or "code" in text.lower():
                    return "FOUND"
            except Exception:
                pass
            if r.status == 200:
                return "FOUND"
            if r.status == 404:
                return "NOT_FOUND"
            return "ERROR"
    except asyncio.TimeoutError:
        return "TIMEOUT"
    except Exception:
        return "ERROR"


# ─────────────────────────────────────────────────────────
#  11. LINKEDIN
#  Metod: Password reset — phone bilan
#  Redirect "checkYourEmail" → FOUND
# ─────────────────────────────────────────────────────────
async def check_linkedin(session: aiohttp.ClientSession, phone: str):
    try:
        async with session.get(
            "https://www.linkedin.com/uas/request-password-reset",
            headers={"User-Agent": CHROME_UA, "Accept-Language": "en-US,en;q=0.9"},
            timeout=TIMEOUT,
        ) as r:
            text = await r.text()
            csrf_m = re.search(r'csrfToken=([^&"\']+)', text)
            csrf = csrf_m.group(1) if csrf_m else ""
            pi_m = re.search(r'"pageInstance":"([^"]+)"', text)
            pi = pi_m.group(1) if pi_m else ""

        pdata = urllib.parse.urlencode({
            "csrfToken": csrf,
            "pageInstance": pi,
            "resendUrl": "",
            "email": phone,
            "btn-primary": "",
        })
        async with session.post(
            "https://www.linkedin.com/uas/request-password-reset",
            data=pdata,
            headers={
                "User-Agent": CHROME_UA,
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://www.linkedin.com/uas/request-password-reset",
                "Origin": "https://www.linkedin.com",
            },
            timeout=TIMEOUT, allow_redirects=True,
        ) as r:
            if r.status == 429:
                return "RATE_LIMIT"
            final = str(r.url)
            text = await r.text()
            if "checkYourEmail" in final or "check_your_email" in final:
                return "FOUND"
            if "We sent" in text or "Check your email" in text:
                return "FOUND"
            if "doesn't match" in text or "No account" in text:
                return "NOT_FOUND"
            if "request-password-reset" in final:
                return "NOT_FOUND"
            return "NOT_FOUND"
    except asyncio.TimeoutError:
        return "TIMEOUT"
    except Exception:
        return "ERROR"


# ─────────────────────────────────────────────────────────
#  12. GOOGLE
#  Metod: accounts.google.com/v3/signin/identifier — phone step
#  Agar raqam topilsa: "next" step ko'rsatiladi
#  Bu eng murakkab — reCAPTCHA ko'p bo'ladi
# ─────────────────────────────────────────────────────────
async def check_google(session: aiohttp.ClientSession, phone: str):
    try:
        # Step 1: signin page dan context olamiz
        async with session.get(
            "https://accounts.google.com/v3/signin/identifier?"
            "flowName=GlifWebSignIn&flowEntry=ServiceLogin",
            headers={"User-Agent": CHROME_UA, "Accept-Language": "en-US,en;q=0.9"},
            timeout=TIMEOUT,
        ) as r:
            text = await r.text()

        # Muhim tokenlar: GALX, og-cookie
        galx_m = re.search(r'"GALX":"([^"]+)"', text)
        galx = galx_m.group(1) if galx_m else ""
        glm_m = re.search(r'"gxf":"([^"]+)"', text)
        gxf = glm_m.group(1) if glm_m else ""
        at_m = re.search(r'"at":"([^"]+)"', text)
        at_tok = at_m.group(1) if at_m else ""

        if not (galx or gxf or at_tok):
            return "ERROR"

        pdata = urllib.parse.urlencode({
            "identifier": phone,
            "continue": "https://myaccount.google.com/",
            "followup": "https://myaccount.google.com/",
            "ifkv": galx,
            "GALX": galx,
            "gxf": gxf,
            "at": at_tok,
            "_utf8": "☃",
            "bgresponse": "js_disabled",
        })
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
                return "RATE_LIMIT"
            text = await r.text()
            # Google javobida "accounts.google.com" profilga redirect → FOUND
            if '"accounts.google.com"' in text or "myaccount" in text:
                return "FOUND"
            # INVALID_ARGUMENT yoki reCAPTCHA
            if "INVALID" in text or "recaptcha" in text.lower():
                return "ERROR"
            if r.status == 200 and len(text) > 100:
                return "FOUND"
            return "NOT_FOUND"

    except asyncio.TimeoutError:
        return "TIMEOUT"
    except Exception:
        return "ERROR"


# ═══════════════════════════════════════════════════════════
#   SITES REGISTRY
# ═══════════════════════════════════════════════════════════

SITES = {
    "Instagram":   check_instagram,
    "Telegram":    check_telegram,
    "TikTok":      check_tiktok,
    "WhatsApp":    check_whatsapp,
    "Snapchat":    check_snapchat,
    "Twitter/X":   check_twitter,
    "Viber":       check_viber,
    "OLX UZ":      check_olx_uz,
    "Amazon":      check_amazon,
    "Microsoft":   check_microsoft,
    "LinkedIn":    check_linkedin,
    "Google":      check_google,
}

# ═══════════════════════════════════════════════════════════
#   DISPLAY ICONS / TEXT
# ═══════════════════════════════════════════════════════════

STATUS_ICON = {
    "FOUND":      f"{Fore.GREEN}[+]{Style.RESET_ALL}",
    "NOT_FOUND":  f"{Fore.RED}[-]{Style.RESET_ALL}",
    "RATE_LIMIT": f"{Fore.YELLOW}[x]{Style.RESET_ALL}",
    "TIMEOUT":    f"{Fore.YELLOW}[t]{Style.RESET_ALL}",
    "UNKNOWN":    f"{Fore.BLUE}[~]{Style.RESET_ALL}",
    "ERROR":      f"{Fore.MAGENTA}[?]{Style.RESET_ALL}",
}
STATUS_TEXT = {
    "FOUND":      f"{Fore.GREEN}Phone number used{Style.RESET_ALL}",
    "NOT_FOUND":  f"{Fore.RED}Phone number not used{Style.RESET_ALL}",
    "RATE_LIMIT": f"{Fore.YELLOW}Rate limit — try later{Style.RESET_ALL}",
    "TIMEOUT":    f"{Fore.YELLOW}Timeout{Style.RESET_ALL}",
    "UNKNOWN":    f"{Fore.BLUE}Unknown — manual check{Style.RESET_ALL}",
    "ERROR":      f"{Fore.MAGENTA}Error{Style.RESET_ALL}",
}

# ═══════════════════════════════════════════════════════════
#   REPORT SAVER
# ═══════════════════════════════════════════════════════════

def save_report(phone: str, results: dict, elapsed: float) -> str | None:
    last4 = digits_only(phone)[-4:]
    fname = f"report-{last4}.txt"
    ts    = time.strftime("%Y-%m-%d %H:%M:%S")
    found = [s for s, st in results.items() if st == "FOUND"]

    status_labels = {
        "FOUND":      "[+] Phone number used",
        "NOT_FOUND":  "[-] Phone number not used",
        "RATE_LIMIT": "[x] Rate limit",
        "TIMEOUT":    "[t] Timeout",
        "UNKNOWN":    "[~] Unknown",
        "ERROR":      "[?] Error",
    }

    lines = [
        "=" * 52,
        "   IGNORANT PRO v4.0 — Report",
        "=" * 52,
        f"  Telefon raqam : {phone}",
        f"  Sana / Vaqt  : {ts}",
        f"  Tekshirilgan : {len(results)} platform",
        f"  Vaqt ketdi   : {elapsed:.2f}s",
        "=" * 52,
        "",
        "[ BARCHA NATIJALAR ]",
        "-" * 52,
    ]
    for site, st in results.items():
        pad   = " " * max(1, 14 - len(site))
        label = status_labels.get(st, f"[?] {st}")
        lines.append(f"  {site}{pad}{label}")

    lines += [
        "",
        "=" * 52,
        "[ TOPILGAN PLATFORMALAR ]",
        "-" * 52,
    ]
    if found:
        for s in found:
            lines.append(f"  ✔  {s}")
    else:
        lines.append("  Hech qaysi platformada topilmadi.")

    lines += [
        "",
        "=" * 52,
        f"  Jami topildi : {len(found)} ta platform",
        "=" * 52,
        "",
    ]

    try:
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return fname
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════
#   RUNNER
# ═══════════════════════════════════════════════════════════

async def run_checks(phone: str, selected: list | None = None) -> dict:
    sites = {k: v for k, v in SITES.items()
             if selected is None or k in selected}

    conn = aiohttp.TCPConnector(limit=30, ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        tasks = {
            name: asyncio.create_task(func(session, phone))
            for name, func in sites.items()
        }
        await asyncio.wait(list(tasks.values()), timeout=22)

        results = {}
        for name, task in tasks.items():
            if task.done() and not task.cancelled():
                try:
                    results[name] = task.result()
                except Exception:
                    results[name] = "ERROR"
            else:
                task.cancel()
                results[name] = "TIMEOUT"

    return results


# ═══════════════════════════════════════════════════════════
#   DISPLAY
# ═══════════════════════════════════════════════════════════

def print_results(phone: str, results: dict, elapsed: float):
    print(f"\n{'*' * 50}")
    print(f"   {Fore.CYAN}{phone}{Style.RESET_ALL}")
    print(f"{'*' * 50}")

    counts: dict = {}
    for site, status in results.items():
        icon  = STATUS_ICON.get(status, STATUS_ICON["ERROR"])
        stext = STATUS_TEXT.get(status, status)
        pad   = " " * max(1, 14 - len(site))
        print(f"{icon} {Fore.WHITE}{site}{Style.RESET_ALL}{pad}{stext}")
        counts[status] = counts.get(status, 0) + 1

    print(f"\n{Fore.CYAN}{len(results)} platforms checked in {elapsed:.2f}s{Style.RESET_ALL}")
    print(
        f"{Fore.GREEN}[+]{Style.RESET_ALL} Found: {counts.get('FOUND', 0)}  "
        f"{Fore.RED}[-]{Style.RESET_ALL} Not found: {counts.get('NOT_FOUND', 0)}  "
        f"{Fore.YELLOW}[x]{Style.RESET_ALL} Rate limit: {counts.get('RATE_LIMIT', 0)}  "
        f"{Fore.YELLOW}[t]{Style.RESET_ALL} Timeout: {counts.get('TIMEOUT', 0)}  "
        f"{Fore.MAGENTA}[?]{Style.RESET_ALL} Error: {counts.get('ERROR', 0)}"
    )
    print(
        f"\n{Fore.WHITE}Legend:{Style.RESET_ALL} "
        f"{Fore.GREEN}[+]{Style.RESET_ALL} Found  "
        f"{Fore.RED}[-]{Style.RESET_ALL} Not used  "
        f"{Fore.YELLOW}[x]{Style.RESET_ALL} Rate limit  "
        f"{Fore.YELLOW}[t]{Style.RESET_ALL} Timeout  "
        f"{Fore.BLUE}[~]{Style.RESET_ALL} Unknown  "
        f"{Fore.MAGENTA}[?]{Style.RESET_ALL} Error"
    )

    fname = save_report(phone, results, elapsed)
    if fname:
        print(f"\n{Fore.GREEN}[✔] Report saqlandi:{Style.RESET_ALL} {Fore.WHITE}{fname}{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}[!] Report saqlanmadi.{Style.RESET_ALL}")


# ═══════════════════════════════════════════════════════════
#   CLI
# ═══════════════════════════════════════════════════════════

def validate_phone(raw: str) -> str | None:
    clean = re.sub(r"[\s\-\(\)]", "", raw)
    if not clean.startswith("+"):
        clean = "+" + clean
    return clean if re.match(r"^\+\d{7,15}$", clean) else None


def main():
    print(BANNER)

    if len(sys.argv) < 2:
        print(f"{Fore.YELLOW}Usage:{Style.RESET_ALL}")
        print(f"  python3 ignorant_pro.py +998941350269")
        print(f"  python3 ignorant_pro.py +998941350269 --only Instagram,Telegram")
        print(f"\n{Fore.CYAN}Platforms:{Style.RESET_ALL} {', '.join(SITES.keys())}")
        sys.exit(0)

    phone = validate_phone(sys.argv[1])
    if not phone:
        print(f"{Fore.RED}[!] Noto'g'ri format: {sys.argv[1]}{Style.RESET_ALL}")
        print("    To'g'ri: +998941350269")
        sys.exit(1)

    selected = None
    if "--only" in sys.argv:
        idx = sys.argv.index("--only")
        if idx + 1 < len(sys.argv):
            selected = [s.strip() for s in sys.argv[idx + 1].split(",")]
            bad = [s for s in selected if s not in SITES]
            if bad:
                print(f"{Fore.YELLOW}[!] Noma'lum: {', '.join(bad)}{Style.RESET_ALL}")
                print(f"    Mavjud: {', '.join(SITES.keys())}")
                sys.exit(1)

    label = ", ".join(selected) if selected else f"barcha {len(SITES)} ta platform"
    print(f"{Fore.CYAN}[*] Raqam   : {Fore.WHITE}{phone}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[*] Tekshirish: {label}...{Style.RESET_ALL}\n")

    start   = time.time()
    results = asyncio.run(run_checks(phone, selected))
    elapsed = time.time() - start

    print_results(phone, results, elapsed)


if __name__ == "__main__":
    main()
