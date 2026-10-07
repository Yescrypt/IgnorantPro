"""Asosiy tiplar va har bir platforma tekshiruvchisi uchun umumiy shartnoma.

Bu modul butun loyihaning markaziy abstraksiyasi: `Result`, `Outcome` va
`BaseChecker`. Har bir platforma moduli `BaseChecker` dan meros oladi va
faqat bitta narsani biladi — o'z platformasini qanday so'roq qilish.

Dizayn qoidasi (eng muhimi):
    Tekshiruvchi HECH QACHON "catch-all → FOUND/NOT_FOUND" qilmaydi.
    Agar signal aniq bo'lmasa — `Result.UNKNOWN` qaytariladi.
    Noto'g'ri "bor/yo'q" javobdan ko'ra halol "bilmayman" afzal.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum


class Result(str, Enum):
    """Bitta platforma tekshiruvining yakuniy holati.

    `str` dan meros olingani uchun to'g'ridan-to'g'ri satr sifatida ham
    ishlatish mumkin (masalan, dict kalit yoki JSON seriyalashda).
    """

    FOUND = "FOUND"            # Raqam platformada ro'yxatdan o'tgan
    NOT_FOUND = "NOT_FOUND"    # Raqam platformada yo'q
    UNKNOWN = "UNKNOWN"        # Oracle aniq javob bermadi (ishonchsiz)
    RATE_LIMIT = "RATE_LIMIT"  # Platforma so'rovlarni cheklab qo'ydi
    TIMEOUT = "TIMEOUT"        # Vaqt tugadi
    ERROR = "ERROR"            # Kutilmagan xato / endpoint o'zgargan

    def __str__(self) -> str:  # chiroyli chop etish uchun
        return self.value


@dataclass(slots=True)
class Outcome:
    """Tekshiruv natijasi + ixtiyoriy tushuntirish matni.

    `note` — nega aynan shu natija chiqqanini tushuntiradi (masalan,
    "IfExistsResult=0" yoki "endpoint 404"). Report va debug uchun qulay.
    """

    result: Result
    note: str = ""

    def __str__(self) -> str:
        return f"{self.result}" + (f" ({self.note})" if self.note else "")


# Qisqa yordamchi konstruktorlar — modullarda kodni toza qiladi.
def found(note: str = "") -> Outcome:
    return Outcome(Result.FOUND, note)


def not_found(note: str = "") -> Outcome:
    return Outcome(Result.NOT_FOUND, note)


def unknown(note: str = "") -> Outcome:
    return Outcome(Result.UNKNOWN, note)


def rate_limit(note: str = "") -> Outcome:
    return Outcome(Result.RATE_LIMIT, note)


def error(note: str = "") -> Outcome:
    return Outcome(Result.ERROR, note)


class BaseChecker:
    """Har bir platforma moduli shu klassdan meros oladi.

    Atributlar:
        name:     Chiroyli nom, UI/hisobotda ko'rinadi (masalan "Instagram").
        slug:     Mashina uchun qisqa id (masalan "instagram"). CLI `--only`.
        reliable: Platforma ishonchli "bor/yo'q" oracle beradimi?
                  False bo'lsa — platforma enumeration-hardened, natijalariga
                  ehtiyotkorlik bilan qarash kerak (UI buni belgilab ko'rsatadi).
        status:   2024-12 empirik kuzatuv yorlig'i (masalan "✅ WORKING",
                  "⚠️ RATE_LIMITED", "❌ API_DOWN"). Bo'sh bo'lsa noma'lum.
        phone_hint: Raqam qanday formatda kutilishi haqida eslatma.
    """

    name: str = "Base"
    slug: str = "base"
    reliable: bool = True
    status: str = ""
    phone_hint: str = "E.164, masalan +998901234567"

    async def check(self, session, phone: str) -> Outcome:
        """Platformani so'roq qiladi. Modul shu metodni qayta yozadi.

        Args:
            session: ochiq `aiohttp.ClientSession`.
            phone:   E.164 formatdagi raqam, masalan "+998901234567".

        Returns:
            Outcome — natija va ixtiyoriy izoh.
        """
        raise NotImplementedError

    async def safe_check(self, session, phone: str) -> Outcome:
        """`check()` ni o'rab, barcha istisnolarni Outcome ga aylantiradi.

        Runner aynan shu metodni chaqiradi — shuning uchun bitta modulning
        yiqilishi butun jarayonni to'xtatmaydi.
        """
        try:
            return await self.check(session, phone)
        except asyncio.TimeoutError:
            return Outcome(Result.TIMEOUT, "so'rov vaqti tugadi")
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 — har qanday xatoni ERROR qilamiz
            return Outcome(Result.ERROR, f"{type(exc).__name__}: {exc}")
