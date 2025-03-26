import unittest
import requests
import time
from pymongo import MongoClient

BASE_URL = "http://localhost:3000"

# Dictionary to store test outcomes
test_outcomes = {
    "passed": 0,
    "failed": 0,
    "skipped": 0,
}


class TestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Wait for containers to start before running tests.
        """
        time.sleep(10)

    @classmethod
    def tearDownClass(cls):
        """
        Calculate and save test result summary to a file after tests are run.
        """
        total_tests = sum(test_outcomes.values())
        passed_tests = test_outcomes["passed"]
        failed_tests = test_outcomes["failed"]
        skipped_tests = test_outcomes["skipped"]
        passed_percentage = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        summary = (
            f"Total Tests Run     : {total_tests}\n"
            f"Passed Tests        : {passed_tests}\n"
            f"Failed Tests        : {failed_tests}\n"
            f"Skipped Tests       : {skipped_tests}\n"
            f"Pass Percentage     : {passed_percentage:.2f}%\n"
        )

        # Print summary to console
        print("\n" + "=" * 50)
        print("Summary of Test Results")
        print("=" * 50)
        print(summary)
        print("=" * 50 + "\n")

        # Save summary to a file
        with open("test_results.txt", "w") as file:
            file.write("Test Results Summary\n")
            file.write("=" * 50 + "\n")
            file.write(summary)

    def record_outcome(self, outcome):
        """
        Record the outcome of a test.
        """
        if outcome == "passed":
            test_outcomes["passed"] += 1
        elif outcome == "failed":
            test_outcomes["failed"] += 1
        elif outcome == "skipped":
            test_outcomes["skipped"] += 1

    def test_login(self):
        """
        Test the login functionality.
        """
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "password123"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["message"], "Login successful")
            self.record_outcome("passed")
        except Exception as e:
            self.record_outcome("failed")
            raise e

    def test_create_poll(self):
        """
        Test poll creation functionality.
        """
        global poll_id
        try:
            response = requests.post(f"{BASE_URL}/polls", json={"question": "Favorite color?", "options": ["Red", "Blue", "Green"]})
            self.assertEqual(response.status_code, 201)
            poll_id = response.json()["_id"]
            self.record_outcome("passed")
        except Exception as e:
            self.record_outcome("failed")
            raise e

    def test_get_polls(self):
        """
        Test fetching the list of polls.
        """
        try:
            response = requests.get(f"{BASE_URL}/polls")
            self.assertEqual(response.status_code, 200)
            self.assertGreater(len(response.json()), 0)
            self.record_outcome("passed")
        except Exception as e:
            self.record_outcome("failed")
            raise e

    def test_vote_poll(self):
        """
        Test voting functionality for a poll.
        """
        try:
            response = requests.post(f"{BASE_URL}/polls/{poll_id}/vote", json={"option": "Red"})
            self.assertEqual(response.status_code, 200)
            self.assertTrue(any(opt["option"] == "Red" and opt["votes"] == 1 for opt in response.json()["options"]))
            self.record_outcome("passed")
        except Exception as e:
            self.record_outcome("failed")
            raise e

    def test_node_service_on_3000(self):
        """
        Verify that Node.js service is running and accessible on port 3000.
        """
        url = "http://localhost:3000"
        try:
            response = requests.get(url, timeout=5)
            self.assertEqual(response.status_code, 200, f"Node.js service on port 3000 returned {response.status_code}")
            print(f"Node.js service is accessible on port 3000 with response: {response.text}")
            self.record_outcome("passed")
        except requests.exceptions.ConnectionError:
            self.record_outcome("failed")
            self.fail("Node.js service on port 3000 is not reachable")

    def test_mongodb_on_27017(self):
        """
        Verify that MongoDB is running and accepting connections on port 27017.
        """
        try:
            client = MongoClient("localhost", 27017, serverSelectionTimeoutMS=5000)
            client.server_info()  # Ping the MongoDB server
            print("MongoDB is running and accessible on port 27017")
            self.record_outcome("passed")
        except Exception as e:
            self.record_outcome("failed")
            self.fail(f"MongoDB on port 27017 is not reachable: {e}")


if __name__ == "__main__":
    unittest.main()
