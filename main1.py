import pytest
import requests
import time
from pymongo import MongoClient

BASE_URL = "http://localhost:3000"

# TestUtils class for yaksha assertions
class TestUtils:
    def yakshaAssert(self, test_name, result, test_type):
        """
        Method to handle yaksha assertions
        """
        if result:
            print(f"{test_name} = Passed")
        else:
            print(f"{test_name} = Failed")
        return result

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


# Example test cases with yaksha assert structure
def test_login(wait_for_server):
    """
    Test the login functionality.
    """
    test_obj = TestUtils()
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "password123"})
        if response.status_code == 200 and response.json()["message"] == "Login successful":
            test_obj.yakshaAssert("TestLogin", True, "functional")
            print("TestLogin = Passed")
        else:
            test_obj.yakshaAssert("TestLogin", False, "functional")
            print("TestLogin = Failed")
    except Exception as e:
        test_obj.yakshaAssert("TestLogin", False, "functional")
        print(f"TestLogin = Failed: {str(e)}")


def test_create_poll(wait_for_server):
    """
    Test poll creation functionality.
    """
    test_obj = TestUtils()
    try:
        response = requests.post(f"{BASE_URL}/polls", json={"question": "Favorite color?", "options": ["Red", "Blue", "Green"]})
        if response.status_code == 201:
            global poll_id
            poll_id = response.json()["_id"]
            test_obj.yakshaAssert("TestCreatePoll", True, "functional")
            print("TestCreatePoll = Passed")
        else:
            test_obj.yakshaAssert("TestCreatePoll", False, "functional")
            print("TestCreatePoll = Failed")
    except Exception as e:
        test_obj.yakshaAssert("TestCreatePoll", False, "functional")
        print(f"TestCreatePoll = Failed: {str(e)}")


def test_get_polls(wait_for_server):
    """
    Test fetching the list of polls.
    """
    test_obj = TestUtils()
    try:
        response = requests.get(f"{BASE_URL}/polls")
        if response.status_code == 200 and len(response.json()) > 0:
            test_obj.yakshaAssert("TestGetPolls", True, "functional")
            print("TestGetPolls = Passed")
        else:
            test_obj.yakshaAssert("TestGetPolls", False, "functional")
            print("TestGetPolls = Failed")
    except Exception as e:
        test_obj.yakshaAssert("TestGetPolls", False, "functional")
        print(f"TestGetPolls = Failed: {str(e)}")


def test_vote_poll(wait_for_server):
    """
    Test voting functionality for a poll.
    """
    test_obj = TestUtils()
    try:
        response = requests.post(f"{BASE_URL}/polls/{poll_id}/vote", json={"option": "Red"})
        if response.status_code == 200 and any(opt["option"] == "Red" and opt["votes"] == 1 for opt in response.json()["options"]):
            test_obj.yakshaAssert("TestVotePoll", True, "functional")
            print("TestVotePoll = Passed")
        else:
            test_obj.yakshaAssert("TestVotePoll", False, "functional")
            print("TestVotePoll = Failed")
    except Exception as e:
        test_obj.yakshaAssert("TestVotePoll", False, "functional")
        print(f"TestVotePoll = Failed: {str(e)}")


def test_node_service_on_3000():
    """
    Verify that Node.js service is running and accessible on port 3000.
    """
    test_obj = TestUtils()
    try:
        url = "http://localhost:3000"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            test_obj.yakshaAssert("TestNodeService", True, "functional")
            print("TestNodeService = Passed")
        else:
            test_obj.yakshaAssert("TestNodeService", False, "functional")
            print(f"TestNodeService = Failed: Node.js service on port 3000 returned {response.status_code}")
    except requests.exceptions.ConnectionError:
        test_obj.yakshaAssert("TestNodeService", False, "functional")
        print("TestNodeService = Failed: Node.js service on port 3000 is not reachable")


def test_mongodb_on_27017():
    """
    Verify that MongoDB is running and accepting connections on port 27017.
    """
    test_obj = TestUtils()
    try:
        client = MongoClient("localhost", 27017, serverSelectionTimeoutMS=5000)
        client.server_info()  # Ping the MongoDB server
        test_obj.yakshaAssert("TestMongoDB", True, "functional")
        print("TestMongoDB = Passed")
    except Exception as e:
        test_obj.yakshaAssert("TestMongoDB", False, "functional")
        print(f"TestMongoDB = Failed: MongoDB on port 27017 is not reachable: {e}")
