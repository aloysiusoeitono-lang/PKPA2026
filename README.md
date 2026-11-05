# Sistem Informasi Data Anggota - Perkumpulan Keluarga Pulau Ambon (Papua Barat Daya)

## Fungsi file
- main.py      : Titik awal aplikasi, jendela utama, sidebar, header, dashboard.
- database.py  : Koneksi SQLite (PRAGMA foreign_keys=ON), pembuatan tabel otomatis, hashing password, semua fungsi CRUD (parameterized query + transaksi).
- auth.py      : Fungsi login dan halaman login.
- anggota.py   : Halaman CRUD Data Anggota.
- ikatan.py    : Halaman CRUD Data Ikatan (+ jumlah anggota per ikatan).
- user.py      : Halaman CRUD Data User + ubah password.
- laporan.py   : Laporan per ikatan, cetak, export Excel dan PDF.
- widgets.py   : Warna, tombol, dan tabel bersama.
- perkumpulan_ambon.db : Database (dibuat ulang otomatis jika dihapus).

## Instalasi
1. Install Python 3.9+ (Windows: centang "Add Python to PATH"; tkinter sudah termasuk).
2. Buka terminal di folder ini lalu jalankan:  pip install -r requirements.txt

## Menjalankan
    python main.py

## Login pertama
Kode user: admin  |  Password: admin123
Segera ganti password lewat menu Data User > pilih admin > isi password baru > Ubah Password.

## Anggota
- Tambah ikatan dulu di menu Data Ikatan.
- Data Anggota: isi formulir (tanggal DD-MM-YYYY), pilih ikatan, klik Tambah.
- Ubah: klik baris di tabel, edit, klik Ubah. Hapus: klik baris, klik Hapus, konfirmasi.
- Bersihkan: kosongkan formulir untuk data baru. Kolom cari: nama atau kode.

## Laporan
Menu Laporan Anggota > pilih ikatan (atau SEMUA IKATAN) > TAMPILKAN LAPORAN.
Lalu CETAK LAPORAN (ke printer default), EXPORT EXCEL (.xlsx), atau EXPORT PDF.
