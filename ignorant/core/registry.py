"""Tekshiruvchilar reyestri — barcha platforma modullarini bir joyga yig'adi.

`ignorant.modules` paketidan har bir `BaseChecker` nusxasini oladi va
nom/slug bo'yicha qidirish imkonini beradi. CLI va runner shu yerdan
platformalar ro'yxatini oladi.
"""

from __future__ import annotations

from ignorant.core.base import BaseChecker
from ignorant.modules import ALL_CHECKERS


def all_checkers() -> list[BaseChecker]:
    """Ro'yxatga olingan barcha tekshiruvchilar (tartib saqlanadi)."""
    return list(ALL_CHECKERS)


def by_slug() -> dict[str, BaseChecker]:
    """{slug: checker} — CLI `--only instagram,telegram` uchun."""
    return {c.slug: c for c in ALL_CHECKERS}


def by_name() -> dict[str, BaseChecker]:
    """{name: checker} — chiroyli nom bo'yicha qidirish uchun."""
    return {c.name: c for c in ALL_CHECKERS}


def resolve(selectors: list[str]) -> tuple[list[BaseChecker], list[str]]:
    """Foydalanuvchi bergan nom/slug ro'yxatini tekshiruvchilarga aylantiradi.

    Katta-kichik harf va nom/slug ikkisini ham qabul qiladi.

    Returns:
        (topilgan_checkerlar, nomalum_selektorlar)
    """
    slug_map = by_slug()
    name_map = {k.lower(): v for k, v in by_name().items()}

    found: list[BaseChecker] = []
    unknown: list[str] = []
    for sel in selectors:
        key = sel.strip().lower()
        if key in slug_map:
            found.append(slug_map[key])
        elif key in name_map:
            found.append(name_map[key])
        else:
            unknown.append(sel)
    return found, unknown
