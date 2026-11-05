"""database.py - Koneksi SQLite dan seluruh operasi CRUD (tanpa kode GUI)."""
import os
import sqlite3
import hashlib
import secrets
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "perkumpulan_ambon.db")

AGAMA_LIST = ["ISLAM", "PROTESTAN", "KATOLIK", "HINDU", "BUDDHA"]
JENIS_KELAMIN_LIST = ["LAKI-LAKI", "PEREMPUAN"]


class DatabaseError(Exception):
    """Kesalahan database dengan pesan berbahasa Indonesia."""


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def transaksi():
    """Context manager transaksi: commit jika sukses, rollback jika gagal."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        msg = str(e)
        if "UNIQUE" in msg or "PRIMARY KEY" in msg:
            raise DatabaseError("Kode sudah digunakan. Gunakan kode lain.") from e
        if "FOREIGN KEY" in msg:
            raise DatabaseError("Data masih terhubung dengan data lain (relasi foreign key).") from e
        raise DatabaseError(f"Pelanggaran integritas data: {msg}") from e
    except sqlite3.Error as e:
        conn.rollback()
        raise DatabaseError(f"Terjadi kesalahan database: {e}") from e
    finally:
        conn.close()


def _query(sql, params=()):
    try:
        conn = get_connection()
        try:
            return [dict(r) for r in conn.execute(sql, params).fetchall()]
        finally:
            conn.close()
    except sqlite3.Error as e:
        raise DatabaseError(f"Gagal membaca data: {e}") from e


# ---------------- Hash password ----------------
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()
    return f"pbkdf2${salt}${h}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, salt, h = stored.split("$")
    except ValueError:
        return False
    calc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()
    return secrets.compare_digest(calc, h)


# ---------------- Inisialisasi ----------------
def init_db():
    with transaksi() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS user (
            kode_user TEXT PRIMARY KEY,
            nama_user TEXT NOT NULL,
            password  TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS ikatan (
            kode_ikatan TEXT PRIMARY KEY,
            nama_ikatan TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS anggota (
            kode_anggota  TEXT PRIMARY KEY,
            nama_anggota  TEXT NOT NULL,
            tanggal_lahir TEXT NOT NULL,
            jenis_kelamin TEXT NOT NULL,
            agama         TEXT NOT NULL CHECK (agama IN ('ISLAM','PROTESTAN','KATOLIK','HINDU','BUDDHA')),
            alamat        TEXT,
            pekerjaan     TEXT,
            kode_ikatan   TEXT NOT NULL,
            FOREIGN KEY (kode_ikatan) REFERENCES ikatan(kode_ikatan)
                ON UPDATE CASCADE ON DELETE RESTRICT)""")
        if c.execute("SELECT COUNT(*) FROM user").fetchone()[0] == 0:
            c.execute("INSERT INTO user VALUES (?,?,?)",
                      ("admin", "ADMINISTRATOR", hash_password("admin123")))


# ---------------- USER ----------------
def user_get(kode):
    r = _query("SELECT * FROM user WHERE kode_user=?", (kode,))
    return r[0] if r else None


def user_list(cari=""):
    k = f"%{cari}%"
    return _query("SELECT kode_user, nama_user FROM user WHERE kode_user LIKE ? OR nama_user LIKE ? "
                  "ORDER BY kode_user", (k, k))


def user_tambah(kode, nama, password):
    with transaksi() as c:
        c.execute("INSERT INTO user VALUES (?,?,?)", (kode, nama, hash_password(password)))


def user_ubah(kode, nama, password=None):
    with transaksi() as c:
        if password:
            c.execute("UPDATE user SET nama_user=?, password=? WHERE kode_user=?",
                      (nama, hash_password(password), kode))
        else:
            c.execute("UPDATE user SET nama_user=? WHERE kode_user=?", (nama, kode))


def user_ubah_password(kode, password):
    with transaksi() as c:
        c.execute("UPDATE user SET password=? WHERE kode_user=?", (hash_password(password), kode))


def user_hapus(kode):
    with transaksi() as c:
        if c.execute("SELECT COUNT(*) FROM user").fetchone()[0] <= 1:
            raise DatabaseError("User terakhir tidak boleh dihapus.")
        c.execute("DELETE FROM user WHERE kode_user=?", (kode,))


# ---------------- IKATAN ----------------
def ikatan_list(cari=""):
    k = f"%{cari}%"
    return _query("""SELECT i.kode_ikatan, i.nama_ikatan, COUNT(a.kode_anggota) AS jumlah
                     FROM ikatan i LEFT JOIN anggota a ON a.kode_ikatan = i.kode_ikatan
                     WHERE i.kode_ikatan LIKE ? OR i.nama_ikatan LIKE ?
                     GROUP BY i.kode_ikatan ORDER BY i.nama_ikatan""", (k, k))


def ikatan_tambah(kode, nama):
    with transaksi() as c:
        c.execute("INSERT INTO ikatan VALUES (?,?)", (kode, nama))


def ikatan_ubah(kode, nama):
    with transaksi() as c:
        c.execute("UPDATE ikatan SET nama_ikatan=? WHERE kode_ikatan=?", (nama, kode))


def ikatan_hapus(kode):
    with transaksi() as c:
        n = c.execute("SELECT COUNT(*) FROM anggota WHERE kode_ikatan=?", (kode,)).fetchone()[0]
        if n > 0:
            raise DatabaseError(f"Ikatan masih memiliki {n} anggota. Pindahkan atau hapus anggota "
                                "terkait terlebih dahulu.")
        c.execute("DELETE FROM ikatan WHERE kode_ikatan=?", (kode,))


# ---------------- ANGGOTA ----------------
def anggota_list(cari="", kode_ikatan=None):
    k = f"%{cari}%"
    sql = """SELECT a.*, i.nama_ikatan FROM anggota a
             JOIN ikatan i ON i.kode_ikatan = a.kode_ikatan
             WHERE (a.kode_anggota LIKE ? OR a.nama_anggota LIKE ?)"""
    params = [k, k]
    if kode_ikatan:
        sql += " AND a.kode_ikatan = ?"
        params.append(kode_ikatan)
    sql += " ORDER BY a.nama_anggota"
    return _query(sql, params)


def _anggota_params(d):
    return (d["nama_anggota"].strip().upper(), d["tanggal_lahir"], d["jenis_kelamin"], d["agama"],
            d["alamat"], d["pekerjaan"], d["kode_ikatan"])


def anggota_tambah(d):
    with transaksi() as c:
        c.execute("INSERT INTO anggota (nama_anggota, tanggal_lahir, jenis_kelamin, agama, alamat, "
                  "pekerjaan, kode_ikatan, kode_anggota) VALUES (?,?,?,?,?,?,?,?)",
                  _anggota_params(d) + (d["kode_anggota"],))


def anggota_ubah(d):
    with transaksi() as c:
        c.execute("UPDATE anggota SET nama_anggota=?, tanggal_lahir=?, jenis_kelamin=?, agama=?, "
                  "alamat=?, pekerjaan=?, kode_ikatan=? WHERE kode_anggota=?",
                  _anggota_params(d) + (d["kode_anggota"],))


def anggota_hapus(kode):
    with transaksi() as c:
        c.execute("DELETE FROM anggota WHERE kode_anggota=?", (kode,))


def statistik():
    r = _query("SELECT (SELECT COUNT(*) FROM anggota) AS anggota, (SELECT COUNT(*) FROM ikatan) AS ikatan, "
               "(SELECT COUNT(*) FROM user) AS user")
    return r[0]
