"""main.py - Titik awal aplikasi: jendela utama, sidebar, header, dashboard."""
from tkinter import messagebox
import customtkinter as ctk
import database as db
from auth import LoginFrame
from anggota import AnggotaPage
from ikatan import IkatanPage
from user import UserPage
from laporan import LaporanPage
from widgets import PRIMARY, PRIMARY_HOVER, ACCENT, BG, CARD, TEXT, MUTED, FONT

APP_NAME = "SISTEM INFORMASI DATA ANGGOTA"


class Dashboard(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.lbl_sapa = ctk.CTkLabel(self, text="", font=(FONT, 22, "bold"), text_color=TEXT)
        self.lbl_sapa.pack(anchor="w")
        ctk.CTkLabel(self, text="Ringkasan Data Perkumpulan Keluarga Pulau Ambon (PKPA) - Papua Barat Daya",
                     font=(FONT, 13), text_color=MUTED).pack(anchor="w", pady=(0, 20))
        row = ctk.CTkFrame(self, fg_color="transparent"); row.pack(fill="x")
        self.kartu = {}
        for key, teks, warna in [("anggota", "Total Anggota", PRIMARY), ("ikatan", "Jumlah Ikatan", ACCENT),
                                 ("user", "Jumlah User", "#1D7A46")]:
            c = ctk.CTkFrame(row, fg_color=warna, corner_radius=14, height=140)
            c.pack(side="left", expand=True, fill="x", padx=(0, 16))
            ctk.CTkLabel(c, text=teks, font=(FONT, 14), text_color="white").pack(anchor="w", padx=20, pady=(18, 0))
            lb = ctk.CTkLabel(c, text="0", font=(FONT, 42, "bold"), text_color="white")
            lb.pack(anchor="w", padx=20, pady=(0, 18))
            self.kartu[key] = lb
        self.refresh()

    def refresh(self):
        self.lbl_sapa.configure(text=f"Selamat datang, {self.app.user['nama_user']}")
        try:
            s = db.statistik()
            for k, lb in self.kartu.items():
                lb.configure(text=str(s[k]))
        except db.DatabaseError as e:
            messagebox.showerror("Kesalahan", str(e))


class MainFrame(ctk.CTkFrame):
    MENU = [("Dashboard", "dashboard"), ("Data Anggota", "anggota"), ("Data Ikatan", "ikatan"),
            ("Data User", "user"), ("Laporan Anggota", "laporan")]

    def __init__(self, master, app):
        super().__init__(master, fg_color=BG)
        self.app = app
        side = ctk.CTkFrame(self, fg_color=PRIMARY, corner_radius=0, width=230)
        side.pack(side="left", fill="y"); side.pack_propagate(False)
        ctk.CTkLabel(side, text="PKPA", font=(FONT, 20, "bold"), text_color="white").pack(pady=(28, 0))
        ctk.CTkLabel(side, text="Papua Barat Daya", font=(FONT, 12), text_color="#CFE3EA").pack(pady=(0, 24))
        self.btns = {}
        for i, (teks, key) in enumerate(self.MENU, 1):
            b = ctk.CTkButton(side, text=f"  {i}.  {teks}", anchor="w", height=42, corner_radius=8,
                              fg_color="transparent", hover_color=PRIMARY_HOVER, font=(FONT, 13),
                              command=lambda k=key: self.tampil(k))
            b.pack(fill="x", padx=14, pady=3)
            self.btns[key] = b
        ctk.CTkButton(side, text="  6.  Logout", anchor="w", height=42, corner_radius=8, fg_color="transparent",
                      hover_color="#8E2E3A", font=(FONT, 13), command=app.logout).pack(fill="x", padx=14, pady=3)

        right = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        right.pack(side="left", fill="both", expand=True)
        header = ctk.CTkFrame(right, fg_color=CARD, corner_radius=0, height=64)
        header.pack(fill="x"); header.pack_propagate(False)
        ctk.CTkLabel(header, text=f"{APP_NAME}  •  PERKUMPULAN KELUARGA PULAU AMBON (PKPA)",
                     font=(FONT, 15, "bold"), text_color=PRIMARY).pack(side="left", padx=24)
        ctk.CTkButton(header, text="Logout", width=90, fg_color="#B23A48", hover_color="#8E2E3A",
                      command=app.logout).pack(side="right", padx=(8, 24))
        self.lbl_user = ctk.CTkLabel(header, text="", font=(FONT, 13), text_color=TEXT)
        self.lbl_user.pack(side="right")

        self.content = ctk.CTkFrame(right, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=24, pady=20)
        self.pages = {}
        self.perbarui_header()
        self.tampil("dashboard")

    def perbarui_header(self):
        u = self.app.user
        self.lbl_user.configure(text=f"👤 {u['nama_user']} ({u['kode_user']})")

    def tampil(self, key):
        for k, b in self.btns.items():
            b.configure(fg_color=ACCENT if k == key else "transparent")
        for p in self.pages.values():
            p.pack_forget()
        if key not in self.pages:
            cls = {"dashboard": lambda: Dashboard(self.content, self.app), "anggota": lambda: AnggotaPage(self.content),
                   "ikatan": lambda: IkatanPage(self.content), "user": lambda: UserPage(self.content, self),
                   "laporan": lambda: LaporanPage(self.content)}[key]
            self.pages[key] = cls()
        else:
            self.pages[key].refresh()
        self.pages[key].pack(fill="both", expand=True)

    @property
    def user(self):
        return self.app.user


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")
        self.title("PERKUMPULAN KELUARGA PULAU AMBON (PKPA) - Sistem Informasi Data Anggota")
        self.geometry("1280x760"); self.minsize(1100, 680)
        self.user = None
        self.frame = None
        self.tampil_login()

    def _ganti(self, frame):
        if self.frame:
            self.frame.destroy()
        self.frame = frame
        frame.pack(fill="both", expand=True)

    def tampil_login(self):
        self._ganti(LoginFrame(self, self.login_berhasil))

    def login_berhasil(self, user):
        self.user = user
        self._ganti(MainFrame(self, self))

    def logout(self):
        if messagebox.askyesno("Logout", "Yakin ingin keluar dari aplikasi?"):
            self.user = None
            self.tampil_login()


def main():
    try:
        db.init_db()
    except db.DatabaseError as e:
        messagebox.showerror("Kesalahan Database", f"Database gagal dibuat:\n{e}")
        return
    App().mainloop()


if __name__ == "__main__":
    main()
