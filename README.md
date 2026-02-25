# IGNORANT PRO v4.0

### Telefon raqam OSINT CLI vositasi

IGNORANT PRO — bu telefon raqamning turli onlayn platformalarda ro‘yxatdan o‘tgan-o‘tmaganini tekshiruvchi buyruq qatori (CLI) asosidagi OSINT vosita. Natijada avtomatik hisobot (report) fayl ham yaratadi.

---

## Imkoniyatlari

* Telefon raqamni **12 ta platformada** tekshiradi
* Qaysi servisda ishlatilganini aniqlaydi
* Timeout, xatolik va boshqa holatlarni ko‘rsatadi
* **Avtomatik report fayl** saqlaydi
* Oddiy va tez CLI ishlatish

---

## O‘rnatish

Repository’ni yuklab oling:

```
git clone https://github.com/Yescrypt/ignorantpro.git
cd ignorantpro
```

Virtual muhit (tavsiya etiladi):

```
python3 -m venv venv
source venv/bin/activate
```

Kutubxonalarni o‘rnating:

```
pip install -r requirements.txt
```

---

## Ishlatish

Oddiy buyruq:

```
python3 ignorant_pro.py +998901234567
```

Tekshiruv tugagach, report fayl avtomatik saqlanadi.

---

## Output Legend

```
[+] Topildi        → raqam servisda ishlatilgan
[-] Ishlatilmagan  → ro‘yxatdan o‘tmagan
[x] Rate limit     → servis so‘rovni chekladi
[t] Timeout        → javob kelmadi
[?] Error          → noma’lum xatolik
```

---

## Author

Created by Yescrypt
Cybersecurity & OSINT Research
