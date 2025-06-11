import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import sqlite3

# Koneksi ke database (jika belum ada, akan dibuat)
conn = sqlite3.connect("perpustakaan.db")
cursor = conn.cursor()

# Buat tabel buku
cursor.execute('''
CREATE TABLE IF NOT EXISTS buku (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    judul TEXT,
    status TEXT,
    tanggal_pinjam TEXT
)
''')

# Buat tabel riwayat peminjaman
cursor.execute('''
CREATE TABLE IF NOT EXISTS riwayat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    judul TEXT,
    tanggal TEXT
)
''')

# Cek apakah data sudah ada, jika belum, isi data awal
cursor.execute("SELECT COUNT(*) FROM buku")
if cursor.fetchone()[0] == 0:
    data_awal = [
        ("Sejarah", "Tersedia", None),
        ("Bahasa Indonesia", "Tersedia", None),
        ("Matematika", "Dipinjam", "2025-05-25"),
        ("Ilmu Pengetahuan Alam", "Dipinjam", "2025-05-26"),
    ]
    cursor.executemany("INSERT INTO buku (judul, status, tanggal_pinjam) VALUES (?, ?, ?)", data_awal)
    cursor.executemany("INSERT INTO riwayat (nama, judul, tanggal) VALUES (?, ?, ?)", [
        ("Andi", "Matematika", "2025-05-25"),
        ("Budi", "Ilmu Pengetahuan Alam", "2025-05-26"),
    ])
    conn.commit()

# Fungsi untuk memperbarui daftar buku
def tampilkan_buku():
    listbox.delete(0, tk.END)
    cursor.execute("SELECT judul, status, tanggal_pinjam FROM buku")
    for judul, status, tanggal in cursor.fetchall():
        if status == "Dipinjam" and tanggal:
            listbox.insert(tk.END, f"{judul} ({status} - {tanggal})")
        else:
            listbox.insert(tk.END, f"{judul} ({status})")

# Fungsi untuk memperbarui daftar peminjam
def tampilkan_peminjam():
    list_peminjam.delete(0, tk.END)
    cursor.execute("SELECT nama, judul, tanggal FROM riwayat ORDER BY id DESC")
    for nama, judul, tanggal in cursor.fetchall():
        list_peminjam.insert(tk.END, f"{nama} meminjam '{judul}' pada {tanggal}")

# Fungsi meminjam buku
def pinjam_buku():
    nama = entry_nama.get()
    if not nama:
        messagebox.showwarning("Peringatan", "Masukkan nama peminjam terlebih dahulu.")
        return
    pilih = listbox.curselection()
    if not pilih:
        messagebox.showwarning("Peringatan", "Pilih buku yang ingin dipinjam.")
        return

    judul = listbox.get(pilih[0]).split(" (")[0]
    cursor.execute("SELECT status FROM buku WHERE judul=?", (judul,))
    result = cursor.fetchone()
    if result and result[0] == "Tersedia":
        tanggal = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("UPDATE buku SET status='Dipinjam', tanggal_pinjam=? WHERE judul=?", (tanggal, judul))
        cursor.execute("INSERT INTO riwayat (nama, judul, tanggal) VALUES (?, ?, ?)", (nama, judul, tanggal))
        conn.commit()
        messagebox.showinfo("Berhasil", f"{nama} berhasil meminjam '{judul}' pada {tanggal}.")
    else:
        messagebox.showerror("Gagal", f"Buku '{judul}' sedang dipinjam.")
    tampilkan_buku()
    tampilkan_peminjam()

# Fungsi mengembalikan buku
def kembalikan_buku():
    pilih = listbox.curselection()
    if not pilih:
        messagebox.showwarning("Peringatan", "Pilih buku yang ingin dikembalikan.")
        return

    judul = listbox.get(pilih[0]).split(" (")[0]
    cursor.execute("SELECT status FROM buku WHERE judul=?", (judul,))
    result = cursor.fetchone()
    if result and result[0] == "Dipinjam":
        cursor.execute("UPDATE buku SET status='Tersedia', tanggal_pinjam=NULL WHERE judul=?", (judul,))
        conn.commit()
        messagebox.showinfo("Berhasil", f"Buku '{judul}' berhasil dikembalikan.")
    else:
        messagebox.showinfo("Info", f"Buku '{judul}' belum dipinjam.")
    tampilkan_buku()

# UI
root = tk.Tk()
root.title("Aplikasi Peminjaman Buku")
root.geometry("400x500")
root.config(bg="#f0f0f0")

frame = tk.Frame(root, padx=10, pady=10, bg="#f0f0f0")
frame.pack(pady=10)

tk.Label(frame, text="Nama Peminjam:", bg="#f0f0f0").pack()
entry_nama = tk.Entry(frame, width=40)
entry_nama.pack(pady=5)

tk.Label(frame, text="Daftar Buku:", bg="#f0f0f0").pack()
listbox = tk.Listbox(frame, width=50)
listbox.pack(pady=5)

tampilkan_buku()

btn_frame = tk.Frame(frame, bg="#f0f0f0")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Pinjam Buku", width=15, command=pinjam_buku, bg="#a0d2eb").pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Kembalikan Buku", width=15, command=kembalikan_buku, bg="#c2f0c2").pack(side=tk.LEFT, padx=5)

# Label dan Listbox untuk peminjam
tk.Label(frame, text="Daftar Peminjam:", bg="#f0f0f0").pack(pady=5)
list_peminjam = tk.Listbox(frame, width=50)
list_peminjam.pack()

tampilkan_peminjam()

# Fungsi menutup aplikasi dan menutup koneksi database
def on_closing():
    conn.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
