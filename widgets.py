"""widgets.py - Komponen tampilan bersama (warna, tabel, judul halaman)."""
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

PRIMARY = "#0E4D64"
PRIMARY_HOVER = "#0A3A4C"
ACCENT = "#C8963E"
DANGER = "#B23A48"
BG = "#F3F5F7"
CARD = "#FFFFFF"
TEXT = "#1F2933"
MUTED = "#6B7280"
FONT = "Segoe UI"


def judul(parent, teks, sub=None):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    ctk.CTkLabel(f, text=teks, font=(FONT, 22, "bold"), text_color=TEXT).pack(anchor="w")
    if sub:
        ctk.CTkLabel(f, text=sub, font=(FONT, 13), text_color=MUTED).pack(anchor="w")
    return f


def tombol(parent, teks, cmd, warna=PRIMARY, hover=PRIMARY_HOVER, width=110):
    return ctk.CTkButton(parent, text=teks, command=cmd, fg_color=warna, hover_color=hover,
                         width=width, height=34, font=(FONT, 13, "bold"), corner_radius=8)


def buat_tabel(parent, kolom):
    """kolom: list of (id, judul, lebar). Mengembalikan (frame, treeview)."""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Ambon.Treeview", font=(FONT, 11), rowheight=28, background=CARD,
                    fieldbackground=CARD, foreground=TEXT, borderwidth=0)
    style.configure("Ambon.Treeview.Heading", font=(FONT, 11, "bold"), background=PRIMARY,
                    foreground="white", relief="flat", padding=6)
    style.map("Ambon.Treeview", background=[("selected", ACCENT)])
    style.map("Ambon.Treeview.Heading", background=[("active", PRIMARY_HOVER)])

    frame = tk.Frame(parent, bg=CARD)
    tree = ttk.Treeview(frame, columns=[k[0] for k in kolom], show="headings",
                        style="Ambon.Treeview", selectmode="browse")
    for cid, head, w in kolom:
        tree.heading(cid, text=head)
        tree.column(cid, width=w, minwidth=50, anchor="w")
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    tree.tag_configure("ganjil", background="#F7F9FA")
    return frame, tree


def isi_tabel(tree, rows):
    tree.delete(*tree.get_children())
    for i, r in enumerate(rows):
        tree.insert("", "end", values=r, tags=("ganjil",) if i % 2 else ())
