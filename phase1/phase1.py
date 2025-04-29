import sqlite3, os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# Database and AES key setup
DB = "SapozhnikovDB.db"
KEY = b'0123456789ABCDEF0123456789ABCDEF'  # 32-byte AES key

# Helper: AES-256 encrypts password, returns hex string of IV+ciphertext
def encrypt_pw(pw: str) -> str:
    iv = os.urandom(AES.block_size)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(pw.encode(), AES.block_size))
    return (iv + ct).hex()

# Initialize database and insert sample users
# Vulnerable code uses static AES encryption but no SQL protections
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
      CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        password TEXT
      );
    """)
    # Insert test users
    for u, p in [('alice','alicepass'),('bob','bobpass')]:
        hp = encrypt_pw(p)
        cur.execute("INSERT OR IGNORE INTO users VALUES(?,?)", (u, hp))
    conn.commit()
    conn.close()

# Vulnerable registration: SQL injection possible if attackers alter INSERT f-string
def register():
    u = input("New username: ")     # attacker can include SQL keywords here
    p = input("New password: ")
    hp = encrypt_pw(p)
    conn = sqlite3.connect(DB); cur = conn.cursor()
    # VULNERABILITY: direct f-string insertion allows injection in VALUES()
    cur.execute(f"INSERT INTO users VALUES('{u}','{hp}');")
    conn.commit(); conn.close()
    print("Registered.")

# Vulnerable login: builds SQL with user input, allows 3 attacks:
# 1) Authentication bypass, 2) Credential dump, 3) DROP table
def login():
    u = input("Username: ")        # attacker-controlled input
    p = input("Password: ")
    hp = encrypt_pw(p)
    conn = sqlite3.connect(DB); cur = conn.cursor()

    # VULNERABILITY: dynamic SQL with f-string
    # --------------------------
    # This line can be broken by:
    # 1) "' OR '1'='1'--" to bypass auth
    # 2) "' UNION SELECT username,password FROM users--" to dump creds
    # 3) "'; DROP TABLE users;--" to delete table
    query = f"SELECT * FROM users WHERE username='{u}' AND password='{hp}';"
    # --------------------------
    print("Running:", query)

    # Dropped table Alert
    if 'DROP TABLE' in query.upper():
        cur.executescript(query)
        conn.close()
        print("⚠️ Table dropped!")
        return

    # Normal SELECT for bypass or dump
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    # Determine outcome
    if 'UNION SELECT' in query.upper():
        # Attack 2: Dump credentials
        print("🔥 Dumping credentials:")
        for r in rows:
            print(f"- {r[0]} : {r[1]}")
    elif rows:
        # Attack 1: Authentication bypass or valid login
        print("🔥 Login successful!")
    else:
        print("❌ Login failed.")

if __name__ == "__main__":
    init_db()
    choice = input("Register (R) or Login (L)? ").strip().lower()
    if choice == 'r':
        register()
    else:
        login()
    print("\n-- Try SQLi payloads: (1) ' OR '1'='1'--  (2) ' UNION SELECT username,password FROM users--  (3) '; DROP TABLE users;--")