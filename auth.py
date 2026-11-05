"""auth.py - Autentikasi pengguna dan halaman login."""
from tkinter import messagebox
import customtkinter as ctk
import database as db
from widgets import PRIMARY, PRIMARY_HOVER, ACCENT, DANGER, TEXT, MUTED, FONT


def login(kode_user: str, password: str):
    """Mengembalikan dict user bila valid, None bila gagal."""
    if not kode_user or not password:
        return None
    u = db.user_get(kode_user.strip())
    if u and db.verify_password(password, u["password"]):
        return {"kode_user": u["kode_user"], "nama_user": u["nama_user"]}
    return None


class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, on_success):
        super().__init__(master, fg_color=PRIMARY)
        self.on_success = on_success
        card = ctk.CTkFrame(self, fg_color="white", corner_radius=16, width=460)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card, text="PERKUMPULAN KELUARGA PULAU AMBON\n(P K P A)\nPAPUA BARAT DAYA",
                     font=(FONT, 18, "bold"), text_color=PRIMARY, justify="center").pack(padx=40, pady=(36, 4))
        ctk.CTkFrame(card, height=3, width=80, fg_color=ACCENT).pack(pady=6)
        ctk.CTkLabel(card, text="SISTEM INFORMASI DATA ANGGOTA", font=(FONT, 13),
                     text_color=MUTED).pack(pady=(0, 24))

        ctk.CTkLabel(card, text="Kode User", font=(FONT, 12, "bold"), text_color=TEXT).pack(anchor="w", padx=40)
        self.e_kode = ctk.CTkEntry(card, width=360, height=38, placeholder_text="Masukkan kode user")
        self.e_kode.pack(padx=40, pady=(4, 12))
        ctk.CTkLabel(card, text="Password", font=(FONT, 12, "bold"), text_color=TEXT).pack(anchor="w", padx=40)
        self.e_pass = ctk.CTkEntry(card, width=360, height=38, show="•", placeholder_text="Masukkan password")
        self.e_pass.pack(padx=40, pady=(4, 6))
        self.show_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(card, text="Tampilkan password", variable=self.show_var,
                        command=self._toggle, font=(FONT, 12)).pack(anchor="w", padx=40, pady=4)

        self.lbl_err = ctk.CTkLabel(card, text="", text_color=DANGER, font=(FONT, 12))
        self.lbl_err.pack(pady=(6, 0))
        ctk.CTkButton(card, text="LOGIN", width=360, height=42, fg_color=PRIMARY, hover_color=PRIMARY_HOVER,
                      font=(FONT, 14, "bold"), command=self._login).pack(padx=40, pady=(6, 36))
        self.e_kode.bind("<Return>", lambda e: self.e_pass.focus())
        self.e_pass.bind("<Return>", lambda e: self._login())
        self.after(100, self.e_kode.focus)

    def _toggle(self):
        self.e_pass.configure(show="" if self.show_var.get() else "•")

    def _login(self):
        try:
            u = login(self.e_kode.get(), self.e_pass.get())
        except db.DatabaseError as e:
            messagebox.showerror("Kesalahan Database", str(e))
            return
        if u:
            self.lbl_err.configure(text="")
            self.on_success(u)
        else:
            self.lbl_err.configure(text="Kode user atau password salah!")
            self.e_pass.delete(0, "end")
