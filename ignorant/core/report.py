"""Tekshiruv natijalarini matnli fayl hisobotiga saqlash."""

from __future__ import annotations

import time

from ignorant.core.base import Outcome, Result
from ignorant.utils.phone import digits_only

STATUS_LABELS = {
    Result.FOUND:      "[+] Phone number used",
    Result.NOT_FOUND:  "[-] Phone number not used",
    Result.UNKNOWN:    "[~] Unknown — manual check",
    Result.RATE_LIMIT: "[x] Rate limit",
    Result.TIMEOUT:    "[t] Timeout",
    Result.ERROR:      "[?] Error",
}


def save_report(phone: str, results: dict[str, Outcome], elapsed: float) -> str | None:
    """Natijalarni `report-XXXX.txt` fayliga yozadi (XXXX = raqamning oxirgi 4).

    Returns:
        Fayl nomi, yoki saqlashda xato bo'lsa None.
    """
    last4 = digits_only(phone)[-4:]
    fname = f"report-{last4}.txt"
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    found = [s for s, o in results.items() if o.result is Result.FOUND]

    lines = [
        "=" * 52,
        "   IGNORANT PRO — Report",
        "=" * 52,
        f"  Telefon raqam : {phone}",
        f"  Sana / Vaqt   : {ts}",
        f"  Tekshirilgan  : {len(results)} platform",
        f"  Vaqt ketdi    : {elapsed:.2f}s",
        "=" * 52,
        "",
        "[ BARCHA NATIJALAR ]",
        "-" * 52,
    ]
    for site, outcome in results.items():
        pad = " " * max(1, 14 - len(site))
        label = STATUS_LABELS.get(outcome.result, f"[?] {outcome.result}")
        note = f"  — {outcome.note}" if outcome.note else ""
        lines.append(f"  {site}{pad}{label}{note}")

    lines += ["", "=" * 52, "[ TOPILGAN PLATFORMALAR ]", "-" * 52]
    if found:
        lines += [f"  ✔  {s}" for s in found]
    else:
        lines.append("  Hech qaysi platformada aniq topilmadi.")

    lines += [
        "",
        "=" * 52,
        f"  Jami topildi : {len(found)} ta platform",
        "=" * 52,
        "",
    ]

    try:
        with open(fname, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        return fname
    except OSError:
        return None
