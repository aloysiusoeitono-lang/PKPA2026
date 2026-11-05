"""laporan.py - Pembuatan laporan anggota per ikatan, cetak, export Excel & PDF."""
import os
import sys
import subprocess
import tempfile
from datetime import datetime
from tkinter import messagebox, filedialog
import customtkinter as ctk
import database as db
from widgets import judul, tombol, buat_tabel, isi_tabel, ACCENT, CARD, FONT, TEXT, MUTED

NAMA_PERKUMPULAN = "PERKUMPULAN KELUARGA PULAU AMBON - PAPUA BARAT DAYA"
SEMUA = "SEMUA IKATAN"
HEADER = ["No.", "Kode Anggota", "Nama Anggota", "Tanggal Lahir", "Agama", "Alamat", "Pekerjaan"]


def ambil_laporan(kode_ikatan=None):
    """Data laporan (JOIN anggota-ikatan), urut nama. Mengembalikan list baris + nama ikatan."""
    rows = db.anggota_list(kode_ikatan=kode_ikatan)
    return [(i + 1, r["kode_anggota"], r["nama_anggota"], r["tanggal_lahir"], r["agama"],
             r["alamat"], r["pekerjaan"], r["nama_ikatan"]) for i, r in enumerate(rows)]


def tanggal_hari_ini():
    return datetime.now().strftime("%d-%m-%Y")


def export_excel(path, nama_ikatan, rows, semua):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    wb = Workbook(); ws = wb.active; ws.title = "Laporan Anggota"
    header = HEADER + (["Ikatan"] if semua else [])
    n = len(header)
    ws.append([NAMA_PERKUMPULAN]); ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n)
    ws.append(["LAPORAN DATA ANGGOTA"]); ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=n)
    ws["A1"].font = Font(bold=True, size=14); ws["A2"].font = Font(bold=True, size=12)
    ws["A1"].alignment = ws["A2"].alignment = Alignment(horizontal="center")
    ws.append([f"Ikatan: {nama_ikatan}"])
    ws.append([f"Tanggal Laporan: {tanggal_hari_ini()}"])
    ws.append([]); ws.append(header)
    thin = Side(style="thin", color="999999")
    for c in ws[6]:
        c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="0E4D64")
        c.alignment = Alignment(horizontal="center"); c.border = Border(thin, thin, thin, thin)
    for r in rows:
        ws.append(list(r[:7]) + ([r[7]] if semua else []))
        for c in ws[ws.max_row]:
            c.border = Border(thin, thin, thin, thin)
    ws.append([])
    ws.append([("Total seluruh anggota: " if semua else "Jumlah anggota: ") + str(len(rows))])
    ws.cell(ws.max_row, 1).font = Font(bold=True)
    for col, w in zip("ABCDEFGH", [6, 15, 30, 14, 12, 40, 20, 25]):
        ws.column_dimensions[col].width = w
    wb.save(path)


def export_pdf(path, nama_ikatan, rows, semua):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
    doc = SimpleDocTemplate(path, pagesize=landscape(A4), leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                            topMargin=1.5 * cm, bottomMargin=1.5 * cm, title="Laporan Data Anggota")
    ss = getSampleStyleSheet()
    cell = ParagraphStyle("cell", parent=ss["Normal"], fontSize=8, leading=10)
    el = [Paragraph(f"<b>{NAMA_PERKUMPULAN}</b>", ParagraphStyle("t", parent=ss["Title"], fontSize=15)),
          Paragraph("<b>LAPORAN DATA ANGGOTA</b>", ParagraphStyle("s", parent=ss["Normal"], alignment=1, fontSize=11)),
          Spacer(1, 10),
          Paragraph(f"Ikatan: <b>{nama_ikatan}</b>", ss["Normal"]),
          Paragraph(f"Tanggal Laporan: {tanggal_hari_ini()}", ss["Normal"]), Spacer(1, 8)]
    header = HEADER + (["Ikatan"] if semua else [])
    data = [header]
    for r in rows:
        vals = list(r[:7]) + ([r[7]] if semua else [])
        data.append([Paragraph(str(v or ""), cell) for v in vals])
    widths = [1 * cm, 2.5 * cm, 5 * cm, 2.4 * cm, 2.2 * cm, 8 * cm, 3.5 * cm] if not semua else \
        [1 * cm, 2.3 * cm, 4.5 * cm, 2.3 * cm, 2 * cm, 6.5 * cm, 3 * cm, 3.6 * cm]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0E4D64")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F5F7")]),
    ]))
    el += [t, Spacer(1, 10),
           Paragraph(f"<b>{'Total seluruh anggota' if semua else 'Jumlah anggota'}: {len(rows)}</b>", ss["Normal"])]
    doc.build(el)


def buka_file(path, cetak=False):
    if sys.platform.startswith("win"):
        os.startfile(path, "print" if cetak else "open")
    elif sys.platform == "darwin":
        subprocess.Popen(["lp", path] if cetak else ["open", path])
    else:
        subprocess.Popen(["lp", path] if cetak else ["xdg-open", path])


class LaporanPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.rows, self.nama_ikatan = [], SEMUA
        judul(self, "Laporan Anggota", "Tampilkan, cetak, dan ekspor data anggota per ikatan").pack(anchor="w", pady=(0, 12))
        bar = ctk.CTkFrame(self, fg_color=CARD, corner_radius=12)
        bar.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(bar, text="Pilih Ikatan", font=(FONT, 12)).pack(side="left", padx=12, pady=12)
        self.cb = ctk.CTkOptionMenu(bar, values=[SEMUA], width=240)
        self.cb.pack(side="left", padx=6)
        tombol(bar, "TAMPILKAN LAPORAN", self.tampilkan, width=170).pack(side="left", padx=6)
        tombol(bar, "CETAK LAPORAN", self.cetak, ACCENT, "#A87A2E", width=140).pack(side="left", padx=6)
        tombol(bar, "EXPORT EXCEL", self.excel, "#1D7A46", "#155C34", width=130).pack(side="left", padx=6)
        tombol(bar, "EXPORT PDF", self.pdf, "#B23A48", "#8E2E3A", width=120).pack(side="left", padx=6)

        info = ctk.CTkFrame(self, fg_color=CARD, corner_radius=12)
        info.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(info, text=NAMA_PERKUMPULAN, font=(FONT, 15, "bold"), text_color=TEXT).pack(pady=(10, 0))
        self.lbl_info = ctk.CTkLabel(info, text="", font=(FONT, 12), text_color=MUTED)
        self.lbl_info.pack(pady=(2, 10))

        kol = [("no", "No.", 50), ("kode", "Kode Anggota", 110), ("nama", "Nama Anggota", 220),
               ("tgl", "Tanggal Lahir", 100), ("agama", "Agama", 90), ("alamat", "Alamat", 260),
               ("kerja", "Pekerjaan", 140)]
        f, self.tree = buat_tabel(self, kol)
        f.pack(fill="both", expand=True)
        self.refresh()

    def refresh(self):
        try:
            self.map = {r["nama_ikatan"]: r["kode_ikatan"] for r in db.ikatan_list()}
        except db.DatabaseError as e:
            return messagebox.showerror("Kesalahan", str(e))
        vals = [SEMUA] + list(self.map)
        self.cb.configure(values=vals)
        if self.cb.get() not in vals:
            self.cb.set(SEMUA)
        self.tampilkan()

    def tampilkan(self):
        nama = self.cb.get()
        try:
            self.rows = ambil_laporan(self.map.get(nama) if nama != SEMUA else None)
        except db.DatabaseError as e:
            return messagebox.showerror("Kesalahan", str(e))
        self.nama_ikatan = nama
        isi_tabel(self.tree, [r[:7] for r in self.rows])
        label = "Total seluruh anggota" if nama == SEMUA else "Jumlah anggota"
        self.lbl_info.configure(text=f"Ikatan: {nama}   |   Tanggal Laporan: {tanggal_hari_ini()}   |   "
                                     f"{label}: {len(self.rows)}")

    def _siap(self):
        if self.nama_ikatan != self.cb.get():
            self.tampilkan()
        if not self.rows:
            messagebox.showwarning("Info", "Tidak ada data untuk ikatan yang dipilih.")
            return False
        return True

    def _nama_file(self, ext):
        return f"Laporan_Anggota_{self.nama_ikatan.replace(' ', '_')}_{datetime.now():%d-%m-%Y}.{ext}"

    def excel(self):
        if not self._siap():
            return
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", initialfile=self._nama_file("xlsx"),
                                            filetypes=[("Excel", "*.xlsx")])
        if path:
            try:
                export_excel(path, self.nama_ikatan, self.rows, self.nama_ikatan == SEMUA)
                messagebox.showinfo("Berhasil", f"Laporan berhasil disimpan:\n{path}")
            except Exception as e:
                messagebox.showerror("Gagal", f"Gagal export Excel: {e}")

    def pdf(self):
        if not self._siap():
            return
        path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=self._nama_file("pdf"),
                                            filetypes=[("PDF", "*.pdf")])
        if path:
            try:
                export_pdf(path, self.nama_ikatan, self.rows, self.nama_ikatan == SEMUA)
                messagebox.showinfo("Berhasil", f"Laporan berhasil disimpan:\n{path}")
            except Exception as e:
                messagebox.showerror("Gagal", f"Gagal export PDF: {e}")

    def cetak(self):
        if not self._siap():
            return
        try:
            path = os.path.join(tempfile.gettempdir(), self._nama_file("pdf"))
            export_pdf(path, self.nama_ikatan, self.rows, self.nama_ikatan == SEMUA)
            try:
                buka_file(path, cetak=True)
                messagebox.showinfo("Cetak", "Laporan dikirim ke printer default.")
            except Exception:
                buka_file(path)
                messagebox.showinfo("Cetak", "Laporan dibuka. Silakan cetak dari aplikasi PDF (Ctrl+P).")
        except Exception as e:
            messagebox.showerror("Gagal", f"Gagal mencetak laporan: {e}")
