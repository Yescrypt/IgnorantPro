"""Telefon raqam yordamchilarining testlari."""

from __future__ import annotations

import pytest

from ignorant.utils.phone import digits_only, split_cc, to_e164, validate_phone


def test_digits_only():
    assert digits_only("+998 (90) 123-45-67") == "998901234567"


@pytest.mark.parametrize("phone, cc, nat", [
    ("+998901234567", "998", "901234567"),   # O'zbekiston (eski kodda to'g'ri edi)
    ("+14155550123", "1", "4155550123"),      # AQSh (eski kodda BUZUQ edi)
    ("+447911123456", "44", "7911123456"),    # Buyuk Britaniya (eski kodda BUZUQ)
    ("+79161234567", "7", "9161234567"),       # Rossiya (eski kodda BUZUQ)
    ("+919812345678", "91", "9812345678"),     # Hindiston
])
def test_split_cc(phone, cc, nat):
    assert split_cc(phone) == (cc, nat)


def test_to_e164():
    assert to_e164("998 90 123 45 67") == "+998901234567"


@pytest.mark.parametrize("raw, expected", [
    ("+998901234567", "+998901234567"),
    ("998901234567", "+998901234567"),
    ("+998 90 123 45 67", "+998901234567"),
    ("abc", None),
    ("+1", None),               # juda qisqa
    ("+1234567890123456", None),  # juda uzun (>15)
])
def test_validate_phone(raw, expected):
    assert validate_phone(raw) == expected
