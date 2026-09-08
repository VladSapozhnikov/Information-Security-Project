# SQL Injection: Vulnerability and Mitigation Lab

A small Python, Flask, and SQLite learning project that compares a vulnerable login with a protected implementation. It began as information security coursework. The maintained version adds working login flows, repeatable setup, and regression checks.

The goal is to explain a security finding clearly: reproduce it, identify its cause, apply a fix, and verify the result.

## What the lab demonstrates

| Behavior | Phase 1: vulnerable | Phase 2: protected |
| --- | --- | --- |
| Correct demo credentials | Login succeeds | Login succeeds |
| Incorrect password | Login fails | Login fails |
| SQL injection in username | Can bypass login or disclose demo hashes | Treated as data; login fails |
| Password storage | Deliberately weak, unsalted SHA-256 | Salted scrypt password hashes |
| Database queries | SQL strings include user input | Bound parameters |
| Interface | Command line or local browser | Command line or local browser |

**Run locally with synthetic data only.** Phase 1 is deliberately vulnerable. Phase 2 demonstrates specific mitigations, not a production authentication system. Neither creates a logged-in session or protects a real account.

## Setup

Requires Python 3.10 or later.

Clone or download this repository, then open a terminal in its root folder.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m phase1.phase1_web
```

In a second terminal, from the same folder:

```powershell
.\.venv\Scripts\python.exe -m phase2.phase2_web
```

### Linux or macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m phase1.phase1_web
```

In a second terminal:

```bash
.venv/bin/python -m phase2.phase2_web
```

Open [Phase 1](http://127.0.0.1:5000) and [Phase 2](http://127.0.0.1:5001). Both servers bind to the local computer, with debug mode disabled. Stop them with Ctrl+C.

Demo accounts: `alice / alicepass` and `bob / bobpass`.

For the command-line interfaces, replace `phase1.phase1_web` with `phase1.phase1`, or `phase2.phase2_web` with `phase2.phase2`.

## Five-minute comparison

1. Log in to both phases with `alice / alicepass`. Both should succeed.
2. Try `alice / wrong`. Both should fail.
3. Enter `' OR '1'='1'--` as the username and `wrong` as the password. Phase 1 succeeds; Phase 2 fails.
4. Enter `' UNION SELECT username,password FROM users--` as the username with `wrong` as the password. Phase 1 displays the synthetic account hashes; Phase 2 fails.
5. Read the query in `phase1/phase1.py` beside the query in `phase2/phase2.py`. In Phase 2, the placeholder binds the complete username as a value.

The username rules on protected registration are a separate input policy. The login tests pass SQL syntax to the database through a bound parameter, so the result does not rely on filtering out quote characters.

See [the test plan](docs/TEST_PLAN.md) for expected outcomes and [the maintenance notes](docs/MAINTENANCE.md) for the original defects and repairs.

## Automated checks

Windows:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Linux or macOS:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

The checks use temporary databases and Flask's test client. They cover valid and invalid logins, registration, injection, duplicate users, password hashing, escaped output, and command-line startup.

## Files and data

- `phase1/`: deliberately vulnerable command-line and web versions.
- `phase2/`: protected command-line and web versions.
- `tests/`: behavioral regression checks.
- `docs/`: test plan and repair history.

Each phase creates a new `demo_*.sqlite3` database next to its Python module. Generated databases are ignored by Git. Existing coursework `.db` files are retained as legacy artifacts but are not read or modified by this version.

To reset the lab, stop both servers and remove only `phase1/demo_vulnerable.sqlite3` and `phase2/demo_protected.sqlite3`. Restart to restore the two demo accounts.

## Limits

This lab has no sessions, account recovery, multifactor authentication, or rate limiting. The forms do not implement CSRF protection. It is a local SQL injection demonstration, not a deployable login service. Stacked queries such as `'; DROP TABLE users;--` are rejected by Phase 1's single-statement execution; the older special-case destructive execution path has been removed.

## References

- [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html): separating SQL structure from supplied values.
- [Werkzeug password hashing](https://werkzeug.palletsprojects.com/en/stable/utils/#werkzeug.security.generate_password_hash): scrypt hash generation and verification.
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/): testing HTTP routes without starting a public server.
