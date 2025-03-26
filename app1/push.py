import os
import subprocess
import sys
import unittest
import requests
import time
from pymongo import MongoClient
from datetime import datetime

def run_command(command):
    """Run a shell command and print its output."""
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        sys.exit(1)

def push_to_repository():
    """Push project to a private repository."""
    repo_url = "https://github.com/iihtmahesh/node.git"
    print(f"Using repository URL: {repo_url}")

    # Create a unique branch name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    branch_name = f"branch_{timestamp}"
    print(f"Creating or switching to branch: {branch_name}")

    # Initialize Git repository if not already done
    if not os.path.exists(".git"):
        print("Initializing a new Git repository...")
        run_command(["git", "init"])

    # Add all changes
    print("Adding files to the repository...")
    run_command(["git", "add", "."])

    # Commit changes
    commit_message = f"Auto commit on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    print(f"Committing changes with message: {commit_message}")
    run_command(["git", "commit", "-m", commit_message])

    # Create or switch to the branch locally
    try:
        run_command(["git", "checkout", "-b", branch_name])
    except subprocess.CalledProcessError:
        print(f"Branch {branch_name} already exists. Switching to it.")
        run_command(["git", "checkout", branch_name])

    # Push directly to the remote URL
    try:
        print(f"Pushing changes to branch: {branch_name} at {repo_url}")
        run_command(["git", "push", "-u", repo_url, branch_name])
    except subprocess.CalledProcessError as e:
        print("Failed to push changes. Please check your credentials or repository settings.")
        print(f"Error details: {e.stderr}")
        sys.exit(1)

    print(f"Project successfully pushed to {repo_url} on branch {branch_name}!")

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
        time.sleep(10)

    @classmethod
    def tearDownClass(cls):
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

        print("\n" + "=" * 50)
        print("Summary of Test Results")
        print("=" * 50)
        print(summary)
        print("=" * 50 + "\n")

        with open("test_results.txt", "w") as file:
            file.write("Test Results Summary\n")
            file.write("=" * 50 + "\n")
            file.write(summary)

    def record_outcome(self, outcome):
        if outcome == "passed":
            test_outcomes["passed"] += 1
        elif outcome == "failed":
            test_outcomes["failed"] += 1
        elif outcome == "skipped":
            test_outcomes["skipped"] += 1

    def test_login(self):
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "password123"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["message"], "Login successful")
            self.record_outcome("passed")
        except Exception as e:
            self.record_outcome("failed")
            raise e

    def test_create_poll(self):
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
        try:
            response = requests.get(f"{BASE_URL}/polls")
            self.assertEqual(response.status_code, 200)
            self.assertGreater(len(response.json()), 0)
            self.record_outcome("passed")
        except Exception as e:
            self.record_outcome("failed")
            raise e

    def test_vote_poll(self):
        try:
            response = requests.post(f"{BASE_URL}/polls/{poll_id}/vote", json={"option": "Red"})
            self.assertEqual(response.status_code, 200)
            self.assertTrue(any(opt["option"] == "Red" and opt["votes"] == 1 for opt in response.json()["options"]))
            self.record_outcome("passed")
        except Exception as e:
            self.record_outcome("failed")
            raise e

    def test_node_service_on_3000(self):
        url = "http://localhost:3000"
        try:
            response = requests.get(url, timeout=5)
            self.assertEqual(response.status_code, 200)
            print(f"Node.js service is accessible on port 3000 with response: {response.text}")
            self.record_outcome("passed")
        except requests.exceptions.ConnectionError:
            self.record_outcome("failed")
            self.fail("Node.js service on port 3000 is not reachable")

    def test_mongodb_on_27017(self):
        try:
            client = MongoClient("localhost", 27017, serverSelectionTimeoutMS=5000)
            client.server_info()
            print("MongoDB is running and accessible on port 27017")
            self.record_outcome("passed")
        except Exception as e:
            self.record_outcome("failed")
            self.fail(f"MongoDB on port 27017 is not reachable: {e}")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Run Tests")
    print("2. Push to Repository")
    choice = input("Enter your choice (1/2): ")

    if choice == "1":
        unittest.main()
    elif choice == "2":
        push_to_repository()
    else:
        print("Invalid choice. Exiting.")
