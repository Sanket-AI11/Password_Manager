import os
import base64
import sqlite3
import random
import string
from Crypto.Cipher import AES
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk  # For icon support

# Encryption Key (fixed for simplicity - replace with secure key management for production)
key = b'ThisIsA32ByteLongEncryptionKey!!'  # 32 bytes

# Initialize Database
def initialize_database():
    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY,
            service TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Encrypt/Decrypt
def encrypt_password(password):
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(password.encode())
    return base64.b64encode(nonce + ciphertext).decode()

def decrypt_password(encrypted_password):
    try:
        data = base64.b64decode(encrypted_password)
        nonce = data[:16]
        ciphertext = data[16:]
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        decrypted = cipher.decrypt(ciphertext)
        return decrypted.decode("utf-8")
    except (ValueError, UnicodeDecodeError, IndexError) as e:
        return "[Decryption Failed]"

# Save/Retrieve to/from DB
def save_password(service, username, encrypted_password):
    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO passwords (service, username, password) VALUES (?, ?, ?)",
                   (service, username, encrypted_password))
    conn.commit()
    conn.close()

def retrieve_password(service):
    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM passwords WHERE service = ?", (service,))
    result = cursor.fetchone()
    conn.close()
    return result

# Password Generator
def generate_password(length=16, include_special=True):
    chars = string.ascii_letters + string.digits
    if include_special:
        chars += string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

# Reset Database (Clear all stored passwords)
def reset_database():
    confirm = messagebox.askyesno("Confirm Reset", "Are you sure you want to delete all saved passwords?")
    if confirm:
        conn = sqlite3.connect("passwords.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM passwords")
        conn.commit()
        conn.close()
        messagebox.showinfo("Database Reset", "All saved passwords have been deleted.")

# GUI Functions
def add_password():
    service = simpledialog.askstring("Add Password", "Service name:")
    username = simpledialog.askstring("Add Password", "Username:")
    password = simpledialog.askstring("Add Password", "Password (leave blank to generate):", show='*')

    if not password:
        password = generate_password()
        messagebox.showinfo("Generated Password", f"Generated password: {password}")

    encrypted = encrypt_password(password)
    save_password(service, username, encrypted)
    messagebox.showinfo("Success", "Password saved successfully.")

def retrieve_password_gui():
    service = simpledialog.askstring("Retrieve Password", "Enter service name:")
    result = retrieve_password(service)
    if result:
        username, encrypted = result
        decrypted = decrypt_password(encrypted)
        if decrypted == "[Decryption Failed]":
            messagebox.showerror("Error", "Failed to decrypt password. Possible key mismatch or corrupted data.")
        else:
            messagebox.showinfo("Password Found", f"Service: {service}\nUsername: {username}\nPassword: {decrypted}")
    else:
        messagebox.showerror("Not Found", "No password found for this service.")

def generate_password_gui():
    length = simpledialog.askinteger("Password Length", "Enter password length:", minvalue=4)
    include_special = messagebox.askyesno("Special Characters", "Include special characters?")
    if length:
        pwd = generate_password(length, include_special)
        messagebox.showinfo("Generated Password", f"Password: {pwd}")

# Main GUI
def main_gui():
    initialize_database()

    root = tk.Tk()
    root.title("Secure Password Manager")
    root.geometry("500x500")  # Increased height for better spacing
    root.configure(bg="#2C3E50")  # Darker background for a professional look

    # Load icons (ensure these paths are correct)
    def load_icon(name):
        try:
            img = Image.open(name)
            return ImageTk.PhotoImage(img.resize((24, 24)))
        except Exception:
            return None

    gen_icon = load_icon("D:/LAB/password/icons/g1.png")
    ret_icon = load_icon("D:/LAB/password/icons/g1.png")
    exit_icon = load_icon("D:/LAB/password/icons/e1.png")
    reset_icon = load_icon("D:/LAB/password/icons/reset.png")

    # Create a frame for the buttons to give them proper spacing
    frame = tk.Frame(root, bg="#2C3E50")
    frame.pack(pady=20)

    # Buttons with modern UI elements and hover effects
    button_style = {
        "font": ("Roboto", 12, "bold"),
        "bg": "#3498db",
        "fg": "white",
        "width": 200,
        "height": 50,
        "relief": "flat",
        "bd": 0,
        "activebackground": "#2980b9",
        "activeforeground": "white"
    }

    def create_button(text, image, command):
        return tk.Button(frame, text=text, image=image, compound="left", command=command,
                         **button_style).pack(pady=10)

    # Adding buttons to the interface
    create_button("Generate Password", gen_icon, generate_password_gui)
    create_button("Retrieve Password", ret_icon, retrieve_password_gui)
    create_button("Add Password", gen_icon, add_password)
    create_button("Reset Database", reset_icon, reset_database)
    create_button("Exit", exit_icon, root.quit)

    root.mainloop()

if __name__ == "__main__":
    main_gui()
