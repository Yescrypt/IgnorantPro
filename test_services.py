#!/usr/bin/env python3
"""Jonli debug skripti — alohida platformalarni real tarmoqda sinash.

DIQQAT: bu avtomatik (pytest) test EMAS — u haqiqiy so'rov yuboradi.
Avtomatik, tarmoqsiz testlar uchun: `pytest -q` (tests/ papkasi).

Foydalanish:
    python3 test_services.py                      # barcha platforma, default raqamlar
    python3 test_services.py +998901234567        # bitta raqam
    python3 test_services.py +998901234567 telegram olx_uz

Faqat o'zingizga tegishli yoki ruxsat berilgan raqamlarni sinang.
"""

from __future__ import annotations

import asyncio
import sys

from ignorant.core import registry
from ignorant.core.http import make_session
from ignorant.utils.phone import validate_phone

DEFAULT_PHONES = ["+998901234567"]


async def _debug(phones: list[str], slugs: list[str]) -> None:
    checkers, unknown = (registry.resolve(slugs) if slugs
                         else (registry.all_checkers(), []))
    if unknown:
        print(f"[!] Noma'lum platforma: {', '.join(unknown)}")
        return

    async with make_session() as session:
        for phone in phones:
            print(f"\n{'=' * 50}\nTesting: {phone}\n{'=' * 50}")
            for c in checkers:
                print(f"► {c.name:12}", end=" ", flush=True)
                outcome = await c.safe_check(session, phone)
                print(outcome)


def main() -> None:
    args = sys.argv[1:]
    phones, slugs = [], []
    for a in args:
        norm = validate_phone(a)
        (phones if norm else slugs).append(norm or a)
    asyncio.run(_debug(phones or DEFAULT_PHONES, slugs))


if __name__ == "__main__":
    main()
