#!/usr/bin/env python3
import asyncio
import aiohttp
from ignorant_pro import check_telegram, check_whatsapp, CHROME_UA, TIMEOUT
import urllib.parse

phone = "+99893123456"  # Test raqam (haqiqiy emas, lekin test uchun)

async def debug():
    conn = aiohttp.TCPConnector(limit=5, ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        print("=" * 60)
        print("TELEGRAM DEBUG")
        print("=" * 60)
        try:
            # Direct test Telegram API
            response = await session.post(
                "https://my.telegram.org/auth/send_password",
                data=urllib.parse.urlencode({"phone": phone}),
                headers={
                    "User-Agent": CHROME_UA,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                timeout=TIMEOUT,
            )
            text = await response.text()
            print(f"Status: {response.status}")
            print(f"Response text (first 200 chars): {text[:200]}")
            print(f"Response length: {len(text)}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n" + "=" * 60)
        print("WHATSAPP DEBUG")
        print("=" * 60)
        try:
            # Direct test WhatsApp API
            d = "99893123456"
            url = f"https://api.whatsapp.com/send/?phone={d}&text&type=phone_number&app_absent=0"
            response = await session.get(url, allow_redirects=True, timeout=TIMEOUT)
            text = await response.text()
            print(f"Status: {response.status}")
            print(f"URL (final): {response.url}")
            print(f"Response text (first 300 chars): {text[:300]}")
            print(f"Response length: {len(text)}")
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(debug())
