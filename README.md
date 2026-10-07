# Ignorant Pro

Telefon raqam OSINT vositasi — bitta raqam 12 ta platformada ro'yxatdan
o'tganmi, har platformaning **ochiq** "parolni tiklash / ro'yxatdan o'tish"
oqimi orqali tekshiradi. Login, parol yoki hack yo'q — faqat ochiq endpointlar.

> ⚠️ Faqat o'zingizga tegishli yoki qonuniy ruxsat berilgan raqamlarni tekshiring.

## O'rnatish

```bash
python3 -m venv venv
venv/bin/python -m pip install -r requirements.txt
```

## Foydalanish

```bash
python3 ignorant_pro.py +998901234567
python3 ignorant_pro.py +998901234567 --only instagram,telegram
python3 ignorant_pro.py --list        # platformalar ro'yxati + status
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

## Platformalar holati (2024-12 empirik kuzatuv + oracle sifati)

Har platforma raqamni "bor/yo'q" deb aniq ayta oladimi — bu platformaga bog'liq.
Ba'zilari ataylab bu ma'lumotni yashiradi (enumeration-hardened). Shunday
hollarda vosita **noto'g'ri FOUND/NOT_FOUND qaytarmaydi — halol UNKNOWN qaytaradi.**

| Platforma | Kuzatilgan holat | Izoh |
|-----------|------------------|------|
| OLX UZ | ✅ WORKING | `isRegistered` maydoni — ishonchli |
| Telegram | ⚠️ RATE_LIMITED | JSON `random_hash`/`error_message`; raqam egasiga kod yuboradi |
| Microsoft | ⚠️ ERROR_RESPONSE | `IfExistsResult`; ba'zan `ErrorHR` |
| TikTok | ⚠️ GEO_BLOCK / imzo | imzolangan parametr talab qiladi |
| Viber | ⚠️ UNSTABLE | umumiy javob |
| Snapchat | ⚠️ hardened | enumeration-hardened |
| Amazon | ⚠️ hardened | enumeration-hardened |
| Instagram | ❌ API_DOWN | lookup endpoint tez-tez 500/429 |
| Twitter/X | ❌ BEARER/JS | JS-challenge / client-transaction-id kerak |
| LinkedIn | ❌ ANTI_BOT | 999 anti-bot himoyasi |
| WhatsApp | ❌ oracle yo'q | **ochiq existence-oracle YO'Q** — hech qachon FOUND bermaydi |
| Google | ❌ RECAPTCHA | reCAPTCHA / JS-challenge |

`⚠️`/`❌` platformalar ko'pincha `UNKNOWN`/`ERROR` qaytaradi — bu kamchilik emas,
soxta natijadan ko'ra halollik.

## Testlar

```bash
venv/bin/python -m pip install -r requirements-dev.txt
venv/bin/python -m pytest -q
```

Testlar tarmoqqa chiqmaydi — soxta javoblar bilan ishlaydi va eski koddagi
xavfli "catch-all → FOUND" mantiqlari qaytib kelmaganini tekshiradi.

## Litsenziya va muallif

**Proprietary** — faqat shaxsiy foydalanish uchun. Tijorat maqsadida yoki
boshqalarga sotish taqiqlangan.

**Muallif:** [@Yescrypt](https://github.com/Yescrypt)
