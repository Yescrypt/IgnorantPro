# Ignorant Pro

Telefon raqam OSINT vositasi — bitta raqam 12 ta platformada ro'yxatdan
o'tganmi, har platformaning **ochiq** "parolni tiklash / ro'yxatdan o'tish"
oqimi orqali tekshiradi. Login, parol yoki hack yo'q — faqat ochiq endpointlar.

> Faqat o'zingizga tegishli yoki qonuniy ruxsat berilgan raqamlarni tekshiring.

## O'rnatish

```bash
python3 -m venv venv
venv/bin/python -m pip install -r requirements.txt
```

## Foydalanish

```bash
python3 ignorant_pro.py +998901234567
python3 ignorant_pro.py +998901234567 --only instagram,telegram
python3 ignorant_pro.py --list        # platformalar ro'yxati
python3 ignorant_pro.py +998901234567 --no-report
```

Natija holatlari:

| Belgi | Holat | Ma'no |
|------|-------|-------|
| `[+]` | FOUND | Raqam platformada bor |
| `[-]` | NOT_FOUND | Raqam platformada yo'q |
| `[~]` | UNKNOWN | Oracle aniq javob bermadi (qo'lda tekshiring) |
| `[x]` | RATE_LIMIT | Platforma so'rovlarni cheklab qo'ydi |
| `[t]` | TIMEOUT | Vaqt tugadi |
| `[?]` | ERROR | Xato / endpoint o'zgargan |

## Loyiha tuzilmasi

```
ignorant_pro.py            # ingichka CLI entrypoint
ignorant/
├─ cli.py                  # argumentlar, ishga tushirish
├─ core/
│  ├─ base.py              # Result, Outcome, BaseChecker
│  ├─ http.py              # sessiya fabrikasi, timeout, UA
│  ├─ registry.py          # modullarni yig'ish/qidirish
│  ├─ runner.py            # parallel ishga tushirish
│  ├─ display.py           # terminalga chop etish
│  └─ report.py            # report-XXXX.txt saqlash
├─ utils/
│  └─ phone.py             # digits_only, split_cc, validate_phone
└─ modules/                # har platforma — alohida fayl
   instagram · telegram · tiktok · whatsapp · snapchat · twitter
   viber · olx_uz · amazon · microsoft · linkedin · google
```

**Yangi platforma qo'shish:** `ignorant/modules/` da yangi fayl yarating,
`BaseChecker` dan meros oling, `check()` ni yozing va uni
`ignorant/modules/__init__.py` dagi `ALL_CHECKERS` ro'yxatiga qo'shing.

## Platformalar ishonchliligi

Har platforma raqamni "bor/yo'q" deb aniq ayta oladimi — bu platformaga bog'liq.
Ba'zilari ataylab bu ma'lumotni yashiradi (enumeration-hardened). Shunday
hollarda vosita **noto'g'ri FOUND/NOT_FOUND qaytarmaydi — halol UNKNOWN qaytaradi.**

| Platforma | Ishonchli | Izoh |
|-----------|-----------|------|
| Microsoft | ✅ | `IfExistsResult` — ishonchli oracle |
| Telegram | ✅ | `send_password` — lekin raqam egasiga kod yuboradi |
| Instagram | ✅ | lookup endpoint; tez-tez rate-limit |
| OLX UZ | ✅ | `isRegistered` maydoni |
| TikTok | ⚠️ | endi imzolangan parametr talab qiladi |
| Twitter/X | ⚠️ | JS-challenge / client-transaction-id kerak |
| Snapchat | ⚠️ | enumeration-hardened |
| Viber | ⚠️ | umumiy javob |
| Amazon | ⚠️ | enumeration-hardened |
| LinkedIn | ⚠️ | enumeration-hardened |
| WhatsApp | ⚠️ | **ochiq existence-oracle YO'Q** — FOUND bermaydi |
| Google | ⚠️ | reCAPTCHA / JS-challenge |

`⚠️` platformalar ko'pincha `UNKNOWN` qaytaradi — bu kamchilik emas, halollik.

## Testlar

```bash
venv/bin/python -m pip install -r requirements-dev.txt
venv/bin/python -m pytest -q
```

Testlar tarmoqqa chiqmaydi — soxta javoblar bilan ishlaydi va eski koddagi
xavfli "catch-all → FOUND" mantiqlari qaytib kelmaganini tekshiradi.
