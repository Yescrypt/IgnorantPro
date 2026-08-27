#!/usr/bin/env python3
"""
Service testing — real scenarios uchun
Har bir service'ni debug qilish uchun
"""

import asyncio
import aiohttp
from ignorant_pro import (
    check_telegram, check_tiktok, check_whatsapp,
    check_instagram, check_twitter, check_microsoft,
    CHROME_UA, TIMEOUT
)

async def test_service():
    """
    Test phone raqamlar:
    +1234567890 — ko'p saitlarda NOT_FOUND bo'lishi kerak
    +998901234567 — o'zbek raqami, OLX da bo'lishi ehtimoli
    """

    # Test case 1: invalid raqam
    test_phones = [
        "+1234567890",      # invalid (to'liq saitlarda yo'q)
        "+998901234567",    # o'zbek raqami
    ]

    conn = aiohttp.TCPConnector(limit=5, ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        for phone in test_phones:
            print(f"\n\n{'='*50}")
            print(f"Testing: {phone}")
            print(f"{'='*50}\n")

            # 1. Telegram
            print("► Telegram...", end=" ", flush=True)
            result = await check_telegram(session, phone)
            print(f"  {result}")

            # 2. TikTok
            print("► TikTok...", end=" ", flush=True)
            result = await check_tiktok(session, phone)
            print(f"  {result}")

            # 3. WhatsApp
            print("► WhatsApp...", end=" ", flush=True)
            result = await check_whatsapp(session, phone)
            print(f"  {result}")

            # 4. Instagram
            print("► Instagram...", end=" ", flush=True)
            result = await check_instagram(session, phone)
            print(f"  {result}")

            # 5. Twitter
            print("► Twitter/X...", end=" ", flush=True)
            result = await check_twitter(session, phone)
            print(f"  {result}")

            # 6. Microsoft
            print("► Microsoft...", end=" ", flush=True)
            result = await check_microsoft(session, phone)
            print(f"  {result}")

if __name__ == "__main__":
    asyncio.run(test_service())
