# IGNORANT PRO — Changelog

Barcha muhim o'zgarishlar shu yerda qayd etiladi.

---

## [4.1] - 2024-12-20

### ✨ Added
- Test fayli: `test_services.py` debug uchun
- README: markdown table format, detallarni expand
- Version history va development info

### 🔧 Improved
- Timeout qiymatlari optimizatsiya qilindi (14s→15s, 8s→9s)
- Telegram check'i JSON response handling bilan yaxshilandi
- asyncio.wait() performance qoidalari to'g'rilandi
- WhatsApp check: fallback endpoint logic yaxshilandi
- Instagram check: multiple fallback endpoints qo'shildi
- Google check: try-except wrapping, cleaner logic

### 🐛 Fixed
- False negative risk kamaytirildi barcha servislarda
- asyncio timeout handling to'g'rilandi
- JSON parsing error handling yaxshilandi

### 📊 Performance
- Global timeout: 20 sekund (oldindan: 22s)
- Per-request timeout: 15 sekund (oldindan: 14s)
- TCP pool size: 30 connections

---

## [4.0] - 2024-11-15

### ✨ Initial Public Release
- 12 ta platform suporti
- Async parallel tekshiruv
- Avtomatik report fayli
- CLI filtering (`--only` flag)
- Color-coded output
- User-Agent spoofing

### 📋 Supported Platforms
1. Instagram — web signup endpoint
2. Telegram — my.telegram.org API
3. TikTok — passport mobile endpoint
4. WhatsApp — api.whatsapp.com
5. Snapchat — password reset flow
6. Twitter/X — onboarding flow API
7. Viber — account recovery
8. Amazon — forgot password endpoint
9. Microsoft — GetCredentialType SRF
10. OLX.uz — auth OTP endpoint
11. LinkedIn — password reset form
12. Google — signin identifier flow

### ⚙️ Technical Stack
- Python 3.10+
- aiohttp (async HTTP)
- colorama (terminal colors)
- asyncio (parallel execution)

---

## [3.0] - 2024-10-01

### ✨ Added
- 8 ta platform initial support
- Report generation feature
- CLI argument parsing

### 🔧 Improved
- Email endpoints stability

---

## [2.0] - 2024-09-01

### ✨ Added
- Async execution
- Basic CLI

---

## [1.0] - 2024-08-01

### ✨ Initial
- First release
- 2 ta platform (Instagram, Telegram)
- Sequential check (non-async)

---

## Future Plans (Roadmap)

### v5.0
- [ ] Telegram username resolution (bot API)
- [ ] WhatsApp status check
- [ ] Additional platforms (Signal, Discord, Matrix)
- [ ] Database storage (SQLite)
- [ ] Web API wrapper

### v6.0
- [ ] GUI desktop app
- [ ] Batch processing (.csv input)
- [ ] Webhook notifications
- [ ] Export formats (JSON, CSV, PDF)
- [ ] Browser automation (Selenium fallback)

### v7.0
- [ ] Machine Learning false positive detection
- [ ] Geo-IP tracking
- [ ] Account profile scraping
- [ ] Social graph analysis
- [ ] Dark web monitoring

---

## Contribution

Bug reports va feature requests uchun GitHub Issues ochib qo'ying!

```
Tepa'si: https://github.com/Yescrypt/IgnorantPro/issues
```

---

## License

**Proprietary** — Personal use only. Unauthorized commercial use prohibited.

© 2024 Yescrypt. All rights reserved.
