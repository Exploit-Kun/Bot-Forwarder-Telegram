# 🤖 Telegram Message Forwarder Bot - Nexa Tools v1.0

Bot Telegram berbasis Python yang digunakan untuk memforward pesan dari **Saved Messages** (akun sendiri) ke beberapa grup secara otomatis dan berkala. Kontrol penuh dilakukan melalui **admin Telegram** dengan perintah yang dikirimkan langsung ke bot.

---

## 🚀 Fitur
- Auto join grup dengan link `t.me/...`
- Perintah admin melalui chat
- Menyimpan dan membersihkan daftar grup
- Forward otomatis setiap 60 menit
- Menampilkan status, waktu terkirim, daftar grup, dll.

---

## 🧩 File
- `broadcast.py` → Bot utama, jalankan ini.
- `cek-id.py` → Ambil ID pesan dan ID admin Telegram Anda.

---

## 🛠️ Instalasi & Jalankan

### 1. Kloning Repositori
```bash
git clone https://github.com/username/telegram-forward-bot.git
cd telegram-forward-bot

## ⚙️ Konfigurasi

1. Dapatkan `API_ID` dan `API_HASH` dari [my.telegram.org](https://my.telegram.org)
2. Edit bagian ini di `broadcast.py` dan `cek-id.py`:

```python
API_ID = 'ISI API_ID ANDA'
API_HASH = 'ISI API_HASH ANDA'
ADMIN_ID = 123456789         # ID Telegram Anda
MESSAGE_IDS = [9999999]      # ID pesan dari Saved Messages

