"""Behavior checks for both halves of the local SQL injection lab."""
from contextlib import closing
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from phase1 import phase1 as vulnerable
from phase1.phase1_web import app as vulnerable_app
from phase2 import phase2 as protected
from phase2.phase2_web import app as protected_app


class DemoTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.original_paths = vulnerable.DB, protected.DB
        self.addCleanup(self.restore_paths)
        vulnerable.DB = Path(self.temp.name) / "vulnerable.sqlite3"
        protected.DB = Path(self.temp.name) / "protected.sqlite3"
        vulnerable.init_db()
        protected.init_db()
        self.clients = [vulnerable_app.test_client(), protected_app.test_client()]

    def restore_paths(self):
        vulnerable.DB, protected.DB = self.original_paths

    def post(self, client, route="/login", username="alice", password="alicepass"):
        return client.post(route, data={"username": username, "password": password})

    def test_pages_load(self):
        for client in self.clients:
            for route in ["/", "/register", "/login"]:
                self.assertEqual(client.get(route).status_code, 200)

    def test_valid_logins(self):
        for client in self.clients:
            for _ in range(2):
                self.assertIn("Login successful!", self.post(client).text)

    def test_wrong_password_and_unknown_user(self):
        for client in self.clients:
            self.assertIn("Login failed.", self.post(client, password="wrong").text)
            self.assertIn("Login failed.", self.post(client, username="nobody").text)

    def test_registered_users_can_log_in(self):
        for client in self.clients:
            self.assertEqual(self.post(client, "/register", "charlie", "demo-pass").status_code, 201)
            self.assertIn("Login successful!", self.post(client, username="charlie", password="demo-pass").text)

    def test_authentication_bypass_is_only_in_vulnerable_phase(self):
        payload = "' OR '1'='1'--"
        self.assertIn("Login successful!", self.post(self.clients[0], username=payload, password="wrong").text)
        self.assertIn("Login failed.", self.post(self.clients[1], username=payload, password="wrong").text)
        self.assertFalse(protected.authenticate(payload, "wrong"))

    def test_union_disclosure_is_only_in_vulnerable_phase(self):
        payload = "' UNION SELECT username,password FROM users--"
        self.assertIn("alice:", self.post(self.clients[0], username=payload, password="wrong").text)
        self.assertNotIn("alice:", self.post(self.clients[1], username=payload, password="wrong").text)
        self.assertFalse(protected.authenticate(payload, "wrong"))

    def test_stacked_queries_do_not_remove_tables(self):
        payload = "'; DROP TABLE users;--"
        self.assertEqual(self.post(self.clients[0], username=payload).status_code, 400)
        self.assertIn("Login failed.", self.post(self.clients[1], username=payload).text)
        for module in [vulnerable, protected]:
            with closing(sqlite3.connect(module.DB)) as conn:
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM users").fetchone()[0], 2)

    def test_duplicate_registration_is_handled(self):
        for client in self.clients:
            self.assertEqual(self.post(client, "/register").status_code, 409)
            self.assertIn("Login successful!", self.post(client).text)

    def test_missing_and_oversized_fields_are_handled(self):
        for client in self.clients:
            for route in ["/register", "/login"]:
                self.assertEqual(client.post(route, data={}).status_code, 400)
                self.assertEqual(self.post(client, route, password="x" * 1025).status_code, 400)
                self.assertEqual(self.post(client, route, username="x" * 201).status_code, 400)

    def test_protected_registration_validates_username(self):
        for username in ["ab", "with space", "x" * 21, "' OR 1=1--"]:
            self.assertEqual(self.post(self.clients[1], "/register", username).status_code, 400)

    def test_protected_passwords_use_distinct_salted_hashes(self):
        protected.register_user("charlie", "shared-demo-password")
        protected.register_user("dana", "shared-demo-password")
        with closing(sqlite3.connect(protected.DB)) as conn:
            hashes = [row[0] for row in conn.execute("SELECT password FROM users WHERE username IN ('charlie','dana')")]
        self.assertEqual(len(hashes), 2)
        self.assertNotEqual(hashes[0], hashes[1])
        self.assertTrue(all(value.startswith("scrypt:") for value in hashes))
        self.assertTrue(protected.authenticate("charlie", "shared-demo-password"))
        self.assertFalse(protected.authenticate("charlie", "wrong"))

    def test_reflected_markup_is_escaped(self):
        response = self.post(self.clients[0], "/register", "<b>demo</b>", "demo")
        self.assertEqual(response.status_code, 201)
        self.assertIn("&lt;b&gt;demo&lt;/b&gt;", response.text)
        self.assertNotIn("<b>demo</b>", response.text)

    def test_cli_launches_from_another_directory(self):
        for module in [vulnerable, protected]:
            folder = Path(self.temp.name) / module.__name__.replace(".", "_")
            folder.mkdir()
            script = folder / "demo.py"
            shutil.copyfile(module.__file__, script)
            result = subprocess.run(
                [sys.executable, str(script)], cwd=self.temp.name,
                input="L\nalice\nalicepass\n", text=True, capture_output=True, timeout=10,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Login successful!", result.stdout)


if __name__ == "__main__":
    unittest.main()
