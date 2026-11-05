"""user.py - Halaman CRUD Data User."""
from tkinter import messagebox
import customtkinter as ctk
import database as db
from widgets import judul, tombol, buat_tabel, isi_tabel, DANGER, ACCENT, CARD, FONT, MUTED


class UserPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        judul(self, "Data User", "Kelola pengguna yang dapat mengakses aplikasi").pack(anchor="w", pady=(0, 12))

        form = ctk.CTkFrame(self, fg_color=CARD, corner_radius=12)
        form.pack(fill="x", pady=(0, 12))
        labels = ["Kode User", "Nama User", "Password", "Ulangi Password"]
        self.e = {}
        for i, lb in enumerate(labels):
            r, c = divmod(i, 2)
            ctk.CTkLabel(form, text=lb, font=(FONT, 12)).grid(row=r, column=c * 2, padx=12, pady=8, sticky="w")
            ent = ctk.CTkEntry(form, width=240, show="•" if "Password" in lb else "")
            ent.grid(row=r, column=c * 2 + 1, padx=6, pady=8)
            self.e[lb] = ent
        ctk.CTkLabel(form, text="* Saat mengubah user, kosongkan password jika tidak ingin menggantinya.",
                     font=(FONT, 11), text_color=MUTED).grid(row=2, column=0, columnspan=4, sticky="w", padx=12)
        bar = ctk.CTkFrame(form, fg_color="transparent")
        bar.grid(row=3, column=0, columnspan=4, sticky="w", padx=12, pady=12)
        tombol(bar, "Tambah", self.tambah).pack(side="left", padx=(0, 6))
        tombol(bar, "Ubah", self.ubah, ACCENT, "#A87A2E").pack(side="left", padx=6)
        tombol(bar, "Ubah Password", self.ganti_password, ACCENT, "#A87A2E", width=140).pack(side="left", padx=6)
        tombol(bar, "Hapus", self.hapus, DANGER, "#8E2E3A").pack(side="left", padx=6)
        tombol(bar, "Bersihkan", self.bersih, "#6B7280", "#4B5563").pack(side="left", padx=6)

        cari = ctk.CTkFrame(self, fg_color="transparent")
        cari.pack(fill="x", pady=(0, 8))
        self.e_cari = ctk.CTkEntry(cari, width=300, placeholder_text="Cari kode atau nama user...")
        self.e_cari.pack(side="left")
        self.e_cari.bind("<KeyRelease>", lambda e: self.muat())
        tombol(cari, "Cari", self.muat).pack(side="left", padx=6)

        f, self.tree = buat_tabel(self, [("kode", "Kode User", 180), ("nama", "Nama User", 360),
                                         ("pw", "Password", 160)])
        f.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.pilih)
        self.muat()

    def refresh(self):
        self.muat()

    def muat(self):
        try:
            rows = db.user_list(self.e_cari.get().strip())
        except db.DatabaseError as e:
            return messagebox.showerror("Kesalahan", str(e))
        isi_tabel(self.tree, [(r["kode_user"], r["nama_user"], "••••••••") for r in rows])

    def _kode(self):
        return self.e["Kode User"]

    def pilih(self, _=None):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0], "values")
        self.bersih(keep_sel=True)
        self._kode().insert(0, v[0])
        self._kode().configure(state="disabled")
        self.e["Nama User"].insert(0, v[1])

    def bersih(self, keep_sel=False):
        self._kode().configure(state="normal")
        for ent in self.e.values():
            ent.delete(0, "end")
        if not keep_sel:
            self.tree.selection_remove(self.tree.selection())

    def _password(self, wajib):
        p1, p2 = self.e["Password"].get(), self.e["Ulangi Password"].get()
        if not p1 and not wajib:
            return ""
        if len(p1) < 6:
            messagebox.showwarning("Validasi", "Password minimal 6 karakter.")
            return None
        if p1 != p2:
            messagebox.showwarning("Validasi", "Konfirmasi password tidak sama.")
            return None
        return p1

    def tambah(self):
        if self._kode().cget("state") == "disabled":
            return messagebox.showinfo("Info", "Klik 'Bersihkan' terlebih dahulu untuk menambah data baru.")
        kode, nama = self._kode().get().strip(), self.e["Nama User"].get().strip().upper()
        if not kode or not nama:
            return messagebox.showwarning("Validasi", "Kode user dan nama user wajib diisi.")
        if " " in kode:
            return messagebox.showwarning("Validasi", "Kode user tidak boleh mengandung spasi.")
        if db.user_get(kode):
            return messagebox.showwarning("Validasi", "Kode user sudah digunakan.")
        pw = self._password(True)
        if pw is None:
            return
        try:
            db.user_tambah(kode, nama, pw)
            messagebox.showinfo("Berhasil", "User berhasil ditambahkan.")
            self.bersih(); self.muat()
        except db.DatabaseError as e:
            messagebox.showerror("Gagal", str(e))

    def ubah(self):
        if self._kode().cget("state") != "disabled":
            return messagebox.showwarning("Info", "Pilih user pada tabel terlebih dahulu.")
        nama = self.e["Nama User"].get().strip().upper()
        if not nama:
            return messagebox.showwarning("Validasi", "Nama user wajib diisi.")
        pw = self._password(False)
        if pw is None:
            return
        try:
            kode = self._kode().get()
            db.user_ubah(kode, nama, pw or None)
            if kode == self.app.user["kode_user"]:
                self.app.user["nama_user"] = nama
                self.app.perbarui_header()
            messagebox.showinfo("Berhasil", "Data user berhasil diubah.")
            self.bersih(); self.muat()
        except db.DatabaseError as e:
            messagebox.showerror("Gagal", str(e))

    def ganti_password(self):
        if self._kode().cget("state") != "disabled":
            return messagebox.showwarning("Info", "Pilih user pada tabel terlebih dahulu.")
        pw = self._password(True)
        if pw is None:
            return
        try:
            db.user_ubah_password(self._kode().get(), pw)
            messagebox.showinfo("Berhasil", "Password berhasil diubah.")
            self.bersih()
        except db.DatabaseError as e:
            messagebox.showerror("Gagal", str(e))

    def hapus(self):
        if self._kode().cget("state") != "disabled":
            return messagebox.showwarning("Info", "Pilih user pada tabel terlebih dahulu.")
        kode = self._kode().get()
        if kode == self.app.user["kode_user"]:
            return messagebox.showwarning("Ditolak", "Anda tidak dapat menghapus akun yang sedang login.")
        if not messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus user {kode}?"):
            return
        try:
            db.user_hapus(kode)
            messagebox.showinfo("Berhasil", "User berhasil dihapus.")
            self.bersih(); self.muat()
        except db.DatabaseError as e:
            messagebox.showerror("Gagal", str(e))
