import sqlite3, os, re
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Secure DB and AES key
def decrypt_pw(hex_str: str) -> str:
    data = bytes.fromhex(hex_str)
    iv, ct = data[:AES.block_size], data[AES.block_size:]
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size).decode()

DB = "SapozhnikovSafeDB.db"
KEY = b'0123456789ABCDEF0123456789ABCDEF'

# Input validation blocks SQLi
def valid_username(u: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_]{3,20}", u))

# Setup DB + secure users
def init_db():
    conn = sqlite3.connect(DB); cur = conn.cursor()
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

# Secure register: parameterized + validation
def register():
    u = input("New username: ").strip()
    # Validation prevents quotes, operators
    if not valid_username(u): print("❌ Invalid username."); return
    p = input("New password: ")
    hp = encrypt_pw(p)
    conn = sqlite3.connect(DB); cur = conn.cursor()
    # Parameterized query prevents SQL injection
    cur.execute("INSERT INTO users VALUES(?,?)", (u, hp))
    conn.commit(); conn.close()
    print("Registered.")

# Secure login: parameterized SELECT prevents SQLi
def login():
    u = input("Username: ").strip()
    if not valid_username(u): print("❌ Invalid username."); return
    p = input("Password: ")
    hp = encrypt_pw(p)
    conn = sqlite3.connect(DB); cur = conn.cursor()
    # No f-strings: structure fixed, data separate
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hp))
    if cur.fetchone(): print("🔥 Login successful!")
    else: print("❌ Login failed.")
    conn.close()

if __name__ == "__main__":
    init_db()
    choice = input("Register (R) or Login (L)? ").strip().lower()
    if choice == 'r': register()
    else: login()
    print("\n-- Phase 2 secure: same payloads now fail.")