"""Buyruq qatori interfeysi (CLI).

Foydalanish:
    python3 ignorant_pro.py +998901234567
    python3 ignorant_pro.py +998901234567 --only instagram,telegram
    python3 ignorant_pro.py --list
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import time

from colorama import Fore, Style

from ignorant.core import registry
from ignorant.core.display import BANNER, print_results
from ignorant.core.report import save_report
from ignorant.core.runner import run_checks
from ignorant.utils.phone import validate_phone


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ignorant_pro",
        description="Telefon raqam OSINT — 12 platforma (modular).",
    )
    p.add_argument("phone", nargs="?", help="Tekshiriladigan raqam, masalan +998901234567")
    p.add_argument("--only", metavar="LIST",
                   help="Faqat shu platformalar (vergul bilan): instagram,telegram")
    p.add_argument("--list", action="store_true", help="Platformalar ro'yxatini ko'rsatish")
    p.add_argument("--no-report", action="store_true", help="Hisobot faylini saqlamaslik")
    return p


def _print_list() -> None:
    print(f"{Fore.CYAN}Platformalar:{Style.RESET_ALL}")
    for c in registry.all_checkers():
        mark = (f"{Fore.GREEN}ishonchli{Style.RESET_ALL}" if c.reliable
                else f"{Fore.YELLOW}ishonchsiz{Style.RESET_ALL}")
        print(f"  {c.slug:12} {c.name:14} [{mark}]")


def main(argv: list[str] | None = None) -> int:
    """CLI kirish nuqtasi. Qaytaradi: process exit kodi."""
    print(BANNER)
    args = _build_parser().parse_args(argv)

    if args.list:
        _print_list()
        return 0

    if not args.phone:
        print(f"{Fore.YELLOW}Usage:{Style.RESET_ALL}")
        print("  python3 ignorant_pro.py +998901234567")
        print("  python3 ignorant_pro.py +998901234567 --only instagram,telegram")
        print("  python3 ignorant_pro.py --list")
        return 0

    phone = validate_phone(args.phone)
    if not phone:
        print(f"{Fore.RED}[!] Noto'g'ri format: {args.phone}{Style.RESET_ALL}")
        print("    To'g'ri: +998901234567")
        return 1

    if args.only:
        checkers, unknown = registry.resolve(args.only.split(","))
        if unknown:
            print(f"{Fore.YELLOW}[!] Noma'lum: {', '.join(unknown)}{Style.RESET_ALL}")
            print(f"    Mavjud: {', '.join(c.slug for c in registry.all_checkers())}")
            return 1
    else:
        checkers = registry.all_checkers()

    label = (", ".join(c.name for c in checkers) if args.only
             else f"barcha {len(checkers)} ta platform")
    print(f"{Fore.CYAN}[*] Raqam     : {Fore.WHITE}{phone}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[*] Tekshirish: {label}...{Style.RESET_ALL}\n")

    start = time.time()
    results = asyncio.run(run_checks(phone, checkers))
    elapsed = time.time() - start

    print_results(phone, results, elapsed)

    if not args.no_report:
        fname = save_report(phone, results, elapsed)
        if fname:
            print(f"\n{Fore.GREEN}[✔] Report:{Style.RESET_ALL} {fname}")
        else:
            print(f"\n{Fore.RED}[!] Report saqlanmadi.{Style.RESET_ALL}")

    return 0
