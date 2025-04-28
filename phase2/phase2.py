# phase2.py
import sqlite3, os, re
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Secure DB filename for Phase 2
DB = "SapozhnikovSafeDB.db"
# Same 32-byte key for AES-256
KEY = b'0123456789ABCDEF0123456789ABCDEF'

# AES-256 encryption/decryption helpers
def encrypt_pw(pw: str) -> str:
    iv = os.urandom(AES.block_size)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(pw.encode(), AES.block_size))
    return (iv + ct).hex()

def decrypt_pw(hex_str: str) -> str:
    data = bytes.fromhex(hex_str)
    iv, ct = data[:AES.block_size], data[AES.block_size:]
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size).decode()

# valid_username: input validation blocks SQLi payloads
def valid_username(u: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_]{3,20}", u))

# init_db: creates table and sample users securely
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
      CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        password TEXT
      );
    """)
    for u, p in [('alice','alicepass'),('bob','bobpass')]:
        hp = encrypt_pw(p)
        cur.execute("INSERT OR IGNORE INTO users VALUES(?,?)", (u, hp))
    conn.commit(); conn.close()

# Secure registration: validation + parameterized query
def register():
    u = input("New username: ").strip()
    if not valid_username(u):
        print("❌ Invalid username.")
        return
    p = input("New password: ")
    hp = encrypt_pw(p)
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("INSERT INTO users VALUES(?,?)", (u, hp))
    conn.commit(); conn.close()
    print("Registered.")

# Secure login: uses parameterized SELECT to prevent SQLi
def login():
    u = input("Username: ").strip()
    p = input("Password: ")
    if not valid_username(u):
        print("❌ Invalid username.")
        return
    hp = encrypt_pw(p)
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hp))
    if cur.fetchone():
        print("🔥 Login successful!")
    else:
        print("❌ Login failed.")
    conn.close()

if __name__ == "__main__":
    init_db()
    choice = input("Register (R) or Login (L)? ").strip().lower()
    if choice == 'r':
        register()
    else:
        login()
    print("\n-- Phase 2 protected; same payloads now fail.")