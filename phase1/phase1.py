# phase1.py
import sqlite3, os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# Database filename named after your last name
DB = "SapozhnikovDB.db"
# 32-byte key for AES-256 encryption (must be exactly 32 bytes)
KEY = b'0123456789ABCDEF0123456789ABCDEF'

# encrypt_pw: encrypts plaintext password using AES-256 CBC
# returns hex string containing IV + ciphertext
def encrypt_pw(pw: str) -> str:
    iv = os.urandom(AES.block_size)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(pw.encode(), AES.block_size))
    return (iv + ct).hex()

# init_db: creates users table and adds sample users
# passwords stored encrypted (hex-encoded)
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

# Vulnerable registration: encrypts password but no SQLi protection in login
def register():
    u = input("New username: ")
    p = input("New password: ")
    hp = encrypt_pw(p)
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("INSERT INTO users VALUES(?,?)", (u, hp))
    conn.commit(); conn.close()
    print("Registered.")

# Vulnerable login: dynamic SQL allows injection via username input
def login():
    u = input("Username: ")
    p = input("Password: ")
    hp = encrypt_pw(p)
    conn = sqlite3.connect(DB); cur = conn.cursor()
    # SQLi vulnerability here:
    query = f"SELECT * FROM users WHERE username='{u}' AND password='{hp}';"
    print("Running:", query)
    cur.execute(query)
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
    print("\n-- Demo SQLi payloads for Phase 1:")
    print("1) Bypass auth: Username: ' OR '1'='1'--")
    print("2) Dump creds:    Username: ' UNION SELECT username,password FROM users--")
    print("3) Drop table:    Username: '; DROP TABLE users;--")