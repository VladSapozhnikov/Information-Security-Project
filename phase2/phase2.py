import sqlite3, hashlib, re

DB = "users_safe.db"

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
      CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        password TEXT
      );
    """)
    cur.execute("INSERT OR IGNORE INTO users VALUES('alice', ?)",
                (hashlib.sha256(b"alicepass").hexdigest(),))
    cur.execute("INSERT OR IGNORE INTO users VALUES('bob', ?)",
                (hashlib.sha256(b"bobpass").hexdigest(),))
    conn.commit()
    conn.close()

def valid_username(u):
    return re.fullmatch(r"[A-Za-z0-9_]{3,20}", u)

def register():
    u = input("New username: ")
    if not valid_username(u):
        print("❌ Invalid username.")
        return
    p = input("New password: ")
    hp = hashlib.sha256(p.encode()).hexdigest()
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # SAFE: parameterized
    cur.execute("INSERT INTO users VALUES(?,?)", (u, hp))
    conn.commit()
    conn.close()
    print("Registered.")

def login():
    u = input("Username: ")
    p = input("Password: ")
    if not valid_username(u):
        print("❌ Invalid username.")
        return
    hp = hashlib.sha256(p.encode()).hexdigest()
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # SAFE: parameterized
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hp))
    if cur.fetchone():
        print("🔥 Login successful!")
    else:
        print("❌ Login failed.")
    conn.close()

if __name__=="__main__":
    init_db()
    choice = input("Register (R) or Login (L)? ").lower()
    if choice=="r": register()
    else: login()
    print("\n-- Try same SQLi payloads and watch them fail.")
