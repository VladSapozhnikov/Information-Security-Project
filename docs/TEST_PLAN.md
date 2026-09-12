# Test Plan: SQL Injection Lab

This plan can be followed through the two local browser interfaces. Automated equivalents are in `tests/test_demo.py`.

The regression suite was run with Python 3.12, Flask 3.1.3, and Werkzeug 3.1.8 on Linux. All 13 test methods passed. HTTP behavior was checked using Flask's test client; a graphical browser and Windows were not tested in that run. The steps below are a reproducible manual checklist, not a claim that a person completed a browser session.

## Preparation

Follow the README setup instructions. Start Phase 1 on port 5000 and Phase 2 on port 5001. Use only the built-in synthetic accounts or newly invented demo credentials.

For a clean manual run, reset the generated databases as described in the README.

## Cases

| ID | Action | Phase 1 expected result | Phase 2 expected result |
| --- | --- | --- | --- |
| T01 | Open home, registration, and login | Forms load | Forms load |
| T02 | Log in twice with alice / alicepass | Succeeds both times | Succeeds both times |
| T03 | Log in with alice / wrong | Fails | Fails |
| T04 | Log in with an unknown username | Fails | Fails |
| T05 | Register charlie / demo-pass, then log in | Registration and login succeed | Registration and login succeed |
| T06 | Register alice again | Duplicate message; existing login still works | Duplicate message; existing login still works |
| T07 | Use the bypass input below as username | Login succeeds without the correct password | Login fails |
| T08 | Use the UNION input below as username | Synthetic usernames and stored hashes appear | Login fails; account hashes are not disclosed |
| T09 | Use the stacked-query input below as username | Controlled error; users table remains | Login fails; users table remains |
| T10 | Submit a request with missing fields or excessive length | HTTP 400 | HTTP 400 |
| T11 | Register a username containing a space | Deliberately permissive | Validation message, HTTP 400 |
| T12 | Register two accounts with the same password; inspect their stored values | Not a secure storage example | Different scrypt hashes; correct password still works |
| T13 | Register a username containing HTML markup | Markup is displayed as text | Username validation rejects markup |
| T14 | Start each command-line version from another working directory | Correct demo login succeeds | Correct demo login succeeds |

For T10, browser field validation may prevent the request before submission; the automated test exercises the server-side response directly. T12 checks the local database through the regression suite. T14 is a command-line check.

## Local lab inputs

Use any nonempty demo password, such as `wrong`, with these usernames.

Authentication bypass:

```text
' OR '1'='1'--
```

Account-hash disclosure:

```text
' UNION SELECT username,password FROM users--
```

Rejected stacked statement:

```text
'; DROP TABLE users;--
```

## How to describe a finding

A useful report includes the affected phase, exact input, expected behavior, actual behavior, likely impact, root cause, and retest result.

Example: Phase 1 accepted a login using the bypass username and an incorrect password. The input changed the SQL query's condition. Phase 2 passes that same username through a bound parameter, so it searches for the literal value and returns no matching account.

Do not interpret the deliberate Phase 1 weakness as an unexpected regression. The test checks that the vulnerability is reproducible and that Phase 2 prevents the same behavior.
