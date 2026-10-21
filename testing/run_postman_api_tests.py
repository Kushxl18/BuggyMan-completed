import os
import sys
import unittest
import json
import urllib.request
import urllib.error

API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000/api")
QA_EMAIL = "qa@buggyman.test"
QA_PASSWORD = "Password123!"


class BuggyManPostmanApiIntegrationTest(unittest.TestCase):
    """
    Phase 5: API Integration Testing (Postman Equivalent Automated Suite)
    Executes assertions against all backend endpoints used by the frontend.
    """

    @classmethod
    def setUpClass(cls):
        cls.auth_token = None
        cls.login_qa_user()

    @classmethod
    def login_qa_user(cls):
        url = f"{API_BASE_URL}/login"
        payload = json.dumps({"email": QA_EMAIL, "password": QA_PASSWORD}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            cls.auth_token = data.get("token")
            cls.user_data = data.get("user")

    def _auth_request(self, path, method="GET", body=None):
        url = f"{API_BASE_URL}{path}"
        headers = {"Authorization": f"Bearer {self.auth_token}", "Content-Type": "application/json"}
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        return req

    # 1. System Health
    def test_01_api_health_check(self):
        req = urllib.request.Request(f"{API_BASE_URL}/health")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "healthy")

    # 2. Authentication
    def test_02_login_invalid_password_returns_400_or_401(self):
        url = f"{API_BASE_URL}/login"
        payload = json.dumps({"email": QA_EMAIL, "password": "WrongPassword999!"}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertIn(ctx.exception.code, [400, 401])

    def test_03_check_availability_existing_user(self):
        url = f"{API_BASE_URL}/check-availability"
        payload = json.dumps({"username": "qa_automation_user"}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                self.assertFalse(data.get("available"))
        except urllib.error.HTTPError as err:
            self.assertEqual(err.code, 400)
            data = json.loads(err.read().decode("utf-8"))
            self.assertFalse(data.get("available"))
            self.assertIn("already taken", data.get("error", ""))

    # 3. User Profile & Career Insights
    def test_04_get_user_profile(self):
        req = self._auth_request("/profile")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("username"), "qa_automation_user")
            self.assertIn("totalScore", data)
            self.assertIn("bugbytesBalance", data)

    def test_05_get_career_insights(self):
        req = self._auth_request("/career-insights")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertIn("topMatch", data)
            self.assertIn("roles", data)
            self.assertTrue(len(data.get("roles", [])) > 0)
            self.assertIn("matchScore", data["topMatch"])

    # 4. Challenges & Recommendations
    def test_06_list_challenges_arena_code(self):
        req = self._auth_request("/challenges?arena=code")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertIsInstance(data, list)
            self.assertTrue(len(data) > 0)
            first = data[0]
            self.assertIn("id", first)
            self.assertIn("title", first)
            self.assertIn("difficulty", first)

    def test_07_get_personalized_recommendations(self):
        req = self._auth_request("/challenges/recommendations")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertIsInstance(data, list)

    # 5. PvP Multiplayer Endpoints
    def test_08_pvp_online_presence_stats(self):
        req = self._auth_request("/pvp/online-stats")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertIn("totalOnline", data)
            self.assertIn("waitingInQueue", data)

    def test_09_pvp_create_and_cancel_battle(self):
        # Create
        create_req = self._auth_request("/pvp/create", method="POST", body={"difficultyFilter": "Easy", "timeLimitSeconds": 600})
        with urllib.request.urlopen(create_req) as resp:
            self.assertIn(resp.status, [200, 201])
            battle = json.loads(resp.read().decode("utf-8"))
            room_code = battle.get("roomCode") or battle.get("room_code")
            battle_id = battle.get("id")
            self.assertIsNotNone(room_code)
            self.assertEqual(len(room_code), 6)

        # Cancel
        cancel_req = self._auth_request(f"/pvp/{battle_id}/cancel", method="POST")
        with urllib.request.urlopen(cancel_req) as resp:
            self.assertEqual(resp.status, 200)
            cancelled = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(cancelled.get("status"), "CANCELLED")

    # 6. BugBytes Store & Economy
    def test_10_store_packages_list(self):
        req = self._auth_request("/store/packages")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            packages = data.get("packages")
            self.assertIsInstance(packages, list)
            self.assertTrue(len(packages) > 0)

    # 7. Negative & Error Handling
    def test_11_unauthorized_request_rejected(self):
        req = urllib.request.Request(f"{API_BASE_URL}/profile")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertIn(ctx.exception.code, [401, 403])

    def test_12_nonexistent_challenge_returns_404(self):
        req = self._auth_request("/challenges/nonexistent_id_999999")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
