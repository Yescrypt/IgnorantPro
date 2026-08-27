#!/usr/bin/env python3
"""Raw HTTP debugging - see actual responses"""

import asyncio
import aiohttp
import json
import re
from colorama import Fore, Style, init

init(autoreset=True)

PHONE = "+99893123456"
CHROME_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

async def debug_instagram():
    print(f"\n{Fore.CYAN}{'='*70}")
    print("INSTAGRAM DEBUG")
    print(f"{'='*70}{Style.RESET_ALL}")

    async with aiohttp.ClientSession() as session:
        # Get CSRF
        async with session.get("https://www.instagram.com/accounts/emailsignup/") as r:
            text = await r.text()
            csrf_match = re.search(r'"csrf_token":"([^"]+)"', text)
            csrf = csrf_match.group(1) if csrf_match else "NO_CSRF"
            print(f"CSRF Token: {csrf[:20]}...")

        # Send phone
        headers = {"X-CSRFToken": csrf, "X-Instagram-AJAX": "1"}
        async with session.post(
            "https://www.instagram.com/api/v1/users/lookup_phone_with_count/",
            data=f"phone_number={PHONE}",
            headers=headers,
        ) as r:
            response = await r.text()
            print(f"Status: {r.status}")
            print(f"Response: {response[:300]}")
            try:
                j = json.loads(response)
                print(f"JSON Keys: {list(j.keys())}")
            except:
                print(f"Not JSON: {response[:100]}")

async def debug_linkedin():
    print(f"\n{Fore.CYAN}{'='*70}")
    print("LINKEDIN DEBUG")
    print(f"{'='*70}{Style.RESET_ALL}")

    async with aiohttp.ClientSession() as session:
        # Get CSRF
        async with session.get("https://www.linkedin.com/uas/request-password-reset") as r:
            text = await r.text()
            csrf_match = re.search(r'csrfToken=([^&"\']+)', text)
            csrf = csrf_match.group(1) if csrf_match else "NO_CSRF"
            print(f"CSRF Token found: {'✓' if csrf != 'NO_CSRF' else '✗'}")

        # Try password reset
        async with session.post(
            "https://www.linkedin.com/uas/request-password-reset",
            data=f"csrfToken={csrf}&email={PHONE}",
            allow_redirects=True,
        ) as r:
            response = await r.text()
            url = str(r.url)
            print(f"Status: {r.status}")
            print(f"Final URL: {url}")
            print(f"Response length: {len(response)}")
            if "checkYourEmail" in url or "check" in response.lower():
                print(f"{Fore.GREEN}✓ PHONE FOUND{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}✗ NOT FOUND{Style.RESET_ALL}")
            print(f"Response snippet: {response[:200]}")

async def debug_microsoft():
    print(f"\n{Fore.CYAN}{'='*70}")
    print("MICROSOFT DEBUG")
    print(f"{'='*70}{Style.RESET_ALL}")

    async with aiohttp.ClientSession() as session:
        # Get tokens
        async with session.get("https://login.live.com/login.srf") as r:
            text = await r.text()
            uaid_m = re.search(r'"uaid":"([^"]+)"', text)
            uaid = uaid_m.group(1) if uaid_m else "default"
            print(f"UAID: {uaid}")

        # GetCredentialType
        payload = {
            "username": PHONE,
            "uaid": uaid,
            "isOtherIdpSupported": True,
        }
        async with session.post(
            "https://login.live.com/GetCredentialType.srf",
            json=payload,
        ) as r:
            response = await r.text()
            print(f"Status: {r.status}")
            print(f"Response: {response[:300]}")
            try:
                j = json.loads(response)
                ier = j.get("IfExistsResult")
                print(f"IfExistsResult: {ier} (0=found, 1=not found, 6=federated)")
                if ier == 0 or ier == 6:
                    print(f"{Fore.GREEN}✓ PHONE FOUND{Style.RESET_ALL}")
                elif ier == 1:
                    print(f"{Fore.RED}✗ NOT FOUND{Style.RESET_ALL}")
            except:
                print(f"Not JSON response")

async def debug_twitter():
    print(f"\n{Fore.CYAN}{'='*70}")
    print("TWITTER/X DEBUG")
    print(f"{'='*70}{Style.RESET_ALL}")

    bearer = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

    async with aiohttp.ClientSession() as session:
        # Guest token
        async with session.post(
            "https://api.twitter.com/1.1/guest/activate.json",
            headers={"Authorization": f"Bearer {bearer}"},
        ) as r:
            gtok_data = await r.json()
            gtok = gtok_data.get("guest_token", "")
            print(f"Guest Token: {gtok[:20] if gtok else 'FAILED'}...")

        if gtok:
            # Password reset flow
            headers = {"Authorization": f"Bearer {bearer}", "X-Guest-Token": gtok}
            async with session.post(
                "https://api.twitter.com/1.1/onboarding/task.json?flow_name=forgot-password",
                json={"flow_token": None, "input_flow_data": {}},
                headers=headers,
            ) as r:
                flow_data = await r.json()
                flow_token = flow_data.get("flow_token")
                print(f"Flow Token: {flow_token[:20] if flow_token else 'FAILED'}...")

                if flow_token:
                    # Send phone
                    payload = {
                        "flow_token": flow_token,
                        "subtask_inputs": [{
                            "subtask_id": "EnterUserIdentifier",
                            "enter_text": {"text": PHONE, "link": "next_link"},
                        }],
                    }
                    async with session.post(
                        "https://api.twitter.com/1.1/onboarding/task.json",
                        json=payload,
                        headers=headers,
                    ) as r2:
                        response = await r2.text()
                        print(f"Status: {r2.status}")
                        print(f"Response: {response[:400]}")

async def main():
    print(f"{Fore.YELLOW}Debugging ALL platforms with RAW responses{Style.RESET_ALL}")
    print(f"Phone: {PHONE}\n")

    await debug_instagram()
    await asyncio.sleep(1)

    await debug_linkedin()
    await asyncio.sleep(1)

    await debug_microsoft()
    await asyncio.sleep(1)

    await debug_twitter()

if __name__ == "__main__":
    asyncio.run(main())
