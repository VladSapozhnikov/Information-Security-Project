# Maintenance Notes

## Original defects reproduced

The original code was inspected at commit `5c9d914b58958c78aad4a2260b77958f1eb399f1`. Checks used temporary databases populated with the code's synthetic accounts; the committed database contents were not inspected.

| Finding | Reproduction | Observed result |
| --- | --- | --- |
| Phase 1 rejects a correct password | Initialize fresh accounts; POST alice / alicepass to the original web login | HTTP 200 with Login failed |
| Phase 2 command-line startup crashes | Call the original phase2.py init_db | NameError: encrypt_pw is not defined |
| Duplicate protected registration crashes | Register alice when alice already exists | HTTP 500 |

Phase 1 encrypted the supplied password again with a fresh random IV and compared the resulting ciphertext with the stored ciphertext. Those ciphertexts differed even when the passwords matched. The protected web version's ordinary login and SQL injection rejection worked in the original checks.

## Repairs

- Phase 1 uses a deterministic SHA-256 digest for its deliberately weak password-storage example, so legitimate logins work. The hard-coded AES key and random-ciphertext comparison are removed.
- Phase 2 stores salted scrypt hashes and verifies them using Werkzeug. It looks up the account using a parameterized username query, then checks the supplied password against the stored hash.
- Each web interface shares its phase's database functions with the command-line interface, avoiding diverging login logic.
- Database paths are relative to their Python modules. Generated databases have new names, so the maintained version does not reinterpret legacy AES or SHA-256 records.
- Duplicate registrations, malformed SQL in the vulnerable phase, missing fields, and excessively long inputs have controlled responses.
- Reflected username and database text is HTML-escaped.
- Both web entry points bind to 127.0.0.1 with debug mode disabled.
- The special-case executescript path for DROP TABLE is removed. The comparison focuses on authentication bypass and account-hash disclosure with single SQL statements.
- Dependency versions, setup steps, a manual test plan, and 13 behavioral regression tests are included.

The intentionally vulnerable phase remains suitable only for a local learning exercise. The protected phase demonstrates the listed controls but is not a complete production authentication service.

## Retest

All 13 regression test methods passed under Python 3.12 on Linux using Flask 3.1.3 and Werkzeug 3.1.8. This includes repeat legitimate login, registration, incorrect passwords, SQL injection behavior in both phases, duplicate handling, escaped output, distinct salted hashes, and both command-line launchers.

No graphical browser session, Windows execution, or production deployment was part of this verification.
