"""anggota.py - Halaman CRUD Data Anggota."""
from datetime import datetime
from tkinter import messagebox
import customtkinter as ctk
import database as db
from widgets import judul, tombol, buat_tabel, isi_tabel, DANGER, ACCENT, CARD, FONT


def validasi_tanggal(s):
    try:
        d = datetime.strptime(s, "%d-%m-%Y")
        return d <= datetime.now()
    except ValueError:
        return False


class AnggotaPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.ikatan_map = {}
        judul(self, "Data Anggota", "Kelola data seluruh anggota perkumpulan").pack(anchor="w", pady=(0, 12))

        form = ctk.CTkFrame(self, fg_color=CARD, corner_radius=12)
        form.pack(fill="x", pady=(0, 10))

        def lbl(t, r, c):
            ctk.CTkLabel(form, text=t, font=(FONT, 12)).grid(row=r, column=c, padx=(12, 4), pady=6, sticky="w")

        lbl("Kode Anggota", 0, 0)
        self.e_kode = ctk.CTkEntry(form, width=200); self.e_kode.grid(row=0, column=1, pady=6)
        lbl("Nama Anggota", 0, 2)
        self.e_nama = ctk.CTkEntry(form, width=260); self.e_nama.grid(row=0, column=3, pady=6)
        lbl("Tgl Lahir (DD-MM-YYYY)", 0, 4)
        self.e_tgl = ctk.CTkEntry(form, width=160, placeholder_text="31-12-1990"); self.e_tgl.grid(row=0, column=5, pady=6, padx=(0, 12))

        lbl("Jenis Kelamin", 1, 0)
        self.cb_jk = ctk.CTkOptionMenu(form, values=db.JENIS_KELAMIN_LIST, width=200); self.cb_jk.grid(row=1, column=1)
        lbl("Agama", 1, 2)
        self.cb_agama = ctk.CTkOptionMenu(form, values=db.AGAMA_LIST, width=260); self.cb_agama.grid(row=1, column=3)
        lbl("Pekerjaan", 1, 4)
        self.e_kerja = ctk.CTkEntry(form, width=160); self.e_kerja.grid(row=1, column=5, padx=(0, 12))

        lbl("Alamat", 2, 0)
        self.e_alamat = ctk.CTkEntry(form, width=460); self.e_alamat.grid(row=2, column=1, columnspan=3, sticky="w", pady=6)
        lbl("Ikatan", 2, 4)
        self.cb_ikatan = ctk.CTkOptionMenu(form, values=["-"], width=160); self.cb_ikatan.grid(row=2, column=5, padx=(0, 12))

        bar = ctk.CTkFrame(form, fg_color="transparent")
        bar.grid(row=3, column=0, columnspan=6, sticky="w", padx=12, pady=(4, 12))
        tombol(bar, "Tambah", self.tambah).pack(side="left", padx=(0, 6))
        tombol(bar, "Ubah", self.ubah, ACCENT, "#A87A2E").pack(side="left", padx=6)
        tombol(bar, "Hapus", self.hapus, DANGER, "#8E2E3A").pack(side="left", padx=6)
        tombol(bar, "Bersihkan", self.bersih, "#6B7280", "#4B5563").pack(side="left", padx=6)

        cari = ctk.CTkFrame(self, fg_color="transparent")
        cari.pack(fill="x", pady=(0, 8))
        self.e_cari = ctk.CTkEntry(cari, width=300, placeholder_text="Cari nama atau kode anggota...")
        self.e_cari.pack(side="left")
        self.e_cari.bind("<KeyRelease>", lambda e: self.muat())
        tombol(cari, "Cari", self.muat).pack(side="left", padx=6)

        kol = [("kode", "Kode Anggota", 110), ("nama", "Nama Anggota", 200), ("tgl", "Tanggal Lahir", 100),
               ("jk", "Jenis Kelamin", 100), ("agama", "Agama", 90), ("alamat", "Alamat", 220),
               ("kerja", "Pekerjaan", 130), ("ikatan", "Nama Ikatan", 160)]
        f, self.tree = buat_tabel(self, kol)
        f.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.pilih)
        self.refresh()

    def refresh(self):
        try:
            ik = db.ikatan_list()
        except db.DatabaseError as e:
            return messagebox.showerror("Kesalahan", str(e))
        self.ikatan_map = {r["nama_ikatan"]: r["kode_ikatan"] for r in ik}
        names = list(self.ikatan_map) or ["(Belum ada ikatan)"]
        self.cb_ikatan.configure(values=names)
        if self.cb_ikatan.get() not in names:
            self.cb_ikatan.set(names[0])
        self.muat()

    def muat(self):
        try:
            rows = db.anggota_list(self.e_cari.get().strip())
        except db.DatabaseError as e:
            return messagebox.showerror("Kesalahan", str(e))
        self._rows = {r["kode_anggota"]: r for r in rows}
        isi_tabel(self.tree, [(r["kode_anggota"], r["nama_anggota"], r["tanggal_lahir"], r["jenis_kelamin"],
                               r["agama"], r["alamat"], r["pekerjaan"], r["nama_ikatan"]) for r in rows])

    def pilih(self, _=None):
        sel = self.tree.selection()
        if not sel:
            return
        r = self._rows.get(self.tree.item(sel[0], "values")[0])
        if not r:
            return
        self.bersih(keep_sel=True)
        self.e_kode.insert(0, r["kode_anggota"]); self.e_kode.configure(state="disabled")
        self.e_nama.insert(0, r["nama_anggota"])
        self.e_tgl.insert(0, r["tanggal_lahir"])
        self.cb_jk.set(r["jenis_kelamin"]); self.cb_agama.set(r["agama"])
        self.e_kerja.insert(0, r["pekerjaan"] or ""); self.e_alamat.insert(0, r["alamat"] or "")
        self.cb_ikatan.set(r["nama_ikatan"])

    def bersih(self, keep_sel=False):
        self.e_kode.configure(state="normal")
        for e in (self.e_kode, self.e_nama, self.e_tgl, self.e_kerja, self.e_alamat):
            e.delete(0, "end")
        self.cb_jk.set(db.JENIS_KELAMIN_LIST[0]); self.cb_agama.set(db.AGAMA_LIST[0])
        if not keep_sel:
            self.tree.selection_remove(self.tree.selection())

    def _data(self):
        d = {"kode_anggota": self.e_kode.get().strip().upper(), "nama_anggota": self.e_nama.get().strip().upper(),
             "tanggal_lahir": self.e_tgl.get().strip(), "jenis_kelamin": self.cb_jk.get(),
             "agama": self.cb_agama.get(), "alamat": self.e_alamat.get().strip(),
             "pekerjaan": self.e_kerja.get().strip(), "kode_ikatan": self.ikatan_map.get(self.cb_ikatan.get())}
        err = None
        if not d["kode_anggota"]: err = "Kode anggota tidak boleh kosong."
        elif not d["nama_anggota"]: err = "Nama anggota tidak boleh kosong."
        elif not validasi_tanggal(d["tanggal_lahir"]): err = "Tanggal lahir harus valid dengan format DD-MM-YYYY."
        elif d["agama"] not in db.AGAMA_LIST: err = "Agama tidak valid."
        elif not d["alamat"]: err = "Alamat tidak boleh kosong."
        elif not d["pekerjaan"]: err = "Pekerjaan tidak boleh kosong."
        elif not d["kode_ikatan"]: err = "Pilih ikatan. Tambahkan data ikatan terlebih dahulu bila belum ada."
        if err:
            messagebox.showwarning("Validasi", err)
            return None
        return d

    def tambah(self):
        if self.e_kode.cget("state") == "disabled":
            return messagebox.showinfo("Info", "Klik 'Bersihkan' terlebih dahulu untuk menambah data baru.")
        d = self._data()
        if not d:
            return
        try:
            db.anggota_tambah(d)
            messagebox.showinfo("Berhasil", "Data anggota berhasil ditambahkan.")
            self.bersih(); self.muat()
        except db.DatabaseError as e:
            messagebox.showerror("Gagal", str(e))

    def ubah(self):
        if self.e_kode.cget("state") != "disabled":
            return messagebox.showwarning("Info", "Pilih data anggota pada tabel terlebih dahulu.")
        d = self._data()
        if not d:
            return
        try:
            db.anggota_ubah(d)
            messagebox.showinfo("Berhasil", "Data anggota berhasil diubah.")
            self.bersih(); self.muat()
        except db.DatabaseError as e:
            messagebox.showerror("Gagal", str(e))

    def hapus(self):
        if self.e_kode.cget("state") != "disabled":
            return messagebox.showwarning("Info", "Pilih data anggota pada tabel terlebih dahulu.")
        kode = self.e_kode.get()
        if not messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus anggota {kode} - {self.e_nama.get()}?"):
            return
        try:
            db.anggota_hapus(kode)
            messagebox.showinfo("Berhasil", "Data anggota berhasil dihapus.")
            self.bersih(); self.muat()
        except db.DatabaseError as e:
            messagebox.showerror("Gagal", str(e))
