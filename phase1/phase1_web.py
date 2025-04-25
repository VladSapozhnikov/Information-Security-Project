# phase1_web.py

from flask import Flask, request
import sqlite3, hashlib, threading, webbrowser

DB = "users.db"
app = Flask(__name__)

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
    conn.commit(); conn.close()

BASE_HTML = '''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ display: flex; justify-content: center; align-items: center; height: 100vh; background: #f0f4f8; margin: 0; }}
    .container {{ background: #e0f3ff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); width: 300px; text-align: center; }}
    input {{ width: 100%; padding: 8px; margin: 8px 0; box-sizing: border-box; }}
    button {{ padding: 8px 16px; margin-top: 10px; }}
    a {{ margin: 0 5px; }}
  </style>
</head>
<body>
  <div class="container">
    {content}
  </div>
</body>
</html>'''

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
        hp = hashlib.sha256(p.encode()).hexdigest()
        conn = sqlite3.connect(DB); cur = conn.cursor()
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
        hp = hashlib.sha256(p.encode()).hexdigest()
        conn = sqlite3.connect(DB); cur = conn.cursor()
        query = f"SELECT * FROM users WHERE username='{u}' AND password='{hp}';"
        print("Running:", query)
        cur.execute(query)
        ok = bool(cur.fetchone()); conn.close()
        msg = "<p style='color:green;'>Login successful!</p>" if ok else "<p style='color:red;'>Login failed.</p>"
        return BASE_HTML.format(content=msg + '<a href="/">Home</a>')
    form = '''<h3>Login</h3>
<form method="post">
  <input name="username" placeholder="Username"><br>
  <input name="password" type="password" placeholder="Password"><br>
  <button type="submit">Login</button>
</form>'''
    return BASE_HTML.format(content=form)

if __name__ == "__main__":
    init_db()
    threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:5000/", new=2)).start()
    app.run(debug=True)
