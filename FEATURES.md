# IGNORANT PRO — Platform Features

Har bir platform uchun qaysi metod ishlatilayotgani va constraints'lar.

---

## 1️⃣ Instagram

| Property | Value |
|----------|-------|
| **Method** | Web signup + password reset endpoints |
| **Endpoint** | `/api/v1/users/lookup_phone_with_count/` |
| **Fallback** | `/accounts/account_recovery_send_ajax/` |
| **Headers** | X-CSRFToken, X-Instagram-AJAX |
| **Indicators** | `user_id`, `count`, `obfuscated_phone` |
| **Reliability** | ⚠️ Medium (API tez o'zgaradi) |
| **Rate Limit** | 429 — Expect delays |
| **Notes** | Phone number validation only, username yo'q |

---

## 2️⃣ Telegram

| Property | Value |
|----------|-------|
| **Method** | my.telegram.org API |
| **Endpoint** | `https://my.telegram.org/auth/send_password` |
| **Response** | Plain text "OK" yoki JSON |
| **Indicators** | "OK", "sent", "FLOOD" |
| **Reliability** | ✅ High |
| **Rate Limit** | "FLOOD" → Rate limit |
| **Notes** | Username resolution kerak (TODO) |

---

## 3️⃣ TikTok

| Property | Value |
|----------|-------|
| **Method** | Passport mobile endpoint |
| **Endpoint** | `/passport/mobile/check_unique/` |
| **Post Data** | `mobile`, `area_code`, `aid` |
| **Indicators** | `message_code: 2` (band), `is_unique: 0/1` |
| **Reliability** | ⚠️ Medium (geo-check bo'ladi) |
| **Geo-Block** | VPN kerak bo'lishi mumkin |
| **Notes** | Area code ajratish muhim |

---

## 4️⃣ WhatsApp

| Property | Value |
|----------|-------|
| **Method** | Click-to-chat API |
| **Endpoint** | `https://api.whatsapp.com/send/?phone=...` |
| **Response** | HTML page redirect |
| **Indicators** | "Continue to Chat", "open_app" |
| **Negative** | "invalid", "phone number shared via url is invalid" |
| **Reliability** | ✅ High |
| **Rate Limit** | Not strict |
| **Notes** | Username/profile yo'q, faqat presence |

---

## 5️⃣ Snapchat

| Property | Value |
|----------|-------|
| **Method** | Password reset form |
| **Endpoint** | `/accounts/password_reset_request` |
| **Token** | XTS token (from form) |
| **Indicators** | Location redirect: `confirmation`, `success` |
| **Reliability** | ✅ Good |
| **Rate Limit** | Not strict |
| **Notes** | Redirect header tekshirish muhim |

---

## 6️⃣ Twitter / X

| Property | Value |
|----------|-------|
| **Method** | Onboarding flow API (v1.1) |
| **Endpoint** | `/i/flow/password_reset` (KULI ENDPOINT) |
| **Token** | Guest token (from `/guest/activate.json`) |
| **Bearer** | Public bearer token (hardcoded) |
| **Response** | JSON flow tasks |
| **Indicators** | `SelectAuthMethod`, `ChooseIdentifier`, `PasswordReset` subtasks |
| **Error Codes** | 141 = not found, 32 = bad param |
| **Reliability** | ✅ Good |
| **Rate Limit** | 429 — strict |
| **Notes** | 2024 yangi API, stable |

---

## 7️⃣ Viber

| Property | Value |
|----------|-------|
| **Method** | Account recovery flow |
| **Endpoint** | `https://account.viber.com/en/forgot-password` |
| **Token** | CSRF token (form'dan) |
| **Response** | HTML + optional redirect |
| **Indicators** | Redirect location: `check`, `sent`, `success` |
| **Reliability** | ✅ Good |
| **Rate Limit** | Not strict |
| **Notes** | Text response tekshirish kerak |

---

## 8️⃣ Amazon

| Property | Value |
|----------|-------|
| **Method** | /ap/forgotpassword endpoint |
| **Endpoint** | `https://www.amazon.com/ap/forgotpassword` |
| **Token** | appActionToken, metadata1 (from form) |
| **Indicators** | "We found your account" |
| **Reliability** | ⚠️ Medium (session kerak bo'lishi mumkin) |
| **Rate Limit** | Not strict |
| **Notes** | Email field ishlaydi (phone ham test qilinadi) |

---

## 9️⃣ Microsoft

| Property | Value |
|----------|-------|
| **Method** | GetCredentialType SRF endpoint |
| **Endpoint** | `https://login.live.com/GetCredentialType.srf` |
| **Token** | uaid, sCtx, flowToken (from login page) |
| **Response** | JSON IfExistsResult |
| **Codes** | 0 = exists, 1 = not found, 6 = federated |
| **Reliability** | ✅ High |
| **Rate Limit** | 5 = throttled |
| **Notes** | Most reliable yo'nalishlaridan |

---

## 🔟 OLX.uz

| Property | Value |
|----------|-------|
| **Method** | Auth OTP endpoint |
| **Endpoint** | `https://www.olx.uz/api/open/auth/otp/` |
| **Format** | `{"phone": "+99899..."}` |
| **Response** | JSON |
| **Indicators** | `isRegistered: true` |
| **Reliability** | ✅ High (O'zbekistonda qo'l) |
| **Rate Limit** | Not strict |
| **Notes** | Only for Uzbek numbers (+998) |

---

## 1️⃣1️⃣ LinkedIn

| Property | Value |
|----------|-------|
| **Method** | Password reset form |
| **Endpoint** | `/uas/request-password-reset` |
| **Token** | csrfToken, pageInstance |
| **Response** | HTML + redirect |
| **Indicators** | Redirect: `checkYourEmail`, text: "Check your email" |
| **Reliability** | ✅ Good |
| **Rate Limit** | Not strict |
| **Notes** | Email va phone ikkalasi ishlaydi |

---

## 1️⃣2️⃣ Google

| Property | Value |
|----------|-------|
| **Method** | Signin identifier flow |
| **Endpoint** | `/v3/signin/_/AccountsSignInUi/data/batchexecute` |
| **Token** | GALX, sCtx, at token |
| **Response** | JSON array (protobuf-like) |
| **Indicators** | Text: `myaccount`, `SelectAuthMethod` |
| **Reliability** | ⚠️ Low (reCAPTCHA ko'p) |
| **Rate Limit** | 429 — strict |
| **CAPTCHA** | Often required |
| **Notes** | Eng murakkab, most errors |

---

## 📊 Comparison Table

| Platform | Speed | Reliability | Rate Limit | Notes |
|----------|-------|-------------|-----------|-------|
| Telegram | ⚡⚡⚡ | ✅✅✅ | Medium | Best overall |
| Microsoft | ⚡⚡ | ✅✅✅ | Medium | Reliable |
| WhatsApp | ⚡⚡ | ✅✅ | Low | Simple API |
| Twitter | ⚡⚡ | ✅✅ | High | Strict rate limit |
| Instagram | ⚡ | ⚠️ | High | API unstable |
| TikTok | ⚡ | ⚠️ | Medium | Geo-blocks |
| Google | ⚡ | ⚠️ | Highest | CAPTCHA + rate limit |

---

## 🚀 Performance Tips

### For Faster Checks
```bash
# Only reliable platforms
python3 ignorant_pro.py +998941350269 --only Telegram,Microsoft,WhatsApp
```

### For Comprehensive Check
```bash
# All platforms (slow)
python3 ignorant_pro.py +998941350269
```

### With VPN (For Geo-Blocked)
```bash
# TikTok, Instagram, Google kerak bo'lsa
export HTTP_PROXY=socks5://127.0.0.1:1080
python3 ignorant_pro.py +998941350269
```

---

## 🔒 False Positive Risk

| Risk Level | Platforms |
|-----------|-----------|
| **Low** | Telegram, Microsoft, WhatsApp |
| **Medium** | Twitter, OLX.uz, LinkedIn, Snapchat |
| **High** | Instagram, TikTok, Google |

---

## 📝 Notes

- Barcha check'lar **OSINT qonuni** doirasida
- Hech qanday **brute force** yo'q
- **Rate limiting** haram qayd qilinadi
- **User-Agent spoofing** only for legitimacy
- **No credential theft** — just verification

---

## 🔄 Updates

Ushbu tasnif v4.1 uchun. Endpoint'lar tez o'zgarishi mumkin.

---

**Last Updated:** 2024-12-20
**Version:** 4.1
