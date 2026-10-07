"""Modul-darajali testlar — tarmoqsiz, soxta javoblar bilan.

Asosiy e'tibor: eski kodda bo'lgan XAVFLI catch-all'lar qaytib kelmaganini
isbotlash (false-positive / false-negative regressiyalari).
"""

from __future__ import annotations

import asyncio

from ignorant.core.base import Result
from ignorant.modules.instagram import InstagramChecker
from ignorant.modules.linkedin import LinkedInChecker
from ignorant.modules.microsoft import MicrosoftChecker
from ignorant.modules.olx_uz import OlxUzChecker
from ignorant.modules.snapchat import SnapchatChecker
from ignorant.modules.telegram import TelegramChecker
from ignorant.modules.whatsapp import WhatsAppChecker
from tests.fakes import FakeResponse, FakeSession

PHONE = "+998901234567"


def run(checker, session) -> Result:
    return asyncio.run(checker.check(session, PHONE)).result


# ─── Microsoft: IfExistsResult oracle ───────────────────────────────
def _ms_session(if_exists) -> FakeSession:
    login_html = '"uaid":"u1","sCtx":"c1","sFT":"f1"'
    body = '{"IfExistsResult": %s}' % if_exists
    return FakeSession([FakeResponse(200, login_html), FakeResponse(200, body)])


def test_microsoft_found():
    assert run(MicrosoftChecker(), _ms_session(0)) is Result.FOUND


def test_microsoft_not_found():
    assert run(MicrosoftChecker(), _ms_session(1)) is Result.NOT_FOUND


def test_microsoft_throttled():
    assert run(MicrosoftChecker(), _ms_session(5)) is Result.RATE_LIMIT


def test_microsoft_unknown():
    assert run(MicrosoftChecker(), _ms_session(99)) is Result.UNKNOWN


def test_microsoft_errorhr_is_error():
    # v4.2 fix: ErrorHR bo'lsa → ERROR
    s = FakeSession([
        FakeResponse(200, '"uaid":"u1"'),
        FakeResponse(200, '{"ErrorHR": 80049217}'),
    ])
    assert run(MicrosoftChecker(), s) is Result.ERROR


# ─── Instagram / LinkedIn: API-down va anti-bot aniqlash ────────────
def test_instagram_500_is_error():
    # v4.2 fix: GET 500 → API down → ERROR
    s = FakeSession([FakeResponse(500, "")])
    assert run(InstagramChecker(), s) is Result.ERROR


def test_linkedin_999_is_error():
    # v4.2 fix: status 999 → anti-bot → ERROR
    s = FakeSession([FakeResponse(999, "")])
    assert run(LinkedInChecker(), s) is Result.ERROR


# ─── Telegram: "OK" oracle, regression tekshiruvi ───────────────────
def test_telegram_found():
    s = FakeSession([FakeResponse(200, "OK")])
    assert run(TelegramChecker(), s) is Result.FOUND


def test_telegram_invalid_not_found():
    s = FakeSession([FakeResponse(200, "Invalid phone number")])
    assert run(TelegramChecker(), s) is Result.NOT_FOUND


def test_telegram_weird_short_is_unknown_not_found():
    # REGRESSIYA: eski kod status==200 va qisqa javobni FOUND derdi.
    s = FakeSession([FakeResponse(200, "xyz")])
    assert run(TelegramChecker(), s) is Result.UNKNOWN


def test_telegram_json_random_hash_found():
    # v4.2 fix: JSON {"random_hash": ...} → FOUND
    s = FakeSession([FakeResponse(200, '{"random_hash": "abc123"}')])
    assert run(TelegramChecker(), s) is Result.FOUND


def test_telegram_json_error_message_not_found():
    # v4.2 fix: JSON {"error_message": ...} → NOT_FOUND
    s = FakeSession([FakeResponse(200, '{"error_message": "Invalid phone"}')])
    assert run(TelegramChecker(), s) is Result.NOT_FOUND


# ─── WhatsApp: hech qachon FOUND bermasligi kerak ───────────────────
def test_whatsapp_generic_page_is_unknown():
    # REGRESSIYA: eski kod "Continue to Chat" sahifasini FOUND derdi.
    s = FakeSession([FakeResponse(200, "<html>Continue to Chat</html>")])
    assert run(WhatsAppChecker(), s) is Result.UNKNOWN


def test_whatsapp_invalid_is_not_found():
    s = FakeSession([FakeResponse(200, "phone number shared via url is invalid")])
    assert run(WhatsAppChecker(), s) is Result.NOT_FOUND


# ─── OLX: isRegistered oracle, regression ───────────────────────────
def test_olx_registered():
    s = FakeSession([FakeResponse(200, '{"isRegistered": true}')])
    assert run(OlxUzChecker(), s) is Result.FOUND


def test_olx_not_registered():
    s = FakeSession([FakeResponse(200, '{"isRegistered": false}')])
    assert run(OlxUzChecker(), s) is Result.NOT_FOUND


def test_olx_200_without_field_is_unknown():
    # REGRESSIYA: eski kod har qanday 200 ni FOUND derdi.
    s = FakeSession([FakeResponse(200, '{"status": "ok"}')])
    assert run(OlxUzChecker(), s) is Result.UNKNOWN


# ─── Snapchat: neytral 302 FOUND bo'lmasligi kerak ──────────────────
def test_snapchat_neutral_redirect_is_unknown():
    # REGRESSIYA: eski kod har qanday 302 ni FOUND derdi.
    s = FakeSession([
        FakeResponse(200, '<input name="xts" value="x1">'),
        FakeResponse(302, "", headers={"Location": "https://accounts.snapchat.com/next"}),
    ])
    assert run(SnapchatChecker(), s) is Result.UNKNOWN


# ─── safe_check: istisnolarni Outcome ga aylantiradi ────────────────
def test_safe_check_wraps_exception():
    class Boom(SnapchatChecker):
        async def check(self, session, phone):
            raise ValueError("boom")

    out = asyncio.run(Boom().safe_check(None, PHONE))
    assert out.result is Result.ERROR
    assert "boom" in out.note


def test_safe_check_wraps_timeout():
    class Slow(SnapchatChecker):
        async def check(self, session, phone):
            raise asyncio.TimeoutError

    out = asyncio.run(Slow().safe_check(None, PHONE))
    assert out.result is Result.TIMEOUT
