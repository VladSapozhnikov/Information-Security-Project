# phase1_web.py

from flask import Flask, request
import sqlite3, hashlib, threading, webbrowser, os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# Database and encryption setup
DB = "SapozhnikovDB.db"
KEY = b'0123456789ABCDEF0123456789ABCDEF'  # 32-byte AES key

# HTML template with escaped braces
BASE_HTML = '''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ display: flex; justify-content: center; align-items: center; height: 100vh; background: #f0f4f8; margin: 0; }}
    .container {{ background: #e0f3ff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); width: 300px; text-align: center; }}
    input {{ width: 100%; padding: 8px; margin: 8px 0; box-sizing: border-box; }}
    button {{ padding: 8px 16px; margin-top: 10px; }}
    ul {{ text-align: left; padding-left: 20px; }}
    li {{ margin-bottom: 4px; font-family: monospace; }}
    a {{ margin: 0 5px; display: inline-block; }}
  </style>
</head>
<body>
  <div class="container">
    {content}
  </div>
</body>
</html>'''

app = Flask(__name__)

def encrypt_pw(pw: str) -> str:
    iv = os.urandom(AES.block_size)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(pw.encode(), AES.block_size))
    return (iv + ct).hex()

@app.route("/")
def index():
    content = '<h2>Phase 1: Vulnerable Login</h2>' + \
              '<a href="/register">Register</a> | ' + \
              '<a href="/login">Login</a>'
    return BASE_HTML.format(content=content)

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        hp = encrypt_pw(p)
        conn = sqlite3.connect(DB); cur = conn.cursor()
        # Vulnerable: direct insert
        cur.execute(f"INSERT INTO users VALUES('{u}','{hp}');")
        conn.commit(); conn.close()
        return BASE_HTML.format(content=f"<p>Registered <b>{u}</b>.</p><a href='/'>Home</a>")
    form = '''<h3>Register</h3>
<form method="post">
  <input name="username" placeholder="Username"><br>
  <input name="password" type="password" placeholder="Password"><br>
  <button type="submit">Register</button>
</form>'''
    return BASE_HTML.format(content=form)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        hp = encrypt_pw(p)
        conn = sqlite3.connect(DB); cur = conn.cursor()
        # Vulnerable dynamic SQL allows SQLi
        query = f"SELECT * FROM users WHERE username='{u}' AND password='{hp}';"
        print("Running:", query)
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()
        if rows:
            # Display stolen credentials
            list_items = ''.join(f"<li>{r[0]} : {r[1]}</li>" for r in rows)
            content = "<p style='color:green;'>Login successful!</p>"
            content += f"<ul>{list_items}</ul>"
        else:
            content = "<p style='color:red;'>Login failed.</p>"
        content += '<p><a href="/">Home</a></p>'
        return BASE_HTML.format(content=content)
    form = '''<h3>Login</h3>
<form method="post">
  <input name="username" placeholder="Username"><br>
  <input name="password" type="password" placeholder="Password"><br>
  <button type="submit">Login</button>
</form>'''
    return BASE_HTML.format(content=form)

if __name__ == "__main__":
    # Initialize DB and sample data
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
    # Launch browser
    threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:5000/", new=2)).start()
    app.run(debug=True)
