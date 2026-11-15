# Ignorant Pro — post matnlari

## Qisqa variant (Telegram / X / kanal)

🔍 **Ignorant Pro** — telefon raqam OSINT vositasi.

Bitta raqam — 12 ta platformada ro'yxatdan o'tganmi, tekshiradi. Faqat
platformalarning **ochiq** "parolni tiklash" oqimi orqali. Login yo'q, parol
yo'q, hack yo'q.

✅ Modulli arxitektura — har platforma alohida fayl
✅ Parallel, tez (barcha platforma bir vaqtda)
✅ Halol natija — aniq signal bo'lmasa soxta "topildi" bermaydi
✅ Avtomatik hisobot fayli
✅ Python 3 + asyncio

```
python3 ignorant_pro.py +998901234567
```

⚠️ Faqat o'zingizga tegishli yoki ruxsat berilgan raqamlarni tekshiring.

---

## Uzun variant (GitHub / forum / blog)

### Ignorant Pro — Telefon raqam OSINT vositasi

Ignorant Pro bitta telefon raqamining 12 ta mashhur platformada ro'yxatdan
o'tgan-o'tmaganini aniqlaydi. Vosita faqat har bir platformaning **ochiq
endpointlari** — ya'ni "parolni tiklash / ro'yxatdan o'tish" oqimlari — orqali
ishlaydi. Hech qanday login, parol yoki ruxsatsiz kirish ishlatilmaydi.

**Qo'llab-quvvatlanadigan platformalar:**
Instagram · Telegram · TikTok · WhatsApp · Snapchat · Twitter/X · Viber ·
OLX UZ · Amazon · Microsoft · LinkedIn · Google

**Xususiyatlar:**

- **Modulli arxitektura** — har platforma alohida modul. Yangi platforma
  qo'shish uchun bitta fayl yaratib, ro'yxatga qo'shasiz.
- **Parallel ishga tushirish** — barcha platformalar bir vaqtda tekshiriladi
  (asyncio), natija bir necha soniyada tayyor.
- **Halol natijalar** — aniq signal bo'lmaganda vosita soxta "topildi"
  bermaydi; o'rniga halol `UNKNOWN` qaytaradi. Bu false-positive'larni
  oldini oladi.
- **Avtomatik hisobot** — har tekshiruv matnli hisobot fayliga saqlanadi.
- **Toza CLI** — `--only`, `--list`, `--no-report` kabi qulay bayroqlar.

**O'rnatish:**

```bash
python3 -m venv venv
venv/bin/python -m pip install -r requirements.txt
```

**Foydalanish:**

```bash
python3 ignorant_pro.py +998901234567
python3 ignorant_pro.py +998901234567 --only instagram,telegram
python3 ignorant_pro.py --list
```

Texnologiyalar: Python 3 · asyncio · aiohttp

⚠️ **Ogohlantirish:** faqat o'zingizga tegishli yoki qonuniy ruxsat berilgan
raqamlarni tekshiring.
