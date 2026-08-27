#!/usr/bin/env python3
"""Debug ALL 12 platforms individually"""

import asyncio
import aiohttp
import json
from ignorant_pro import (
    check_instagram, check_telegram, check_tiktok, check_whatsapp,
    check_snapchat, check_twitter, check_viber, check_amazon,
    check_microsoft, check_olx_uz, check_linkedin, check_google,
    CHROME_UA, TIMEOUT
)

# Test raqam (real phone number - foydalanuvchi bersalari kerak)
PHONE = "+99893123456"

async def test_all():
    platforms = {
        "Instagram": check_instagram,
        "Telegram": check_telegram,
        "TikTok": check_tiktok,
        "WhatsApp": check_whatsapp,
        "Snapchat": check_snapchat,
        "Twitter/X": check_twitter,
        "Viber": check_viber,
        "Amazon": check_amazon,
        "Microsoft": check_microsoft,
        "OLX UZ": check_olx_uz,
        "LinkedIn": check_linkedin,
        "Google": check_google,
    }

    conn = aiohttp.TCPConnector(limit=1, ssl=False)  # Single connection
    async with aiohttp.ClientSession(connector=conn) as session:
        for name, func in platforms.items():
            print(f"\n{'='*60}")
            print(f"Testing: {name}")
            print(f"{'='*60}")

            try:
                result = await func(session, PHONE)
                print(f"Result: {result}")

                # Color output
                if result == "FOUND":
                    print(f"✅ PHONE FOUND ON {name.upper()}")
                elif result == "NOT_FOUND":
                    print(f"❌ Phone not found on {name}")
                elif result == "ERROR":
                    print(f"⚠️  ERROR - endpoint broken or changed")
                elif result == "RATE_LIMIT":
                    print(f"🚫 Rate limit - try later")
                elif result == "TIMEOUT":
                    print(f"⏱️  Timeout - server slow")

            except Exception as e:
                print(f"❌ Exception: {type(e).__name__}: {e}")

            # Delay between requests to avoid rate limit
            await asyncio.sleep(1)

if __name__ == "__main__":
    print(f"Testing phone: {PHONE}")
    print("=" * 60)
    asyncio.run(test_all())
