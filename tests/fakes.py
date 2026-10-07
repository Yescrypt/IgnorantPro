"""Testlar uchun soxta (fake) aiohttp sessiya — tarmoqqa chiqmasdan sinash.

Modullar `async with session.get(...) as r:` naqshidan foydalanadi va
`r.status`, `await r.text()`, `await r.json()`, `r.headers`, `r.cookies`,
`str(r.url)` ga murojaat qiladi. FakeSession aynan shu interfeysni taqlid
qiladi va navbatdagi tayyor javoblarni qaytaradi.
"""

from __future__ import annotations

import json as _json
from collections import deque


class FakeCookie:
    def __init__(self, value: str) -> None:
        self.value = value


class FakeResponse:
    """Bitta HTTP javobni taqlid qiladi (async context manager)."""

    def __init__(self, status: int = 200, text: str = "", *,
                 headers: dict | None = None, url: str = "https://example.test/",
                 cookies: dict | None = None) -> None:
        self.status = status
        self._text = text
        self.headers = headers or {}
        self.url = url
        self.cookies = {k: FakeCookie(v) for k, v in (cookies or {}).items()}

    async def text(self) -> str:
        return self._text

    async def json(self):
        return _json.loads(self._text)

    async def __aenter__(self) -> "FakeResponse":
        return self

    async def __aexit__(self, *exc) -> bool:
        return False


class FakeSession:
    """Navbat bo'yicha tayyor javoblarni qaytaruvchi soxta sessiya."""

    def __init__(self, responses: list[FakeResponse]) -> None:
        self._queue: deque[FakeResponse] = deque(responses)
        self.calls: list[tuple[str, str]] = []  # (method, url)

    def _next(self, method: str, url: str) -> FakeResponse:
        self.calls.append((method, url))
        if not self._queue:
            raise AssertionError(f"Kutilmagan {method} {url} — javob navbati bo'sh")
        return self._queue.popleft()

    def get(self, url, **kwargs) -> FakeResponse:
        return self._next("GET", url)

    def post(self, url, **kwargs) -> FakeResponse:
        return self._next("POST", url)
