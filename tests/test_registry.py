"""Reyestr va umumiy modul shartnomasi testlari."""

from __future__ import annotations

from ignorant.core import registry
from ignorant.core.base import BaseChecker


def test_twelve_checkers():
    assert len(registry.all_checkers()) == 12


def test_slugs_unique_and_nonempty():
    slugs = [c.slug for c in registry.all_checkers()]
    assert all(slugs)
    assert len(slugs) == len(set(slugs))


def test_names_unique():
    names = [c.name for c in registry.all_checkers()]
    assert len(names) == len(set(names))


def test_all_inherit_base():
    assert all(isinstance(c, BaseChecker) for c in registry.all_checkers())


def test_resolve_by_slug_and_name():
    found, unknown = registry.resolve(["instagram", "Telegram", "OLX UZ"])
    assert unknown == []
    assert {c.slug for c in found} == {"instagram", "telegram", "olx_uz"}


def test_resolve_unknown():
    found, unknown = registry.resolve(["instagram", "facebook"])
    assert [c.slug for c in found] == ["instagram"]
    assert unknown == ["facebook"]
