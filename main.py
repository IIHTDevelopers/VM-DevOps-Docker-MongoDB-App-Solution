import pytest
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


@pytest.fixture(scope="module")
def wait_for_server():
    """
    Fixture to wait for containers to start.
    """
    time.sleep(10)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_logreport(report):
    """
    Capture test results during execution.
    """
    outcome = yield
    result = outcome.get_result()

    if result.when == "call":  # Only consider the test function (not setup/teardown)
        if result.outcome == "passed":
            test_outcomes["passed"] += 1
        elif result.outcome == "failed":
            test_outcomes["failed"] += 1
        elif result.outcome == "skipped":
            test_outcomes["skipped"] += 1


def pytest_sessionfinish(session, exitstatus):
    """
    Calculate and save test result summary to a file.
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


# Example test cases
def test_login(wait_for_server):
    """
    Test the login functionality.
    """
    response = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "password123"})
    assert response.status_code == 200
    assert response.json()["message"] == "Login successful"


def test_create_poll(wait_for_server):
    """
    Test poll creation functionality.
    """
    response = requests.post(f"{BASE_URL}/polls", json={"question": "Favorite color?", "options": ["Red", "Blue", "Green"]})
    assert response.status_code == 201
    global poll_id
    poll_id = response.json()["_id"]


def test_get_polls(wait_for_server):
    """
    Test fetching the list of polls.
    """
    response = requests.get(f"{BASE_URL}/polls")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_vote_poll(wait_for_server):
    """
    Test voting functionality for a poll.
    """
    response = requests.post(f"{BASE_URL}/polls/{poll_id}/vote", json={"option": "Red"})
    assert response.status_code == 200
    assert any(opt["option"] == "Red" and opt["votes"] == 1 for opt in response.json()["options"])


def test_node_service_on_3000():
    """
    Verify that Node.js service is running and accessible on port 3000.
    """
    url = "http://localhost:3000"
    try:
        response = requests.get(url, timeout=5)
        assert response.status_code == 200, f"Node.js service on port 3000 returned {response.status_code}"
        print(f"Node.js service is accessible on port 3000 with response: {response.text}")
    except requests.exceptions.ConnectionError:
        pytest.fail("Node.js service on port 3000 is not reachable")


def test_mongodb_on_27017():
    """
    Verify that MongoDB is running and accepting connections on port 27017.
    """
    try:
        client = MongoClient("localhost", 27017, serverSelectionTimeoutMS=5000)
        client.server_info()  # Ping the MongoDB server
        print("MongoDB is running and accessible on port 27017")
    except Exception as e:
        pytest.fail(f"MongoDB on port 27017 is not reachable: {e}")
