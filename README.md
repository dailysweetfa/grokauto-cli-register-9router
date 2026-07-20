<div align="center">

[![Grok Register — GUI and CLI registration automation toolkit](assets/banner.png)](https://github.com/AaronL725/grok-register)

Grok Register adalah sebuah alat registrasi otomatis Python yang ditujukan untuk penelitian alur otomatisasi, verifikasi lingkungan pengujian, dan pembelajaran pribadi — mendukung GUI / CLI, email sementara, kontrol alur browser, output akun, dan penulisan token pool grok2api.

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="Lisensi: MIT"></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB.svg" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/Interface-GUI%20%2B%20CLI-success.svg" alt="GUI + CLI">
  <img src="https://img.shields.io/badge/Browser-Chromium%2FChrome-4285F4.svg" alt="Chromium/Chrome">
  <a href="http://makeapullrequest.com"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>

</p>



</div>

---

> Proyek ini hanya digunakan untuk penelitian alur otomatisasi, verifikasi lingkungan pengujian, dan pembelajaran pribadi. Harap patuhi ketentuan layanan situs web target, hukum dan peraturan setempat, serta batasan layanan pihak ketiga.

## Daftar Isi

- [Fitur](#fitur)
- [Persyaratan Sistem](#persyaratan-sistem)
- [Instalasi](#instalasi)
- [Konfigurasi](#konfigurasi)
- [Cara Menjalankan](#cara-menjalankan)
- [File Output](#file-output)
- [Mekanisme Stabilitas](#mekanisme-stabilitas)
- [Pertanyaan yang Sering Diajukan (FAQ)](#pertanyaan-yang-sering-diajukan-faq)
- [Struktur Direktori](#struktur-direktori)
- [Lisensi](#lisensi)


## Fitur

- Mendukung berjalan menggunakan antarmuka grafis GUI.
- Mendukung berjalan melalui terminal CLI tanpa meluncurkan GUI Tkinter.
- Alur registrasi diselesaikan menggunakan halaman browser Chromium/Chrome.
- Mendukung banyak worker secara bersamaan (`concurrent_count`), di mana setiap worker memiliki browser independen dan profil terisolasi.
- Mendukung antarmuka email sementara dari DuckMail, YYDS, dan Cloudflare.
- Mendukung polling dan penguraian email kode verifikasi.
- Mendukung penulisan akun sukses secara real-time ke file `accounts_*.txt`.
- Mendukung penulisan SSO token ke pool grok2api lokal maupun remote.
- Mendukung upaya mengaktifkan NSFW setelah pendaftaran.
- Mendukung ekspor kredensial CPA xAI secara asinkron (secara default menggunakan browser mint terpisah, tidak mengganggu halaman pendaftaran).
- Mendukung pengaturan level log (`quiet` / `info` / `debug`) dan statistik kecepatan pembuatan per menit.
- Mendukung pendeteksian halaman macet, percobaan ulang akun saat ini, restart browser per akun, dan pembersihan memori.

## Persyaratan Sistem

- Python 3.9+
- Google Chrome atau Chromium
- Lingkungan jaringan yang dapat mengakses halaman pendaftaran dan API email sementara

## Instalasi

Unduh proyek ke komputer Anda:

```bash
git clone https://github.com/maxucheng0/grok-register.git
cd grok-register
```

Instal dependensi:

```bash
pip install -r requirements.txt
```

Salin file konfigurasi:

```bash
cp config.example.json config.json
```

Kemudian edit `config.json` sesuai kebutuhan Anda.

## Konfigurasi

Beberapa opsi konfigurasi yang sering digunakan:

| Kunci Konfigurasi | Deskripsi |
| --- | --- |
| `email_provider` | Penyedia layanan email: `duckmail`, `yyds`, `cloudflare` |
| `register_count` | Jumlah target pendaftaran untuk sesi saat ini |
| `proxy` | Alamat proxy, dapat dikosongkan jika tidak ada |
| `enable_nsfw` | Apakah akan mencoba mengaktifkan NSFW setelah pendaftaran selesai |
| `cloudflare_api_base` | Alamat API email sementara Cloudflare |
| `cloudflare_api_key` | Kunci API email sementara Cloudflare; biarkan kosong untuk mode anonim bawaan, isi dengan `ADMIN_PASSWORD` untuk mode admin |
| `cloudflare_auth_mode` | Mode autentikasi API Cloudflare; default `none`, pilihan lainnya `bearer`, `x-api-key`, `x-admin-auth`, `query-key` |
| `cloudflare_path_domains` | Jalur daftar domain Cloudflare; default `/api/domains` |
| `cloudflare_path_accounts` | Jalur pembuatan email Cloudflare; default `/api/new_address` untuk mode anonim, `/admin/new_address` untuk mode admin |
| `cloudflare_path_token` | Jalur token Cloudflare; default `/api/token` |
| `cloudflare_path_messages` | Jalur pesan email masuk Cloudflare; default `/api/mails` |
| `defaultDomains` | Domain email default Cloudflare |
| `grok2api_auto_add_local` | Apakah akan menulis token ke pool grok2api lokal |
| `grok2api_local_token_file` | Jalur file token grok2api lokal |
| `grok2api_auto_add_remote` | Apakah akan menulis token ke grok2api remote |
| `grok2api_remote_base` | Alamat remote grok2api, bisa diisi alamat situs utama atau alamat API manajemen `/admin/api` |
| `grok2api_remote_app_key` | App key grok2api remote |
| `concurrent_count` | Jumlah worker paralel; `1` untuk pendaftaran berurutan menggunakan satu browser, `>1` untuk paralel multi-browser |
| `browser_restart_every` | Interval restart browser berkala tambahan (berdasarkan jumlah akun); **browser akan tetap direstart penuh setelah setiap akun selesai** untuk menghindari sisa sesi |
| `cpa_export_enabled` | Apakah akan mengekspor kredensial CPA xAI setelah pendaftaran sukses |
| `cpa_mint_async` | Apakah akan menggunakan proses asinkron untuk mint CPA (default `true`: browser terpisah + thread latar belakang, tidak memblokir pendaftaran akun berikutnya) |
| `cpa_probe_after_write` | Apakah akan memverifikasi kegunaan antarmuka setelah menulis file CPA |
| `log_level` | Level log: `quiet` / `info` (default) / `debug`; level `info` akan menyembunyikan log diagnosa `[Debug]` frekuensi tinggi |
| `speed_log_interval_sec` | Interval waktu (dalam detik) statistik kecepatan pembuatan, default `60`; output berupa `Sukses 9/min` |
| `browser_use_custom_ua` | Apakah akan memaksa penggunaan UA kustom dalam konfigurasi (default `false`, agar lebih mendekati Chrome asli) |
| `token_only_file` | Jalur file tambahan untuk menulis token SSO saja, dapat dikosongkan |

### Mode Anonim Email Sementara Cloudflare (Default)

Secara default, Cloudflare email menggunakan antarmuka anonim dari `dreamhunter2333/cloudflare_temp_email` untuk membuat email dan membaca pesan masuk:

- Membuat email: `POST /api/new_address`
- Membaca email: `GET /api/mails`
- Mode autentikasi: `none`
- `cloudflare_api_key`: Biarkan kosong

Ini adalah opsi default untuk proyek ini. Jika tidak ada kebutuhan khusus, gunakan konfigurasi berikut:

```json
{
  "email_provider": "cloudflare",
  "cloudflare_api_base": "https://domain-api-worker-anda.dev",
  "cloudflare_api_key": "",
  "cloudflare_auth_mode": "none",
  "cloudflare_path_domains": "/api/domains",
  "cloudflare_path_accounts": "/api/new_address",
  "cloudflare_path_token": "/api/token",
  "cloudflare_path_messages": "/api/mails",
  "defaultDomains": "domain-penerima-email-anda.com"
}
```

### Mode Admin Email Sementara Cloudflare (Opsional)

Jika Anda menggunakan `dreamhunter2333/cloudflare_temp_email` dan antarmuka anonim `/api/new_address` mengaktifkan proteksi Turnstile, Anda dapat beralih ke antarmuka pembuatan email admin:

```json
{
  "email_provider": "cloudflare",
  "cloudflare_api_base": "https://domain-api-worker-anda.dev",
  "cloudflare_api_key": "ADMIN_PASSWORD_ANDA",
  "cloudflare_auth_mode": "x-admin-auth",
  "cloudflare_path_accounts": "/admin/new_address",
  "cloudflare_path_messages": "/api/mails",
  "defaultDomains": "domain-penerima-email-anda.com"
}
```

Pembuatan email akan memanggil `/admin/new_address` menggunakan autentikasi `x-admin-auth`, sedangkan pembacaan email masuk berikutnya tetap menggunakan token JWT alamat yang dikembalikan oleh antarmuka untuk memanggil `/api/mails`. Dengan demikian, kata sandi admin hanya digunakan untuk membuat email, bukan untuk membaca pesan masuk.

Anda dapat memverifikasi antarmuka pembuatan admin terlebih dahulu menggunakan skrip debugging:

```bash
python cf_mail_debug.py --api-base "https://domain-api-worker-anda.dev" --auth-mode x-admin-auth --api-key "ADMIN_PASSWORD_ANDA" --create-path /admin/new_address --domain "domain-penerima-email-anda.com"
```

### Konfigurasi Remote Pool grok2api

Jika mengaktifkan `grok2api_auto_add_remote`, `grok2api_remote_base` dapat diisi dengan alamat situs utama, atau langsung diisi dengan alamat API manajemen:

```json
{
  "grok2api_auto_add_remote": true,
  "grok2api_remote_base": "https://domain-grok2api-anda.com",
  "grok2api_remote_app_key": "app_key_anda"
}
```

Atau:

```json
{
  "grok2api_auto_add_remote": true,
  "grok2api_remote_base": "https://domain-grok2api-anda.com/admin/api",
  "grok2api_remote_app_key": "app_key_anda"
}
```

Program akan memprioritaskan percobaan jalur `/tokens/add`, dan kompatibel dengan `/admin/api/tokens/add`; antarmuka penyimpanan penuh versi lama juga kompatibel dengan `/tokens` dan `/admin/api/tokens`.

> [!WARNING]
> File `config.json` berisi konfigurasi pribadi dan kunci API Anda. Jangan mengunggahnya ke Git.

## Cara Menjalankan

### Mode CLI

Mode CLI tidak akan membuka GUI Tkinter, tetapi alur registrasi akan tetap meluncurkan jendela browser Chromium/Chrome.

```bash
python grok_register_ttk.py cli
```

Setelah melihat perintah di terminal, masukkan:

```text
start
```

Untuk menghentikan tugas:

```text
Ctrl+C
```

Mode CLI sangat cocok untuk eksekusi massal dalam jangka waktu lama. Browser akan direstart penuh setelah setiap akun selesai diproses; selain itu, pembersihan memori runtime akan dilakukan setiap kali berhasil mendaftarkan 5 akun.

Contoh paralel (diatur di dalam `config.json`):

```json
{
  "register_count": 20,
  "concurrent_count": 3,
  "log_level": "info",
  "speed_log_interval_sec": 60
}
```

### Mode GUI

```bash
python grok_register_ttk.py
```

Mode GUI akan membuka jendela Tkinter, yang sangat cocok untuk penyesuaian konfigurasi secara manual dan pemantauan log secara visual. Log tetap difilter berdasarkan `log_level`, dan kecepatan pembuatan global akan ditampilkan secara berkala.

## File Output

Selama program berjalan, file-file berikut akan dihasilkan secara lokal:

- `accounts_*.txt`: Berisi data akun, kata sandi, dan SSO token yang sukses didaftarkan.
- `mail_credentials.txt`: Berisi kredensial email sementara.
- `cpa_auths/`: Folder berisi file JSON kredensial CPA xAI (saat `cpa_export_enabled` diaktifkan).
- `.browser_profiles/`: Direktori profil browser sementara untuk worker paralel (dibuat secara otomatis saat program berjalan, dan telah diabaikan melalui gitignore).
- `*.log`: File log opsional.

File-file tersebut mengandung data sensitif dan telah secara otomatis diabaikan oleh `.gitignore`.

## Mekanisme Stabilitas

- **Restart browser secara penuh setelah setiap akun selesai** (`restart_browser`) untuk menghindari penggunaan kembali sesi login SSO sebelumnya atau berakhir di halaman error seperti `tos-gate`.
- Worker paralel menggunakan browser Chromium terpisah dan direktori user-data yang terisolasi.
- Secara default, mint CPA asinkron berjalan di browser terpisah (`page=None`) dan tidak mengganggu tab registrasi utama.
- Deteksi halaman pemblokiran Cloudflare dan percobaan ulang membuka halaman pendaftaran.
- Pembersihan memori otomatis dilakukan setiap kali berhasil mendaftarkan 5 akun.
- Mode CLI mendukung interupsi `Ctrl+C`: penekanan pertama meminta penghentian secara elegan, penekanan kedua akan memaksa keluar dari program.
- Mencoba kembali secara otomatis jika halaman akhir tidak mengalami perubahan untuk waktu yang lama.
- Mengganti email baru secara otomatis jika kode verifikasi tidak kunjung diterima.
- Laporan statistik kecepatan pembuatan global per menit (jumlah sukses / menit).

## Pertanyaan yang Sering Diajukan (FAQ)

### Mengapa mode CLI masih membuka browser?

Mode CLI hanya berarti tidak membuka GUI Tkinter. Lingkungan browser nyata tetap diperlukan untuk memproses halaman registrasi, verifikasi Turnstile, pengiriman kode verifikasi, dan pengambilan cookie SSO.

### Pendaftaran paralel sukses di awal, tetapi kemudian memunculkan pesan tombol "Daftar dengan email" tidak ditemukan?

Penyebab umum adalah adanya sisa sesi antar akun (misalnya halaman tertahan di `grok.com/tos-gate`). Pada versi ini, browser akan direstart penuh setelah memproses setiap akun; pastikan Anda menggunakan kode terbaru dan tidak mengubah konfigurasi ke opsi "hanya hapus cookie ringan, tanpa restart browser".

### Apa yang harus dilakukan jika gagal mengaktifkan NSFW?

Jika log menampilkan `Terhambat proteksi Cloudflare, HTTP 403`, itu berarti permintaan diblokir oleh sistem perlindungan situs web target. Program akan tetap melanjutkan penyimpanan akun yang sukses dan menulisnya ke grok2api.

### Log terlalu banyak / Ingin melihat Debug?

Ubah nilai di `config.json`:

- `"log_level": "quiet"`: Hanya menampilkan progres sukses/gagal, peringatan kritis, dan statistik kecepatan.
- `"log_level": "info"`: Pengaturan default, menyembunyikan log `[Debug]`.
- `"log_level": "debug"`: Menampilkan seluruh diagnosa secara lengkap.

### Jumlah yang ditampilkan di GUI berbeda dengan file konfigurasi?

Kontrol jumlah pada GUI mungkin memiliki batas maksimum. Mode CLI akan langsung membaca nilai `register_count` yang tertera pada file `config.json`.

### Mengapa pendaftaran akun sering kali ditolak (*rejected*) atau gagal?

Domain email publik gratis (seperti bawaan Mail.tm, DuckMail, atau YYDS publik) sering kali telah terdeteksi dan masuk daftar hitam (*blacklist*) oleh sistem pendaftaran x.ai (Grok) karena tingginya volume penggunaan secara massal.
**Sangat Direkomendasikan**: Gunakan **layanan email sementara pribadi** dengan domain kustom milik Anda sendiri (misalnya, men-deploy proyek Cloudflare Temp Email menggunakan Cloudflare Workers dan domain pribadi Anda). Menggunakan domain kustom pribadi akan secara dramatis menurunkan tingkat penolakan (*rejected*) oleh sistem registrasi Grok dan meningkatkan persentase keberhasilan registrasi hingga mendekati 100%.

## Struktur Direktori

```text
.
├── grok_register_ttk.py   # Program Utama (Registrasi GUI/CLI)
├── cpa_export.py          # Ekspor CPA xAI
├── cpa_xai/               # CPA mint / OAuth / Skema
├── cf_mail_debug.py       # Alat Diagnosa Email Cloudflare
├── config.example.json    # Contoh File Konfigurasi
├── requirements.txt       # Dependensi Python
└── README.md
```

## Lisensi

Didistribusikan di bawah Lisensi [MIT](LICENSE).


