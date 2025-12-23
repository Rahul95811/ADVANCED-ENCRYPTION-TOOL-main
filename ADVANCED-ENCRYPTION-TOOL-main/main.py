import tkinter as tk
from tkinter import filedialog, messagebox
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os
import base64

BACKEND = default_backend()
SALT_SIZE = 16
KEY_SIZE = 32  # 256 bits
ITERATIONS = 100_000
BLOCK_SIZE = 128


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=ITERATIONS,
        backend=BACKEND
    )
    return kdf.derive(password.encode())


def encrypt_file(filepath, password):
    with open(filepath, 'rb') as f:
        data = f.read()
    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    iv = os.urandom(16)
    padder = padding.PKCS7(BLOCK_SIZE).padder()
    padded_data = padder.update(data) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=BACKEND)
    encryptor = cipher.encryptor()
    ct = encryptor.update(padded_data) + encryptor.finalize()
    with open(filepath + '.enc', 'wb') as f:
        f.write(salt + iv + ct)


def decrypt_file(filepath, password):
    with open(filepath, 'rb') as f:
        filedata = f.read()
    salt = filedata[:SALT_SIZE]
    iv = filedata[SALT_SIZE:SALT_SIZE+16]
    ct = filedata[SALT_SIZE+16:]
    key = derive_key(password, salt)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=BACKEND)
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ct) + decryptor.finalize()
    unpadder = padding.PKCS7(BLOCK_SIZE).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    outpath = filepath.replace('.enc', '.dec')
    with open(outpath, 'wb') as f:
        f.write(data)


def select_file():
    filename = filedialog.askopenfilename()
    file_var.set(filename)

def encrypt_action():
    filepath = file_var.get()
    password = pass_var.get()
    if not filepath or not password:
        messagebox.showerror('Error', 'Please select a file and enter a password.')
        return
    try:
        encrypt_file(filepath, password)
        messagebox.showinfo('Success', f'File encrypted: {filepath}.enc')
    except Exception as e:
        messagebox.showerror('Error', str(e))

def decrypt_action():
    filepath = file_var.get()
    password = pass_var.get()
    if not filepath or not password:
        messagebox.showerror('Error', 'Please select a file and enter a password.')
        return
    try:
        decrypt_file(filepath, password)
        messagebox.showinfo('Success', f'File decrypted: {filepath.replace('.enc', '.dec')}')
    except Exception as e:
        messagebox.showerror('Error', str(e))

root = tk.Tk()
root.title('AES-256 Encryption Tool')
root.geometry('400x250')

file_var = tk.StringVar()
pass_var = tk.StringVar()

frame = tk.Frame(root, padx=20, pady=20)
frame.pack(expand=True)

file_label = tk.Label(frame, text='File:')
file_label.grid(row=0, column=0, sticky='e')
file_entry = tk.Entry(frame, textvariable=file_var, width=30)
file_entry.grid(row=0, column=1)
file_btn = tk.Button(frame, text='Browse', command=select_file)
file_btn.grid(row=0, column=2)

pass_label = tk.Label(frame, text='Password:')
pass_label.grid(row=1, column=0, sticky='e')
pass_entry = tk.Entry(frame, textvariable=pass_var, show='*', width=30)
pass_entry.grid(row=1, column=1)

enc_btn = tk.Button(frame, text='Encrypt', command=encrypt_action, width=12, bg='#4CAF50', fg='white')
enc_btn.grid(row=2, column=1, pady=10, sticky='w')
dec_btn = tk.Button(frame, text='Decrypt', command=decrypt_action, width=12, bg='#2196F3', fg='white')
dec_btn.grid(row=2, column=1, pady=10, sticky='e')

root.mainloop() 