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

@app.route("/")
def index():
    return """
      <h1>Phase 1: Vulnerable Login</h1>
      <a href="/register">Register</a> | <a href="/login">Login</a>
    """

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        u = request.form["username"]
        p = request.form["password"]
        hp = hashlib.sha256(p.encode()).hexdigest()
        conn = sqlite3.connect(DB); cur = conn.cursor()
        # VULNERABLE:
        cur.execute(f"INSERT INTO users VALUES('{u}','{hp}');")
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
        u = request.form["username"]
        p = request.form["password"]
        hp = hashlib.sha256(p.encode()).hexdigest()
        conn = sqlite3.connect(DB); cur = conn.cursor()
        # VULNERABLE:
        query = f"SELECT * FROM users WHERE username='{u}' AND password='{hp}';"
        print("Running:", query)
        cur.execute(query)
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
    threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:5000/")).start()
    app.run(debug=True)
