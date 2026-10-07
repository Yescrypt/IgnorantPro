"""Telefon raqam bilan ishlash yordamchilari.

Eski kodda davlat kodini ajratish buzuq edi:
    cc = d[:3] if d.startswith("998") else d[:1]
bu faqat +998 uchun ishlardi, +44 / +1 / +7 larda noto'g'ri natija berardi.

Bu yerda E.164 davlat chaqiruv kodlari jadvali asosida eng uzun mos
prefiksni topuvchi to'g'ri algoritm bor. To'liq libphonenumber emas, lekin
OSINT tekshiruvlari uchun yetarli darajada aniq.
"""

from __future__ import annotations

import re

# E.164 davlat chaqiruv kodlari. To'liq ro'yxat emas, lekin eng ko'p
# uchraydiganlar + loyiha uchun muhimlari (998 = O'zbekiston) bor.
# Eng uzun mos (longest-prefix) tanlanadi, shuning uchun "1" ham, "1340" ham
# bo'lsa — uzunrog'i ustun.
CALLING_CODES: frozenset[str] = frozenset({
    "1", "7",
    "20", "27", "30", "31", "32", "33", "34", "36", "39", "40", "41", "43",
    "44", "45", "46", "47", "48", "49", "51", "52", "53", "54", "55", "56",
    "57", "58", "60", "61", "62", "63", "64", "65", "66", "81", "82", "84",
    "86", "90", "91", "92", "93", "94", "95", "98",
    "211", "212", "213", "216", "218", "220", "221", "222", "223", "224",
    "225", "226", "227", "228", "229", "230", "231", "232", "233", "234",
    "235", "236", "237", "238", "239", "240", "241", "242", "243", "244",
    "245", "248", "249", "250", "251", "252", "253", "254", "255", "256",
    "257", "258", "260", "261", "262", "263", "264", "265", "266", "267",
    "268", "269", "290", "291", "297", "298", "299",
    "350", "351", "352", "353", "354", "355", "356", "357", "358", "359",
    "370", "371", "372", "373", "374", "375", "376", "377", "378", "380",
    "381", "382", "383", "385", "386", "387", "389",
    "420", "421", "423",
    "500", "501", "502", "503", "504", "505", "506", "507", "508", "509",
    "590", "591", "592", "593", "594", "595", "596", "597", "598", "599",
    "670", "672", "673", "674", "675", "676", "677", "678", "679", "680",
    "681", "682", "683", "685", "686", "687", "688", "689", "690", "691",
    "692",
    "850", "852", "853", "855", "856", "880", "886",
    "960", "961", "962", "963", "964", "965", "966", "967", "968", "970",
    "971", "972", "973", "974", "975", "976", "977",
    "992", "993", "994", "995", "996", "998",
})

# Davlat kodlarini uzunligi bo'yicha kamayuvchi tartibda — longest-prefix.
_CODES_BY_LEN = sorted(CALLING_CODES, key=len, reverse=True)


def digits_only(phone: str) -> str:
    """Raqamdan faqat raqam belgilarini qoldiradi: '+998 (90) 123' -> '99890123'."""
    return re.sub(r"[^\d]", "", phone)


def split_cc(phone: str) -> tuple[str, str]:
    """Raqamni (davlat_kodi, milliy_raqam) ga ajratadi.

    E.164 kodlar jadvalidan eng uzun mos prefiksni tanlaydi.

    >>> split_cc("+998901234567")
    ('998', '901234567')
    >>> split_cc("+14155550123")
    ('1', '4155550123')
    >>> split_cc("+447911123456")
    ('44', '7911123456')

    Agar hech qaysi kod mos kelmasa — konservativ fallback: 3 raqam.
    """
    d = digits_only(phone)
    for code in _CODES_BY_LEN:
        if d.startswith(code) and len(d) > len(code):
            return code, d[len(code):]
    # Fallback — hech qaysi ma'lum kod mos kelmadi.
    return d[:3], d[3:]


def to_e164(phone: str) -> str:
    """Raqamni '+' bilan boshlanadigan E.164 ko'rinishga keltiradi."""
    return "+" + digits_only(phone)


def validate_phone(raw: str) -> str | None:
    """CLI kiritgan raqamni tekshiradi va normallashtiradi.

    Bo'sh joy, qavs, chiziqchalarni olib tashlaydi, '+' qo'shadi.
    To'g'ri bo'lsa E.164 satr, aks holda None qaytaradi.
    """
    clean = re.sub(r"[\s\-()]", "", raw)
    if not clean.startswith("+"):
        clean = "+" + clean
    return clean if re.match(r"^\+\d{7,15}$", clean) else None
