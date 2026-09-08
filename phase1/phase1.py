"""Deliberately vulnerable SQL injection lab using synthetic accounts."""
from contextlib import closing
from pathlib import Path
import sqlite3
import hashlib

DB = Path(__file__).with_name("demo_vulnerable.sqlite3")


def hash_pw(password):
    # Deliberately weak storage for the vulnerable half of this local lab.
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    with closing(sqlite3.connect(DB)) as conn, conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
        for username, password in [("alice", "alicepass"), ("bob", "bobpass")]:
            conn.execute("INSERT OR IGNORE INTO users VALUES (?, ?)", (username, hash_pw(password)))


def register_user(username, password):
    # Intentionally unsafe: user input becomes part of the SQL statement.
    with closing(sqlite3.connect(DB)) as conn, conn:
        conn.execute(f"INSERT INTO users VALUES ('{username}', '{hash_pw(password)}')")


def lookup_users(username, password):
    query = f"SELECT username, password FROM users WHERE username='{username}' AND password='{hash_pw(password)}'"
    with closing(sqlite3.connect(DB)) as conn:
        return conn.execute(query).fetchall()


def main():
    init_db()
    choice = input("Register (R) or Login (L)? ").strip().lower()
    username = input("Username: ")
    password = input("Password (use demo values only): ")
    if not username or not password or len(username) > 200 or len(password) > 1024:
        print("Enter a username and password within the demo limits.")
        return
    try:
        if choice == "r":
            register_user(username, password)
            print("Registered.")
        else:
            rows = lookup_users(username, password)
            print("Login successful!" if rows else "Login failed.")
            if "UNION SELECT" in username.upper():
                for user, stored_hash in rows:
                    print(f"{user}: {stored_hash}")
    except sqlite3.IntegrityError:
        print("That username already exists.")
    except sqlite3.Error:
        print("Invalid SQL input. The demo accepts one statement per request.")


if __name__ == "__main__":
    main()
