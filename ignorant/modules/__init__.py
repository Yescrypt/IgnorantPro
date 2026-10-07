"""Platforma modullari — har bir platforma alohida faylda.

`ALL_CHECKERS` — reyestr uchun yagona manba. Yangi platforma qo'shish uchun
yangi fayl yarating, `BaseChecker` dan meros oling va shu ro'yxatga qo'shing.
"""

from __future__ import annotations

from ignorant.core.base import BaseChecker
from ignorant.modules.amazon import AmazonChecker
from ignorant.modules.google import GoogleChecker
from ignorant.modules.instagram import InstagramChecker
from ignorant.modules.linkedin import LinkedInChecker
from ignorant.modules.microsoft import MicrosoftChecker
from ignorant.modules.olx_uz import OlxUzChecker
from ignorant.modules.snapchat import SnapchatChecker
from ignorant.modules.telegram import TelegramChecker
from ignorant.modules.tiktok import TikTokChecker
from ignorant.modules.twitter import TwitterChecker
from ignorant.modules.viber import ViberChecker
from ignorant.modules.whatsapp import WhatsAppChecker

ALL_CHECKERS: list[BaseChecker] = [
    InstagramChecker(),
    TelegramChecker(),
    TikTokChecker(),
    WhatsAppChecker(),
    SnapchatChecker(),
    TwitterChecker(),
    ViberChecker(),
    OlxUzChecker(),
    AmazonChecker(),
    MicrosoftChecker(),
    LinkedInChecker(),
    GoogleChecker(),
]

__all__ = ["ALL_CHECKERS"]
