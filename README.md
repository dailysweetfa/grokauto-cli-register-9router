<div align="center">

[![Grok Register — GUI and CLI registration automation toolkit](assets/banner.png)](https://github.com/AaronL725/grok-register)

Grok Register adalah sebuah alat registrasi otomatis Python yang ditujukan untuk penelitian alur otomatisasi, verifikasi lingkungan pengujian, dan pembelajaran pribadi — mendukung GUI / CLI, email sementara, kontrol alur browser, output akun, dan penulisan token pool grok2api.

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="Lisensi: MIT"></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB.svg" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/Interface-GUI%20%2B%20CLI-success.svg" alt="GUI + CLI">
  <img src="https://img.shields.io/badge/Browser-Chromium%2FChrome-4285F4.svg" alt="Chromium/Chrome">
</p>

</div>

---

> Proyek ini hanya digunakan untuk penelitian alur otomatisasi, verifikasi lingkungan pengujian, dan pembelajaran pribadi. Harap patuhi ketentuan layanan situs web target, hukum dan peraturan setempat, serta batasan layanan pihak ketiga.

> [!NOTE]
> **Keamanan & Privasi Data**:
> Bagian inti program ini (**`grok_core.pyd`**) didistribusikan dalam bentuk **modul terkompilasi** untuk menjaga keamanan dan integritas sistem lisensi.
> Semua data hasil pendaftaran disimpan **100% secara lokal** di perangkat Anda (dalam file `accounts_*.txt` dan `tokens.txt`). Tidak ada pengiriman data ke server pihak ketiga mana pun.

## 📋 Daftar Isi

- [Pernyataan Keamanan (Disclaimer)](#-pernyataan-keamanan--antivirus-false-positive)
- [Persyaratan Sistem](#persyaratan-sistem)
- [Panduan Instalasi Cepat](#-panduan-instalasi-cepat)
- [Konfigurasi Provider Email](#%EF%B8%8F-konfigurasi-provider-email)
  - [1. Duckmail (Default)](#1-duckmail-tanpa-api-key)
  - [2. YYDS Mail](#2-yyds-mail-wajib-api-keyjwt)
  - [3. Cloudflare Temp Mail / AyriMail (Rekomendasi)](#3-cloudflare-temp-mail--ayrimail-temp-mail-pribadi)
  - [4. Mail.tm](#4-mailtm-cadangan)
- [Cara Menjalankan Aplikasi](#-cara-menjalankan-aplikasi)
- [File Hasil Output](#-file-hasil-output)
- [Fitur & Mekanisme Stabilitas](#fitur--mekanisme-stabilitas)
- [Tanya Jawab (FAQ)](#tanya-jawab-faq)
- [Struktur Direktori](#struktur-direktori)
- [Lisensi](#lisensi)

---

## Persyaratan Sistem

Sebelum memulai, pastikan komputer Anda telah terpasang:
1. **Python versi 3.9 s.d 3.13** (Direkomendasikan menggunakan Python 3.12 atau 3.13. Python 3.14 dapat memicu TLS Exception pada beberapa library).
2. **Google Chrome** atau Chromium browser.
3. **Dependensi Sistem (Khusus Pengguna Linux)**:
   * Jika ingin menggunakan mode **GUI**, Anda perlu memasang pustaka Tkinter:
     ```bash
     sudo apt-get install python3-tk
     ```
   * Pastikan Google Chrome / Chromium sudah terpasang di distro Linux Anda (misal via `apt` atau manager paket bawaan).
4. Koneksi internet yang stabil dan dapat mengakses halaman pendaftaran x.ai / Grok.

---

## 🚀 Panduan Instalasi Cepat

Ikuti langkah mudah berikut untuk memasang aplikasi:

1. **Unduh Proyek**:
   Clone repositori ini atau ekstrak file zip ke komputer Anda:
   ```bash
   git clone https://github.com/AaronL725/grok-register.git
   cd grok-register
   ```

2. **Instal Dependensi (Library pendukung)**:
   Buka terminal/CMD di folder tersebut dan jalankan:
   ```bash
   pip install -r requirements.txt
   ```

3. **Buat File Konfigurasi**:
   Salin file contoh konfigurasi menjadi file konfigurasi aktif:
   * **Windows (PowerShell)**: `cp config.example.json config.json`
   * **Windows (CMD)**: `copy config.example.json config.json`
   * **Linux/macOS**: `cp config.example.json config.json`

---

## 🛠️ Konfigurasi Provider Email

Buka file `config.json` menggunakan **Notepad** atau teks editor Anda untuk menyetel penyedia email sementara yang ingin Anda gunakan.

### 1. Duckmail (Tanpa API Key)
Opsi default yang paling praktis karena tidak memerlukan pendaftaran API Key apa pun.
* **Cara setting di `config.json`**:
  ```json
  "email_provider": "duckmail"
  ```

---

### 2. YYDS Mail (Wajib API Key/JWT)
Sangat stabil untuk pendaftaran massal. **Anda wajib memasukkan kunci API** agar tidak memicu error sistem.
* **Cara setting di `config.json`**:
  ```json
  "email_provider": "yyds",
  "yyds_api_key": "MASUKKAN_API_KEY_YYDS_ANDA_DI_SINI",
  "yyds_jwt": ""
  ```
  *(Anda bisa mendapatkan API Key dari dasbor web `mail.215.im` atau bot Telegram resmi YYDS)*.

---

### 3. Cloudflare Temp Mail / AyriMail (Temp Mail Pribadi)
**Sangat Direkomendasikan!** Menggunakan domain kustom pribadi di Cloudflare Worker akan meningkatkan tingkat kesuksesan registrasi hingga mendekati **100%** karena domain Anda bersih dari blacklist sistem pendaftaran x.ai.

* **Cara setting di `config.json` (Mode Anonim)**:
  ```json
  "email_provider": "cloudflare",
  "cloudflare_api_base": "https://domain-api-worker-anda.dev",
  "cloudflare_api_key": "",
  "cloudflare_auth_mode": "none",
  "cloudflare_path_domains": "/api/domains",
  "cloudflare_path_accounts": "/api/new_address",
  "cloudflare_path_token": "/api/token",
  "cloudflare_path_messages": "/api/mails",
  "defaultDomains": "domain-pribadi-anda.com"
  ```
* **Cara setting di `config.json` (Mode Admin)**:
  Jika pembuatan email anonim Anda diproteksi Turnstile, gunakan jalur admin dengan password:
  ```json
  "email_provider": "cloudflare",
  "cloudflare_api_base": "https://domain-api-worker-anda.dev",
  "cloudflare_api_key": "PASSWORD_ADMIN_WORKER_ANDA",
  "cloudflare_auth_mode": "x-admin-auth",
  "cloudflare_path_accounts": "/admin/new_address",
  "defaultDomains": "domain-pribadi-anda.com"
  ```

---

### 4. Mail.tm (Cadangan)
Opsi cadangan bawaan.
* **Cara setting di `config.json`**:
  ```json
  "email_provider": "mailtm"
  ```

---

## 💻 Cara Menjalankan Aplikasi

Aplikasi mendukung dua mode jalan: menggunakan tampilan visual (GUI) atau langsung dari terminal (CLI).

### A. Tampilan GUI (Sangat Direkomendasikan)
Jalankan perintah berikut di CMD/Terminal, atau klik ganda langsung file `grok_register_ttk.py` di Windows Explorer:
```bash
python grok_register_ttk.py
```
* **Langkah Penggunaan**:
  1. Pilih **Email Provider** yang diinginkan melalui menu drop-down di pojok kiri atas.
  2. Isi jumlah registrasi di kolom **Jumlah Registrasi (Register Count)**.
  3. Konfigurasikan proxy jika diperlukan di kolom **Proxy**.
  4. Klik tombol **Mulai (Start)** untuk menjalankan otomatisasi.
  5. Statistik sukses/gagal akan diperbarui secara real-time di layar.

### B. Mode CLI (Tanpa Tampilan GUI)
Cocok untuk dijalankan di server VPS atau eksekusi batch massal tanpa membuang resource grafis:
```bash
python grok_register_ttk.py cli
```
* Ketik perintah `start` di CMD setelah terminal siap untuk memulai.
* Tekan `Ctrl + C` untuk menghentikan proses pendaftaran secara elegan.

> [!TIP]
> **Menjalankan di VPS Linux / Server Headless**:
> Jika Anda menjalankan aplikasi ini di server Linux yang tidak memiliki GUI (desktop environment), pastikan Anda menyetel opsi berikut di file `config.json`:
> * Ubah `"cpa_headless"` menjadi `true` agar browser berjalan sepenuhnya di latar belakang (*headless*).
> * Jalankan aplikasi dengan mode CLI di atas.

---

## 💾 File Hasil Output

Setelah pendaftaran berjalan sukses, file hasil berikut akan tersimpan otomatis di dalam folder aplikasi:
* 📁 `accounts_*.txt` — Berisi daftar email, password, dan token SSO akun yang berhasil dibuat (Format: `email----password----SSO_Token`).
* 📁 `cpa_auths/` — Folder yang berisi file konfigurasi kredensial CPA xAI dalam format JSON.
* 📁 `mail_credentials.txt` — Berisi daftar kredensial email sementara yang pernah dibuat.

---

## Fitur & Mekanisme Stabilitas

* **Multi-Browser & Multi-Worker**: Mendukung pendaftaran paralel (`concurrent_count`) dengan profil browser yang saling terisolasi sepenuhnya.
* **Auto-Restart Browser**: Browser akan otomatis direstart penuh setelah memproses setiap akun untuk mencegah kebocoran sesi SSO.
* **Pembersihan Memori Otomatis**: Melakukan pembersihan memori runtime sistem secara berkala setelah berhasil mendaftarkan 5 akun.
* **Penyimpanan Real-time**: Token sukses dan file CPA disimpan secara instan saat itu juga, sehingga aman meskipun program tiba-tiba ditutup.

---

## Tanya Jawab (FAQ)

#### Mengapa mode CLI masih membuka browser?
Mode CLI hanya berarti tidak menampilkan jendela aplikasi GUI. Proses registrasi tetap membutuhkan browser Chromium nyata untuk memproses kode Turnstile, memuat halaman x.ai, dan memproses cookie pendaftaran secara akurat.

#### Mengapa pendaftaran akun sering ditolak (rejected)?
Layanan email publik gratis (seperti bawaan Duckmail, Mail.tm, atau YYDS publik) sering kali sudah masuk daftar hitam (*blacklist*) sistem x.ai karena pendaftaran massal oleh banyak pengguna lain. Solusi terbaik adalah menggunakan **Cloudflare Temp Email pribadi** dengan domain kustom Anda sendiri.

#### Bagaimana cara mengubah tingkat log (log level)?
Jika Anda ingin menyembunyikan pesan debug yang terlalu ramai, ubah `"log_level"` di `config.json`:
* `"quiet"`: Hanya menampilkan pesan sukses/gagal, peringatan penting, dan kecepatan.
* `"info"` (Rekomendasi): Menyembunyikan log diagnosa internal.
* `"debug"`: Menampilkan seluruh alur eksekusi secara detail.

---

## Struktur Direktori

```text
.
├── grok_register_ttk.py   # Program Utama (GUI dan CLI Wrapper)
├── grok_core.pyd          # Core Logic Engine (Modul Terkompilasi)
├── cpa_export.py          # Script Ekspor CPA xAI
├── cpa_xai/               # Modul backend CPA Mint & skema OAuth
├── cf_mail_debug.py       # Diagnosa pengujian email Cloudflare
├── config.example.json    # Templat file konfigurasi dasar
├── requirements.txt       # Daftar dependensi library Python
└── README.md              # File panduan ini
```

## Lisensi

Didistribusikan di bawah Lisensi [MIT](LICENSE).



