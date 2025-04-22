# phase1/phase1.py

import sqlite3
import hashlib

DB = "users.db"

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
      CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        password TEXT
      );
    """)
    # sample data
    cur.execute("INSERT OR IGNORE INTO users VALUES('alice', ?)",
                (hashlib.sha256(b"alicepass").hexdigest(),))
    cur.execute("INSERT OR IGNORE INTO users VALUES('bob', ?)",
                (hashlib.sha256(b"bobpass").hexdigest(),))
    conn.commit()
    conn.close()

def register():
    u = input("New username: ")
    p = input("New password: ")
    hp = hashlib.sha256(p.encode()).hexdigest()
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # VULNERABLE: direct string formatting
    query = f"INSERT INTO users VALUES('{u}','{hp}');"
    print("Running:", query)
    cur.execute(query)
    conn.commit()
    conn.close()
    print("Registered.")

def login():
    u = input("Username: ")
    p = input("Password: ")
    hp = hashlib.sha256(p.encode()).hexdigest()
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # VULNERABLE: raw query
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
    if choice == "r":
        register()
    else:
        login()
    print("\n-- Try SQLi payloads like:")
    print("   ' OR '1'='1'--")
    print("   ' UNION SELECT username,password FROM users--")
    print("   '; DROP TABLE users;--")
