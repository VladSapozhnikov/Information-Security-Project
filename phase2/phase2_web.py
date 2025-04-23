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

def valid_username(u):
    return re.fullmatch(r"[A-Za-z0-9_]{3,20}", u)

@app.route("/")
def index():
    return """
      <h1>Phase 2: Secure Login</h1>
      <a href="/register">Register</a> | <a href="/login">Login</a>
    """

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        u = request.form["username"].strip()
        p = request.form["password"]
        if not valid_username(u):
            return "<p>Invalid username.</p><a href='/register'>Try again</a>"
        hp = hashlib.sha256(p.encode()).hexdigest()
        conn = sqlite3.connect(DB); cur = conn.cursor()
        # SAFE:
        cur.execute("INSERT INTO users VALUES(?,?)", (u, hp))
        conn.commit(); conn.close()
        return f"<p>Registered {u}.</p><a href='/'>Home</a>"
    return """
      <form method="post">
        Username: <input name="username"><br>
        Password: <input name="password" type="password"><br>
        <button type="submit">Register</button>
      </form>
    """

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u = request.form["username"].strip()
        p = request.form["password"]
        if not valid_username(u):
            return "<p>Invalid username.</p><a href='/login'>Try again</a>"
        hp = hashlib.sha256(p.encode()).hexdigest()
        conn = sqlite3.connect(DB); cur = conn.cursor()
        # SAFE:
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hp))
        ok = bool(cur.fetchone()); conn.close()
        return ("<p>Login successful!</p>" if ok else "<p>Login failed.</p>") + "<a href='/'>Home</a>"
    return """
      <form method="post">
        Username: <input name="username"><br>
        Password: <input name="password" type="password"><br>
        <button type="submit">Login</button>
      </form>
    """

if __name__=="__main__":
    init_db()
    threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:5001/")).start()
    app.run(debug=True, port=5001)
