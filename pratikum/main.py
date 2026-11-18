import sqlite3
import tkinter as tk
from contextlib import contextmanager
from tkinter import ttk, messagebox

DB_NAME = "mahasiswa.db"
DAFTAR_PRODI = ["Informatika", "Sistem Informasi", "Manajemen", "Akuntansi"]

# ==========================================
# 2.4.3 Membuat Fungsi Koneksi
# ==========================================
@contextmanager
def koneksi():
    """Membuka koneksi, menyimpan perubahan, lalu selalu menutupnya."""
    conn = sqlite3.connect(DB_NAME)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# ==========================================
# 2.4.4 Membuat Tabel Mahasiswa
# ==========================================
def buat_tabel():
    with koneksi() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mahasiswa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                nim TEXT NOT NULL UNIQUE,
                prodi TEXT NOT NULL,
                alamat TEXT
            )
        """)

# Panggil fungsi buat tabel agar tabel tersedia sebelum antarmuka dibuat
buat_tabel()

# ==========================================
# 2.4.5 Membuat Jendela Utama dan Formulir
# ==========================================
root = tk.Tk()
root.title("Aplikasi Data Mahasiswa")
root.geometry("900x590")

form = ttk.LabelFrame(root, text="Formulir Mahasiswa", padding=12)
form.pack(fill="x", padx=15, pady=12)

# Baris 1: Nama dan NIM
ttk.Label(form, text="Nama").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_nama = ttk.Entry(form, width=30)
entry_nama.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(form, text="NIM").grid(row=0, column=2, padx=5, pady=5, sticky="w")
entry_nim = ttk.Entry(form, width=30)
entry_nim.grid(row=0, column=3, padx=5, pady=5)

# Baris 2: Program Studi dan Alamat
ttk.Label(form, text="Program Studi").grid(row=1, column=0, padx=5, pady=5, sticky="w")
combo_prodi = ttk.Combobox(form, values=DAFTAR_PRODI, state="readonly", width=27)
combo_prodi.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(form, text="Alamat").grid(row=1, column=2, padx=5, pady=5, sticky="w")
entry_alamat = ttk.Entry(form, width=30)
entry_alamat.grid(row=1, column=3, padx=5, pady=5)

# ==========================================
# 2.4.6 Membuat Tabel Tampilan dengan Treeview
# ==========================================
kolom = ("id", "nama", "nim", "prodi", "alamat")
tabel = ttk.Treeview(root, columns=kolom, show="headings")

for key, judul in [("id", "ID"), ("nama", "Nama"), ("nim", "NIM"), 
                   ("prodi", "Program Studi"), ("alamat", "Alamat")]:
    tabel.heading(key, text=judul)

tabel.column("id", width=50, anchor="center")
tabel.column("nama", width=170)
tabel.column("nim", width=120)
tabel.column("prodi", width=160)
tabel.column("alamat", width=250)
tabel.pack(fill="both", expand=True, padx=15, pady=8)

# ==========================================
# 2.4.7 Membuat Fungsi Menampilkan Data (SELECT)
# ==========================================
def tampilkan_data():
    # Hapus isi treeview agar tidak ganda
    for item in tabel.get_children():
        tabel.delete(item)
        
    with koneksi() as conn:
        rows = conn.execute(
            "SELECT id, nama, nim, prodi, alamat FROM mahasiswa ORDER BY id DESC"
        ).fetchall()
        
    for row in rows:
        tabel.insert("", tk.END, values=row)

# ==========================================
# 2.4.8 Membuat Fungsi Membersihkan Formulir
# ==========================================
def bersihkan_form():
    entry_nama.delete(0, tk.END)
    entry_nim.delete(0, tk.END)
    combo_prodi.set("")
    entry_alamat.delete(0, tk.END)
    entry_nama.focus_set()

# ==========================================
# 2.4.9 Membuat Fungsi Menyimpan Data (INSERT)
# ==========================================
def simpan_data():
    nama = entry_nama.get().strip()
    nim = entry_nim.get().strip()
    prodi = combo_prodi.get().strip()
    alamat = entry_alamat.get().strip()
    
    if not nama or not nim or not prodi:
        messagebox.showwarning("Validasi", "Nama, NIM, dan Program Studi wajib diisi.")
        return
        
    try:
        with koneksi() as conn:
            conn.execute(
                "INSERT INTO mahasiswa (nama, nim, prodi, alamat) VALUES (?, ?, ?, ?)",
                (nama, nim, prodi, alamat)
            )
        messagebox.showinfo("Berhasil", "Data berhasil disimpan.")
        tampilkan_data()
        bersihkan_form()
    except sqlite3.IntegrityError:
        messagebox.showerror("NIM Duplikat", "NIM sudah terdaftar.")
    except sqlite3.Error as error:
        messagebox.showerror("Kesalahan Database", str(error))

# ==========================================
# 2.4.10 Membuat Fungsi Menghapus Data (DELETE)
# ==========================================
def hapus_data():
    pilihan = tabel.selection()
    if not pilihan:
        messagebox.showwarning("Pilih Data", "Pilih baris yang akan dihapus.")
        return
        
    data = tabel.item(pilihan[0], "values")
    record_id = int(data[0])
    
    if not messagebox.askyesno("Konfirmasi", f"Hapus data {data[1]}?"):
        return
        
    with koneksi() as conn:
        conn.execute("DELETE FROM mahasiswa WHERE id = ?", (record_id,))
        
    tampilkan_data()
    bersihkan_form()

# ==========================================
# 2.4.15 Pengembangan: Fungsi Mengubah Data (UPDATE)
# ==========================================
def isi_form_dari_tabel(event=None):
    """Memuat record terpilih ke form."""
    pilihan = tabel.selection()
    if not pilihan:
        return
    record_id = int(tabel.item(pilihan[0], "values")[0])
    
    with koneksi() as conn:
        row = conn.execute(
            "SELECT nama, nim, prodi, alamat FROM mahasiswa WHERE id = ?", 
            (record_id,)
        ).fetchone()
        
    if row is None:
        return
        
    bersihkan_form()
    entry_nama.insert(0, row[0])
    entry_nim.insert(0, row[1])
    combo_prodi.set(row[2])
    entry_alamat.insert(0, row[3] or "")

def ubah_data():
    pilihan = tabel.selection()
    if not pilihan:
        messagebox.showwarning("Pilih Data", "Pilih data yang akan diubah.")
        return
        
    record_id = int(tabel.item(pilihan[0], "values")[0])
    nama = entry_nama.get().strip()
    nim = entry_nim.get().strip()
    prodi = combo_prodi.get().strip()
    alamat = entry_alamat.get().strip()
    
    if not nama or not nim or not prodi:
        messagebox.showwarning("Validasi", "Nama, NIM, dan Program Studi wajib diisi.")
        return
        
    try:
        with koneksi() as conn:
            conn.execute(
                """
                UPDATE mahasiswa 
                SET nama = ?, nim = ?, prodi = ?, alamat = ? 
                WHERE id = ?
                """,
                (nama, nim, prodi, alamat, record_id)
            )
        tampilkan_data()
        bersihkan_form()
        messagebox.showinfo("Berhasil", "Data berhasil diperbarui.")
    except sqlite3.IntegrityError:
        messagebox.showerror("NIM Duplikat", "NIM sudah digunakan data lain.")
    except sqlite3.Error as error:
        messagebox.showerror("Kesalahan Database", str(error))

# Bind event klik pada Treeview untuk mengisi form otomatis
tabel.bind("<<TreeviewSelect>>", isi_form_dari_tabel)

# ==========================================
# 2.4.11 Menghubungkan Fungsi dengan Tombol
# ==========================================
baris_tombol = ttk.Frame(root)
baris_tombol.pack(fill="x", padx=15, pady=5)

ttk.Button(baris_tombol, text="Simpan Data", command=simpan_data).pack(side="left", padx=4)
ttk.Button(baris_tombol, text="Ubah Data", command=ubah_data).pack(side="left", padx=4)
ttk.Button(baris_tombol, text="Refresh", command=tampilkan_data).pack(side="left", padx=4)
ttk.Button(baris_tombol, text="Bersihkan Form", command=bersihkan_form).pack(side="left", padx=4)
ttk.Button(baris_tombol, text="Hapus Data Terpilih", command=hapus_data).pack(side="right", padx=4)

# ==========================================
# 2.4.12 Menjalankan Aplikasi
# ==========================================
# Memuat data lama saat aplikasi dibuka
tampilkan_data()

# Menjaga jendela tetap aktif
root.mainloop()