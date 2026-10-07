"""Asinxron runner — tanlangan tekshiruvchilarni parallel ishga tushiradi.

Har bir tekshiruvchi `safe_check()` orqali chaqiriladi, shuning uchun bitta
platformaning xatosi boshqalarga ta'sir qilmaydi. Umumiy deadline bor —
sekin platformalar TIMEOUT sifatida belgilanadi.
"""

from __future__ import annotations

import asyncio

from ignorant.core.base import BaseChecker, Outcome, Result
from ignorant.core.http import make_session

# Butun jarayon uchun qattiq deadline (sekund). Modul timeoutidan biroz katta.
GLOBAL_DEADLINE = 22


async def run_checks(
    phone: str,
    checkers: list[BaseChecker],
    deadline: int = GLOBAL_DEADLINE,
) -> dict[str, Outcome]:
    """Barcha tekshiruvchilarni parallel ishga tushiradi.

    Args:
        phone:    E.164 formatdagi raqam.
        checkers: ishga tushiriladigan tekshiruvchilar ro'yxati.
        deadline: butun jarayon uchun maksimal vaqt (sekund).

    Returns:
        {platforma_nomi: Outcome} — tartib `checkers` bilan bir xil.
    """
    async with make_session() as session:
        tasks: dict[str, asyncio.Task] = {
            c.name: asyncio.create_task(c.safe_check(session, phone))
            for c in checkers
        }
        if tasks:
            await asyncio.wait(tasks.values(), timeout=deadline)

        results: dict[str, Outcome] = {}
        for name, task in tasks.items():
            if task.done() and not task.cancelled():
                try:
                    results[name] = task.result()
                except Exception as exc:  # noqa: BLE001
                    results[name] = Outcome(Result.ERROR, str(exc))
            else:
                task.cancel()
                results[name] = Outcome(Result.TIMEOUT, "global deadline")

        # Bekor qilingan tasklarni toza yig'ishtirish.
        pending = [t for t in tasks.values() if not t.done()]
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)

    return results
