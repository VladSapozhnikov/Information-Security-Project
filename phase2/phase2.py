# phase2.py
import sqlite3, os, re
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Secure DB name for phase 2
DB = "SapozhnikovSafeDB.db"
KEY = b'my_32_byte_super_secret_key________'

# encrypt_pw and decrypt_pw: AES-256 CBC encryption/decryption
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

# valid_username: ensures only letters, digits, underscore; length 3-20
def valid_username(u: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_]{3,20}", u))

# init_db: create table and sample users securely encrypted
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
    conn.commit()
    conn.close()

# register: secure registration with validation + parameterized query
def register():
    u = input("New username: ").strip()
    if not valid_username(u):
        print("❌ Invalid username.")  # input validation blocks SQLi
        return
    p = input("New password: ")
    hp = encrypt_pw(p)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # safe INSERT using placeholders
    cur.execute("INSERT INTO users VALUES(?,?)", (u, hp))
    conn.commit()
    conn.close()
    print("Registered.")

# login: secure login using parameterized SELECT
def login():
    u = input("Username: ").strip()
    if not valid_username(u):
        print("❌ Invalid username.")
        return
    p = input("Password: ")
    hp = encrypt_pw(p)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # safe SELECT prevents SQLi
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hp))
    if cur.fetchone():
        print("🔥 Login successful!")
    else:
        print("❌ Login failed.")
    conn.close()

if __name__ == "__main__":
    init_db()                           # setup database
    choice = input("Register (R) or Login (L)? ").strip().lower()
    if choice == 'r':
        register()
    else:
        login()
    print("\n-- Phase 2 is now protected; same payloads should fail.")