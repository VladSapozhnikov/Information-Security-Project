import sqlite3, hashlib, os

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
    # sample user
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
    # VULNERABLE: string formatting
    cur.execute(f"INSERT INTO users VALUES('{u}','{hp}');")
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
        print("🔥 Login successful!")
    else:
        print("❌ Login failed.")
    conn.close()

if __name__=="__main__":
    init_db()
    choice = input("Register (R) or Login (L)? ").lower()
    if choice=="r": register()
    else: login()
    print("\n-- Try SQL injection payloads like:")
    print("   Username: ' OR '1'='1   Password: anything")
    print("   Username: alice';--     Password: anything")
    print("   Username: ' UNION SELECT username,password FROM users;--")
