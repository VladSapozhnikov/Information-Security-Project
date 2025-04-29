import sqlite3, os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# Database and AES key
DB = "SapozhnikovDB.db"
KEY = b'0123456789ABCDEF0123456789ABCDEF'  # 32-byte key

# AES-256 encrypt
def encrypt_pw(pw: str) -> str:
    iv = os.urandom(AES.block_size)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(pw.encode(), AES.block_size))
    return (iv + ct).hex()

# Setup DB + sample users
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

# Vulnerable login using dynamic SQL
def login():
    u = input("Username: ")
    p = input("Password: ")
    hp = encrypt_pw(p)
    conn = sqlite3.connect(DB); cur = conn.cursor()
    query = f"SELECT * FROM users WHERE username='{u}' AND password='{hp}';"
    print("Running:", query)
    cur.execute(query)
    if cur.fetchone(): print("🔥 Login successful!")
    else: print("❌ Login failed.")
    conn.close()

# Vulnerable register
def register():
    u = input("New username: ")
    p = input("New password: ")
    hp = encrypt_pw(p)
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute(f"INSERT INTO users VALUES('{u}','{hp}');")
    conn.commit(); conn.close()
    print("Registered.")

if __name__ == "__main__":
    init_db()
    choice = input("Register (R) or Login (L)? ").strip().lower()
    if choice == 'r': register()
    else: login()
    print("\n-- Try SQLi:\n   ' OR '1'='1'--\n   ' UNION SELECT username,password FROM users--\n   '; DROP TABLE users;--")