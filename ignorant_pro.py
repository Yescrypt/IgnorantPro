#!/usr/bin/env python3
"""IGNORANT PRO — Phone Number OSINT Tool (ingichka entrypoint).

Haqiqiy mantiq `ignorant/` paketida — har platforma alohida modulda
(`ignorant/modules/`). Bu fayl faqat CLI ni ishga tushiradi, shunda eski
`python3 ignorant_pro.py +998...` buyrug'i oldingidek ishlaydi.

Metod: saytlarning ochiq "parolni tiklash / ro'yxatdan o'tish" oqimlari.
Login, parol yoki hack yo'q — faqat ochiq endpointlar.
"""

from __future__ import annotations

import sys

from ignorant.cli import main

if __name__ == "__main__":
    sys.exit(main())
