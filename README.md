# IGNORANT PRO v4.0

### 🔍 Telefon raqam OSINT CLI vositasi

IGNORANT PRO — bu telefon raqamning turli onlayn platformalarda ro’yxatdan o’tgan-o’tmaganini tekshiruvchi **async** OSINT vosita. Platforma tahlili va avtomatik hisobot fayl bilan.

---

## ⚡ Imkoniyatlari

| Feature | Description |
|---------|-------------|
| **12 Platform** | Instagram, Telegram, TikTok, WhatsApp, Snapchat, Twitter/X, Viber, Amazon, Microsoft, OLX.uz, LinkedIn, Google |
| **Async Parallel** | Hammasi bir paytda 20 sekund ichida tekshiriladi |
| **Aniq Natija** | FOUND / NOT_FOUND / RATE_LIMIT / TIMEOUT / ERROR |
| **Avtomatik Report** | `report-XXXX.txt` fayli saqlanadi |
| **CLI Filtering** | `--only Instagram,Telegram` bilan specific platforma |
| **Color Output** | Rang rang terminaldagi natija |
| **User-Agent Spoofing** | Real browser kabi request yuborish |

---

## 📦 O’rnatish

### 1. Repository klonlash

```bash
git clone https://github.com/Yescrypt/ignorantpro.git
cd ignorantpro
```

### 2. Virtual Environment (tavsiya etiladi)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate  # Windows
```

### 3. Dependencies o’rnatish

```bash
pip install -r requirements.txt
```

---

## 🚀 Ishlatish

### Oddiy tekshiruv

```bash
python3 ignorant_pro.py +998941350269
```

### Specific platformalar

```bash
python3 ignorant_pro.py +998941350269 --only Telegram,Instagram,TikTok
```

### Available Platforms

```
Instagram | Telegram | TikTok | WhatsApp | Snapchat | Twitter/X
Viber | Amazon | Microsoft | OLX.uz | LinkedIn | Google
```

---

## 📊 Output Formati

```
[+] FOUND           → Raqam servisda topildi
[-] NOT_FOUND       → Ro’yxatdan o’tmagan
[x] RATE_LIMIT      → Servis so’rovni chekladi (keyinroq urinib ko’ring)
[t] TIMEOUT         → Servis javob bermadi (slow connection)
[~] UNKNOWN         → Aniqlanmadi (manual tekshirish kerak)
[?] ERROR           → Xato ro’y berdi (endpoint o’zgargan)
```

### Report fayli

Har tekshiruv oxirida `report-XXXX.txt` fayli yaratiladi:
- Raqam va vaqt
- Barcha tekshirilgan platformalar
- Topilgan/topilmagan jami
- Xato va timeout tahlili

---

## 🔧 Texnik Detallar

### Metod

Bu vosita **OSINT** yo’nalishida ishlaydi:
- Saytlarning **forgot password** yoki **signup** flowini ishlatadi
- Hech qanday **login** yoki **parol** salarmasaydi
- Faqat **ochiq API endpointlar** ishlatiladi
- Hech qanday **brute force** yo’q

### Performance

- Async aiohttp bilan parallel tekshiruv
- TCP connection pooling (limit=30)
- Per-request timeout: 15 sekund
- Global timeout: 20 sekund
- Agar platform timeout bersa → TIMEOUT status

### Rate Limiting

Agar servis **[x] RATE_LIMIT** qaytarsa:
- IP muvaqaytda bloklanmadi
- Keyinchi sessiyada urinib ko’ring
- VPN yoki Proxy ishlatib ko’rishni tavsiya qilamiz

---

## 📝 Xavfsizlik Eslatmasi

✅ **Bu OSINT vositasi qonuni va etikaga muvofiq**
- Faqat **ma’suliyat bilan** ishlatiladi
- Boshqa odamning raqamini uning ijozisiz tekshirmang
- API cheklovlari respect qilinadi (rate limiting, timeout)

---

## 🐛 Known Issues

| Platform | Status | Note |
|----------|--------|------|
| Google | ⚠️ Risky | reCAPTCHA ko’p bo’ladi |
| Instagram | ⚠️ Unstable | API tez o’zgaradi |
| TikTok | ⚠️ Geo-check | VPN kerak bo’lishi mumkin |
| All | ✅ Good | Rate limit bo’lsa retry qiling |

---

## 🛠️ Development

### Test ishga tushirish

```bash
python3 test_services.py
```

### Debug mode

```python
# ignorant_pro.py ni edit qilib qo’ying:
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Versiya tarix

- **v4.0** — Timeout fix, Telegram check yaxshilash, README kengaytirish
- **v3.0** — 12 platform support
- **v2.0** — Async parallel tekshiruv
- **v1.0** — Birinchi release

---

## 📜 Licence

**Proprietary** — Faqat personal use uchun. Tijorat maqsadida yoki boshqalarga sotishni taqiqlangan.

---

## 👤 Author

**Yescrypt** — OSINT vosita developer  
GitHub: [@Yescrypt](https://github.com/Yescrypt)

---

## 🤝 Contribute

Bug topilsa yoki feature kerak bo’lsa — **GitHub Issue** ochib qo’ying!
