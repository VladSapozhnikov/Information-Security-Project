# phase1.py
import sqlite3, os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# Database named after your last name
DB = "SapozhnikovDB.db"
# 32-byte key for AES-256 encryption (must be kept secret)
KEY = b'my_32_byte_super_secret_key________'

# encrypt_pw: encrypts plaintext password using AES-256 CBC
# returns hex string of IV + ciphertext
def encrypt_pw(pw: str) -> str:
    iv = os.urandom(AES.block_size)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(pw.encode(), AES.block_size))
    return (iv + ct).hex()

# init_db: creates the users table and inserts sample users
# passwords are stored encrypted (hex-encoded)
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
      CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        password TEXT
      );
    """)
    # insert sample users with encrypted passwords
    for u, p in [('alice','alicepass'),('bob','bobpass')]:
        hp = encrypt_pw(p)
        cur.execute("INSERT OR IGNORE INTO users VALUES(?,?)", (u, hp))
    conn.commit()
    conn.close()

# register: vulnerable registration that stores encrypted password
def register():
    u = input("New username: ")       # user input for username
    p = input("New password: ")       # user input for password
    hp = encrypt_pw(p)                  # encrypt the password
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # vulnerable INSERT uses parameterized here, but login is vulnerable
    cur.execute("INSERT INTO users VALUES(?,?)", (u, hp))
    conn.commit()
    conn.close()
    print("Registered.")

# login: vulnerable to SQL injection in the WHERE clause
def login():
    u = input("Username: ")           # user input for username
    p = input("Password: ")           # user input for password
    hp = encrypt_pw(p)                  # encrypt the password
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # vulnerability: dynamic SQL using f-string
    query = f"SELECT * FROM users WHERE username='{u}' AND password='{hp}';"
    print("Running:", query)          # show the exact query
    cur.execute(query)                  # executes possibly injected SQL
    if cur.fetchone():                  # successful login if any row returned
        print("🔥 Login successful!")
    else:
        print("❌ Login failed.")
    conn.close()

if __name__ == "__main__":
    init_db()                           # ensure DB and sample data exist
    choice = input("Register (R) or Login (L)? ").strip().lower()
    if choice == 'r':
        register()
    else:
        login()
    print("\n-- Demo SQLi payloads for phase 1:")
    print("1) Bypass auth: Username: ' OR '1'='1'--, any password")
    print("2) Dump creds:    Username: ' UNION SELECT username,password FROM users--, any password")
    print("3) Drop table:    Username: '; DROP TABLE users;--, any password")