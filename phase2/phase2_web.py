from flask import Flask, request
import sqlite3, hashlib, re, threading, webbrowser

DB = "users_safe.db"
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

@app.route("/")
def index():
    content = '<h2>Phase 2: Secure Login</h2>' + \
              '<a href="/register">Register</a> | ' + \
              '<a href="/login">Login</a>'
    return BASE_HTML.format(content=content)

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        u = request.form["username"].strip()
        p = request.form["password"]
        if not re.fullmatch(r"[A-Za-z0-9_]{3,20}", u):
            return BASE_HTML.format(content="<p style='color:red;'>Invalid username.</p><a href='/register'>Try again</a>")
        hp = hashlib.sha256(p.encode()).hexdigest()
        conn = sqlite3.connect(DB); cur = conn.cursor()
        cur.execute("INSERT INTO users VALUES(?,?)", (u, hp))  # SAFE
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
        u = request.form["username"].strip()
        p = request.form["password"]
        if not re.fullmatch(r"[A-Za-z0-9_]{3,20}", u):
            return BASE_HTML.format(content="<p style='color:red;'>Invalid username.</p><a href='/login'>Try again</a>")
        hp = hashlib.sha256(p.encode()).hexdigest()
        conn = sqlite3.connect(DB); cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hp))  # SAFE
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
    threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:5001/", new=2)).start()
    app.run(debug=True, port=5001)