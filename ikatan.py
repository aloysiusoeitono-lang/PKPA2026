"""ikatan.py - Halaman CRUD Data Ikatan."""
from tkinter import messagebox
import customtkinter as ctk
import database as db
from widgets import judul, tombol, buat_tabel, isi_tabel, DANGER, ACCENT, CARD, FONT


class IkatanPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        judul(self, "DATA IKATAN", "Kelola Daftar Ikatan/Kelompok/Kerukunan").pack(anchor="w", pady=(0, 12))

        form = ctk.CTkFrame(self, fg_color=CARD, corner_radius=12)
        form.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(form, text="Kode Ikatan", font=(FONT, 12)).grid(row=0, column=0, padx=12, pady=12, sticky="w")
        self.e_kode = ctk.CTkEntry(form, width=160)
        self.e_kode.grid(row=0, column=1, padx=6)
        ctk.CTkLabel(form, text="Nama Ikatan", font=(FONT, 12)).grid(row=0, column=2, padx=12, sticky="w")
        self.e_nama = ctk.CTkEntry(form, width=320)
        self.e_nama.grid(row=0, column=3, padx=6)

        bar = ctk.CTkFrame(form, fg_color="transparent")
        bar.grid(row=1, column=0, columnspan=4, sticky="w", padx=12, pady=(0, 12))
        tombol(bar, "Tambah", self.tambah).pack(side="left", padx=(0, 6))
        tombol(bar, "Ubah", self.ubah, ACCENT, "#A87A2E").pack(side="left", padx=6)
        tombol(bar, "Hapus", self.hapus, DANGER, "#8E2E3A").pack(side="left", padx=6)
        tombol(bar, "Bersihkan", self.bersih, "#6B7280", "#4B5563").pack(side="left", padx=6)

        cari = ctk.CTkFrame(self, fg_color="transparent")
        cari.pack(fill="x", pady=(0, 8))
        self.e_cari = ctk.CTkEntry(cari, width=300, placeholder_text="Cari kode atau nama ikatan...")
        self.e_cari.pack(side="left")
        self.e_cari.bind("<KeyRelease>", lambda e: self.muat())
        tombol(cari, "Cari", self.muat).pack(side="left", padx=6)

        f, self.tree = buat_tabel(self, [("kode", "Kode Ikatan", 150), ("nama", "Nama Ikatan", 400),
                                         ("jml", "Jumlah Anggota", 150)])
        f.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.pilih)
        self.muat()

    def refresh(self):
        self.muat()

    def muat(self):
        try:
            rows = db.ikatan_list(self.e_cari.get().strip())
        except db.DatabaseError as e:
            return messagebox.showerror("Kesalahan", str(e))
        isi_tabel(self.tree, [(r["kode_ikatan"], r["nama_ikatan"], r["jumlah"]) for r in rows])

    def pilih(self, _=None):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0], "values")
        self.bersih(keep_sel=True)
        self.e_kode.insert(0, v[0])
        self.e_kode.configure(state="disabled")
        self.e_nama.insert(0, v[1])

    def bersih(self, keep_sel=False):
        self.e_kode.configure(state="normal")
        self.e_kode.delete(0, "end")
        self.e_nama.delete(0, "end")
        if not keep_sel:
            self.tree.selection_remove(self.tree.selection())

    def _valid(self):
        kode, nama = self.e_kode.get().strip().upper(), self.e_nama.get().strip().upper()
        if not kode:
            messagebox.showwarning("Validasi", "Kode Ikatan tidak boleh kosong.")
            return None
        if not nama:
            messagebox.showwarning("Validasi", "Nama Ikatan tidak boleh kosong.")
            return None
        return kode, nama

    def tambah(self):
        if self.e_kode.cget("state") == "disabled":
            return messagebox.showinfo("Info", "Klik 'Bersihkan' terlebih dahulu untuk menambah data baru.")
        v = self._valid()
        if not v:
            return
        try:
            db.ikatan_tambah(*v)
            messagebox.showinfo("Berhasil", "Data Ikatan berhasil ditambahkan.")
            self.bersih(); self.muat()
        except db.DatabaseError as e:
            messagebox.showerror("Gagal", str(e))

    def ubah(self):
        if self.e_kode.cget("state") != "disabled":
            return messagebox.showwarning("Info", "Pilih data Ikatan pada tabel terlebih dahulu.")
        v = self._valid()
        if not v:
            return
        try:
            db.ikatan_ubah(*v)
            messagebox.showinfo("Berhasil", "Data Ikatan berhasil diubah.")
            self.bersih(); self.muat()
        except db.DatabaseError as e:
            messagebox.showerror("Gagal", str(e))

    def hapus(self):
        if self.e_kode.cget("state") != "disabled":
            return messagebox.showwarning("Info", "Pilih data Ikatan pada tabel terlebih dahulu.")
        kode = self.e_kode.get()
        if not messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus Ikatan {kode}?"):
            return
        try:
            db.ikatan_hapus(kode)
            messagebox.showinfo("Berhasil", "Data Ikatan berhasil dihapus.")
            self.bersih(); self.muat()
        except db.DatabaseError as e:
            messagebox.showerror("Gagal", str(e))
