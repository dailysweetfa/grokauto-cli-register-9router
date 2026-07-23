<div align="center">

# 🤖 Grok Register - Auto Registration Toolkit 🤖

[![Grok Register — GUI and CLI registration automation toolkit](assets/banner.png)](https://github.com/AaronL725/grok-register)

**Grok Register** adalah alat otomatisasi pendaftaran akun Grok (x.ai) berbasis Python yang mendukung antarmuka visual (**GUI**) maupun terminal (**CLI**). Dilengkapi dengan penanganan Cloudflare Turnstile, dukungan email sementara, dan integrasi otomatis ke pool **9Router**.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.14-3776AB.svg?style=flat-square&logo=python" alt="Python 3.14">
  <img src="https://img.shields.io/badge/OS-Windows-0078D6.svg?style=flat-square&logo=windows" alt="Windows Only">
  <img src="https://img.shields.io/badge/Interface-GUI%20%2B%20CLI-success.svg?style=flat-square" alt="GUI + CLI">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square" alt="License: MIT">
</p>

<p align="center">
  <a href="https://store.ayricreative.com/produk/grok-auto-register-apikey">
    <img src="https://img.shields.io/badge/🛒%20Beli%20Lisensi%20Resmi-Ayri%20Creative%20Store-10b981?style=for-the-badge&logo=shopping-bag" alt="Beli Lisensi Resmi">
  </a>
</p>

</div>

---

### 🔑 Pembelian Lisensi Resmi
Untuk mendapatkan kunci lisensi aktivasi program ini, silakan melakukan pembelian secara resmi melalui tautan Store berikut:
👉 **[https://store.ayricreative.com/produk/grok-auto-register-apikey](https://store.ayricreative.com/produk/grok-auto-register-apikey)**

---

> [!WARNING]  
> **DISCLAIMER / PERNYATAAN HUKUM**:  
> Alat ini dibuat hanya untuk tujuan penelitian otomatisasi web, pengujian integrasi sistem, dan edukasi pribadi. Harap patuhi Ketentuan Layanan (ToS) dari situs web target, undang-undang setempat, serta kebijakan penyedia pihak ketiga. Penyalahgunaan alat ini di luar tanggung jawab pengembang.

---

## ⚡ INFORMASI SANGAT PENTING (WAJIB DIBACA)

> [!IMPORTANT]
> **Sistem Operasi**: Program ini **HANYA MENDUKUNG SISTEM OPERASI WINDOWS**. Sistem operasi lain tidak didukung karena bagian logika utama program didistribusikan dalam bentuk biner terkompilasi khusus untuk Windows.

Bagian logika utama program ini (**`grok_core.pyd`**) didistribusikan dalam bentuk biner terkompilasi (C-Extension) untuk alasan keamanan lisensi dan performa. Agar program ini dapat berjalan tanpa error, pastikan perangkat Anda memenuhi syarat wajib berikut:

1. **Wajib Menggunakan Python 3.14.x (64-bit)**
   * Biner `grok_core.pyd` dikompilasi secara khusus menggunakan **Python 3.14**. Jika Anda menggunakan Python versi lain (seperti 3.10, 3.11, atau 3.12), program akan memunculkan error `DLL load failed`.
2. **Wajib Memasang Microsoft Visual C++ Redistributable**
   * PC Windows memerlukan komponen runtime ini untuk memuat biner `.pyd` terkompilasi. Tanpa ini, program tidak akan bisa mendeteksi modul utama.

---

## 📦 Bahan-Bahan yang Wajib Diinstal

Sebelum menjalankan program, unduh dan pasang bahan-bahan di bawah ini:

| Nama Bahan | Deskripsi & Fungsi | Link Unduhan Resmi |
| :--- | :--- | :--- |
| **Python 3.14.x** | Mesin utama untuk menjalankan skrip. **Wajib versi 3.14**! | 📥 [Download Python 3.14.3 (Windows x64)](https://www.python.org/ftp/python/3.14.3/python-3.14.3-amd64.exe) |
| **VC++ Runtime** | Pustaka Windows agar file biner `.pyd` dapat dimuat. | 📥 [Download VC++ Redistributable (x64)](https://aka.ms/vs/17/release/vc_redist.x64.exe) |
| **Google Chrome** | Browser nyata yang digunakan oleh bot untuk memproses pendaftaran. | 📥 [Download Google Chrome Resmi](https://www.google.com/chrome/) |

---

## 🚀 Panduan Pemasangan Lengkap (Untuk Pemula)

Ikuti langkah-langkah mudah berikut dari awal sampai siap pakai:

### Langkah 1: Instalasi Python 3.14
1. Buka file installer Python 3.14 yang sudah Anda unduh.
2. ⚠️ **PENTING**: Di bagian bawah jendela installer, beri centang pada kotak **"Add python.exe to PATH"**. Jika Anda tidak mencentangnya, perintah `python` tidak akan dikenali di CMD.
3. Klik **"Install Now"** dan tunggu hingga proses selesai.

### Langkah 2: Instalasi Microsoft Visual C++ Redistributable
1. Jalankan installer `vc_redist.x64.exe`.
2. Centang kotak persetujuan lisensi (*I agree*), lalu klik **"Install"**.
3. Jika meminta restart PC setelah instalasi, silakan restart PC Anda terlebih dahulu.

### Langkah 3: Ekstrak File Program
1. Ekstrak file ZIP program ini ke dalam satu folder (misalnya di `D:\grok-register`).
2. Pastikan file **`grok_core.pyd`** dan **`grok_register_ttk.py`** berada di dalam satu folder yang sama.

### Langkah 4: Pemasangan Library Pendukung (Dependencies)
1. Buka folder tempat Anda mengekstrak program.
2. Klik pada bilah alamat (address bar) di bagian atas Windows Explorer, ketik `cmd`, lalu tekan **Enter**. Ini akan membuka Command Prompt langsung di direktori program.
3. Ketik perintah berikut di CMD lalu tekan **Enter**:
   ```bash
   pip install -r requirements.txt
   ```
4. Tunggu hingga semua library selesai diunduh dan dipasang secara otomatis.

### Langkah 5: Menyiapkan File Konfigurasi
1. Cari file bernama `config.example.json` di folder program.
2. Salin (*Copy*) file tersebut dan ubah namanya (*Rename*) menjadi **`config.json`**.
3. Buka file `config.json` menggunakan **Notepad** untuk mengonfigurasi provider email atau menyetel lisensi Anda.

---

## ⚙️ Konfigurasi Provider Email (di `config.json`)

Program ini hanya mendukung 2 penyedia email berkualitas tinggi untuk tingkat keberhasilan pendaftaran maksimal:

### 1. AyriMail (Bawaan - Direkomendasikan ⭐)
Provider email berkecepatan tinggi yang dirancang khusus untuk registrasi akun Grok/xAI.
* **Pengaturan di `config.json`**:
  ```json
  "email_provider": "ayrimail",
  "ayrimail_api_base": "https://app.ayrimail.web.id",
  "ayrimail_api_key": "API_KEY_ANDA",
  "ayrimail_domain": "random"
  ```

### 2. Temp Mail Pribadi (Cloudflare Worker)
Menggunakan domain kustom pribadi Anda di Cloudflare Worker. Tingkat kesuksesan pendaftaran mencapai **99%** karena domain bersih dari blokir sistem x.ai.
* **Pengaturan di `config.json`**:
  ```json
  "email_provider": "cloudflare",
  "cloudflare_api_base": "https://worker-domain-anda.dev",
  "cloudflare_api_key": "",
  "cloudflare_auth_mode": "none",
  "defaultDomains": "domain-pribadi-anda.com"
  ```

---

## 🔌 Integrasi Otomatis ke 9Router (Opsional)

Jika customer/pengguna Anda menggunakan aplikasi **9Router** untuk mengelola koneksi Grok/xAI, bot dapat menyinkronkan dan menguji akun baru secara otomatis:

1. Buka file `config.json`.
2. Masukkan URL dan Password 9Router masing-masing pengguna pada bagian:
   ```json
   "ROUTER9_URL": "http://localhost:20128",
   "ROUTER9_PASS": "kata_sandi_9router_pengguna"
   ```
3. **Fitur Otomatis 9Router**:
   - **Sinkronisasi Otomatis**: Setiap kali pendaftaran 1 akun selesai, biner token akan langsung masuk ke database 9Router lokal.
   - **Auto-Cleanup Error**: Bot akan secara otomatis mendeteksi dan menghapus akun mati (`401` / `402`) serta mereset status `403` / `429` menjadi `success` di 9Router tanpa perlu penanganan manual.

---

## 💻 Cara Menjalankan Program

Program ini mendukung dua cara pengoperasian:

### A. Tampilan GUI (Visual - Mudah)
Cara paling mudah untuk pengguna umum.
1. Klik ganda langsung pada file **`grok_register_ttk.py`** di Windows Explorer, ATAU ketik di CMD:
   ```bash
   python grok_register_ttk.py
   ```
2. Pilih **Email Provider** pada menu drop-down.
3. Tentukan **Jumlah Registrasi (Register Count)** dan jumlah tab berjalan (**Concurrent Count**).
4. Klik tombol **Mulai (Start)**. Proses pendaftaran akan berjalan otomatis di browser Chrome.

### B. Tampilan CLI (Terminal - Hemat Resource)
Cocok untuk dijalankan pada Windows Server atau eksekusi pendaftaran massal tanpa grafis.
1. Jalankan perintah ini di CMD:
   ```bash
   python grok_register_ttk.py cli
   ```
2. Ketik perintah `start` lalu tekan **Enter** setelah terminal siap.
3. Tekan tombol `Ctrl + C` untuk menghentikan proses secara aman.

---

## 🔍 Mengatasi Error yang Sering Terjadi (Troubleshooting)

#### ❓ Error: `ImportError: DLL load failed while importing grok_core`
* **Solusi**:
  1. Periksa kembali versi Python Anda dengan mengetik `python --version` di CMD. Pastikan hasilnya adalah **Python 3.14.x**. Jika bukan 3.14, hapus versi Python lama Anda dan instal ulang Python 3.14.3 melalui tautan di atas.
  2. Pastikan Anda telah menginstal **Microsoft Visual C++ Redistributable** dan sudah merestart PC Anda.

#### ❓ Error: `'python' is not recognized as an internal or external command`
* **Solusi**: Anda lupa mencentang pilihan **"Add python.exe to PATH"** saat menginstal Python. Buka installer Python kembali, pilih opsi *Modify*, dan centang pilihan tersebut.

---

## 💾 Lokasi File Hasil Pendaftaran

Setelah bot berhasil membuat akun, data akan tersimpan langsung di folder aplikasi:
* **`accounts_*.txt`** — Menyimpan hasil dalam format: `email----password----SSO_Token` (Format default ekspor).
* **`tokens.txt`** — Hanya menyimpan daftar token akses SSO untuk keperluan integrasi API.
* **`cpa_auths/`** — Folder berisi kredensial file CPA xAI dalam format JSON untuk digunakan langsung di 9Router.
