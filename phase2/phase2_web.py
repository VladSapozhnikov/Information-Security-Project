"""Local web interface for the protected SQL injection lab."""
from flask import Flask, request
from html import escape
import sqlite3

if __package__:
    from . import phase2 as demo
else:
    import phase2 as demo

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
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


def page(content):
    return BASE_HTML.format(content=content)


def form(action):
    return page(f"""<h3>{action.title()}</h3>
<form method="post">
  <input name="username" placeholder="Username" required maxlength="200"><br>
  <input name="password" type="password" placeholder="Password" required maxlength="1024"><br>
  <button type="submit">{action.title()}</button>
</form>
<p>Local lab. Use demo accounts only.</p><a href="/">Home</a>""")


@app.route("/")
def index():
    return page('<h2>Phase 2: Protected Login</h2>'
                '<p>SQL injection learning lab</p>'
                '<a href="/register">Register</a> | <a href="/login">Login</a>')


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return form("register")
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if not username or not password or len(username) > 200 or len(password) > 1024:
        return page("<p>Enter a username and password within the demo limits.</p>"), 400
    try:
        demo.register_user(username, password)
    except ValueError as error:
        return page(f"<p>{escape(str(error))}</p>"), 400
    except sqlite3.IntegrityError:
        return page("<p>That username already exists.</p>"), 409
    except sqlite3.Error:
        return page("<p>Invalid SQL input.</p>"), 400
    return page(f"<p>Registered <b>{escape(username)}</b>.</p><a href='/'>Home</a>"), 201


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return form("login")
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if not username or not password or len(username) > 200 or len(password) > 1024:
        return page("<p>Enter a username and password within the demo limits.</p>"), 400
    ok = demo.authenticate(username, password)
    content = "<p>Login successful!</p>" if ok else "<p>Login failed.</p>"
    return page(content + '<p><a href="/">Home</a></p>')


if __name__ == "__main__":
    demo.init_db()
    app.run(host="127.0.0.1", port=5001, debug=False)
