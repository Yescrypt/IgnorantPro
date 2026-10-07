"""HTTP sessiya fabrikasi va umumiy sozlamalar.

Butun loyiha bitta `aiohttp.ClientSession` ni baham ko'radi — bu ulanishlarni
qayta ishlatadi va tezlashtiradi. Bu yerda timeout, User-Agent va connector
sozlamalari bir joyda saqlanadi.
"""

from __future__ import annotations

import aiohttp

# Umumiy timeoutlar. Platformalar sekin bo'lishi mumkin, lekin cheksiz kutmaymiz.
TIMEOUT = aiohttp.ClientTimeout(total=14)
SHORT_TIMEOUT = aiohttp.ClientTimeout(total=8)

# Zamonaviy Chrome User-Agent — ko'p sayt eski/bo'sh UA ni bloklaydi.
CHROME_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# Standart brauzerga o'xshash sarlavhalar.
DEFAULT_HEADERS = {
    "User-Agent": CHROME_UA,
    "Accept-Language": "en-US,en;q=0.9",
}


def make_session() -> aiohttp.ClientSession:
    """Loyiha sozlamalari bilan yangi `aiohttp.ClientSession` yaratadi.

    Eslatma: eski kodda `ssl=False` ishlatilgan edi — bu sertifikat
    tekshiruvini butunlay o'chiradi (MITM xavfi). Bu yerda standart SSL
    tekshiruvi yoqilgan holicha qoldirilgan; agar ba'zi platforma sertifikat
    muammosi bersa, buni modul darajasida hal qilish kerak, global emas.
    """
    connector = aiohttp.TCPConnector(limit=30, ttl_dns_cache=300)
    return aiohttp.ClientSession(
        connector=connector,
        headers=DEFAULT_HEADERS,
        timeout=TIMEOUT,
    )
