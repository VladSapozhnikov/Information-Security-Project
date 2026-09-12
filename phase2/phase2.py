"""SQL injection mitigation lab using bound parameters and password hashing."""
from contextlib import closing
from pathlib import Path
import sqlite3
import re
from werkzeug.security import check_password_hash, generate_password_hash

DB = Path(__file__).with_name("demo_protected.sqlite3")


def valid_username(username):
    return bool(re.fullmatch(r"[A-Za-z0-9_]{3,20}", username))


def init_db():
    with closing(sqlite3.connect(DB)) as conn, conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
        for username, password in [("alice", "alicepass"), ("bob", "bobpass")]:
            conn.execute(
                "INSERT OR IGNORE INTO users VALUES (?, ?)",
                (username, generate_password_hash(password, method="scrypt")),
            )


def register_user(username, password):
    if not valid_username(username) or not password or len(password) > 1024:
        raise ValueError("Use a 3-20 character username (letters, digits, underscore) and a nonempty password up to 1024 characters.")
    with closing(sqlite3.connect(DB)) as conn, conn:
        conn.execute(
            "INSERT INTO users VALUES (?, ?)",
            (username, generate_password_hash(password, method="scrypt")),
        )


def authenticate(username, password):
    if not username or not password or len(username) > 200 or len(password) > 1024:
        return False
    # The SQL structure stays fixed even when the username contains SQL syntax.
    with closing(sqlite3.connect(DB)) as conn:
        row = conn.execute("SELECT password FROM users WHERE username = ?", (username,)).fetchone()
    return bool(row and check_password_hash(row[0], password))


def main():
    init_db()
    choice = input("Register (R) or Login (L)? ").strip().lower()
    username = input("Username: ").strip()
    password = input("Password (use demo values only): ")
    try:
        if choice == "r":
            register_user(username, password)
            print("Registered.")
        else:
            print("Login successful!" if authenticate(username, password) else "Login failed.")
    except ValueError as error:
        print(error)
    except sqlite3.IntegrityError:
        print("That username already exists.")


if __name__ == "__main__":
    main()
