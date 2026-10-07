"""Natijalarni terminalga chiroyli chop etish."""

from __future__ import annotations

from colorama import Fore, Style

from ignorant.core.base import Outcome, Result

BANNER = f"""
{Fore.CYAN}╔════════════════════════════════════════════════╗
║  {Fore.WHITE}IGNORANT PRO{Fore.CYAN}  -  Phone Number OSINT Tool      ║
║  {Fore.YELLOW}12 platform  |  modular  |  auto report   {Fore.CYAN}    ║
╚════════════════════════════════════════════════╝{Style.RESET_ALL}
"""

STATUS_ICON = {
    Result.FOUND:      f"{Fore.GREEN}[+]{Style.RESET_ALL}",
    Result.NOT_FOUND:  f"{Fore.RED}[-]{Style.RESET_ALL}",
    Result.UNKNOWN:    f"{Fore.BLUE}[~]{Style.RESET_ALL}",
    Result.RATE_LIMIT: f"{Fore.YELLOW}[x]{Style.RESET_ALL}",
    Result.TIMEOUT:    f"{Fore.YELLOW}[t]{Style.RESET_ALL}",
    Result.ERROR:      f"{Fore.MAGENTA}[?]{Style.RESET_ALL}",
}

STATUS_TEXT = {
    Result.FOUND:      f"{Fore.GREEN}Phone number used{Style.RESET_ALL}",
    Result.NOT_FOUND:  f"{Fore.RED}Phone number not used{Style.RESET_ALL}",
    Result.UNKNOWN:    f"{Fore.BLUE}Unknown — manual check{Style.RESET_ALL}",
    Result.RATE_LIMIT: f"{Fore.YELLOW}Rate limit — try later{Style.RESET_ALL}",
    Result.TIMEOUT:    f"{Fore.YELLOW}Timeout{Style.RESET_ALL}",
    Result.ERROR:      f"{Fore.MAGENTA}Error{Style.RESET_ALL}",
}


def print_results(phone: str, results: dict[str, Outcome], elapsed: float) -> None:
    """Natijalar jadvalini va qisqa statistikani chiqaradi."""
    print(f"\n{'*' * 50}")
    print(f"   {Fore.CYAN}{phone}{Style.RESET_ALL}")
    print(f"{'*' * 50}")

    counts: dict[Result, int] = {}
    for site, outcome in results.items():
        icon = STATUS_ICON.get(outcome.result, STATUS_ICON[Result.ERROR])
        text = STATUS_TEXT.get(outcome.result, str(outcome.result))
        pad = " " * max(1, 14 - len(site))
        note = f"  {Fore.WHITE}· {outcome.note}{Style.RESET_ALL}" if outcome.note else ""
        print(f"{icon} {Fore.WHITE}{site}{Style.RESET_ALL}{pad}{text}{note}")
        counts[outcome.result] = counts.get(outcome.result, 0) + 1

    print(f"\n{Fore.CYAN}{len(results)} platforms checked in {elapsed:.2f}s{Style.RESET_ALL}")
    print(
        f"{Fore.GREEN}[+]{Style.RESET_ALL} Found: {counts.get(Result.FOUND, 0)}  "
        f"{Fore.RED}[-]{Style.RESET_ALL} Not: {counts.get(Result.NOT_FOUND, 0)}  "
        f"{Fore.BLUE}[~]{Style.RESET_ALL} Unknown: {counts.get(Result.UNKNOWN, 0)}  "
        f"{Fore.YELLOW}[x]{Style.RESET_ALL} Limit: {counts.get(Result.RATE_LIMIT, 0)}  "
        f"{Fore.YELLOW}[t]{Style.RESET_ALL} Timeout: {counts.get(Result.TIMEOUT, 0)}  "
        f"{Fore.MAGENTA}[?]{Style.RESET_ALL} Error: {counts.get(Result.ERROR, 0)}"
    )
    print(
        f"\n{Fore.WHITE}Legend:{Style.RESET_ALL} "
        f"{Fore.GREEN}[+]{Style.RESET_ALL} Found  "
        f"{Fore.RED}[-]{Style.RESET_ALL} Not used  "
        f"{Fore.BLUE}[~]{Style.RESET_ALL} Unknown  "
        f"{Fore.YELLOW}[x]{Style.RESET_ALL} Rate limit  "
        f"{Fore.YELLOW}[t]{Style.RESET_ALL} Timeout  "
        f"{Fore.MAGENTA}[?]{Style.RESET_ALL} Error"
    )
