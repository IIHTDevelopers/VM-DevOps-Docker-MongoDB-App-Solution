import unittest
from unittest.runner import TextTestResult, TextTestRunner
import os


class CustomTextTestResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed = 0

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed += 1


class CustomTestRunner(unittest.TextTestRunner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, resultclass=CustomTextTestResult, **kwargs)

    def run(self, test):
        result = super().run(test)
        total_tests = result.testsRun
        passed_tests = result.passed
        failed_tests = len(result.failures)
        skipped_tests = len(result.skipped)
        passed_percentage = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        summary = (
            f"\n{'=' * 50}\n"
            f"Test Execution Summary\n"
            f"{'=' * 50}\n"
            f"Total Tests Run     : {total_tests}\n"
            f"Passed Tests        : {passed_tests}\n"
            f"Failed Tests        : {failed_tests}\n"
            f"Skipped Tests       : {skipped_tests}\n"
            f"Pass Percentage     : {passed_percentage:.2f}%\n"
            f"{'=' * 50}\n"
        )
        print(summary)

        # Save percentage to a file
        try:
            file_path = os.path.join(os.getcwd(), "test_percentage.txt")
            with open(file_path, "w") as file:
                file.write(f"Pass Percentage: {passed_percentage:.2f}%\n")
            print(f"Pass percentage saved to {file_path}")
        except Exception as e:
            print(f"Error saving test percentage: {e}")

        return result


# Example Test Cases
class ExampleTestCase(unittest.TestCase):
    def test_pass1(self):
        """A passing test case."""
        self.assertTrue(True)

    def test_pass2(self):
        """Another passing test case."""
        self.assertEqual(1, 1)

    def test_fail(self):
        """A failing test case."""
        self.assertTrue(False)

    @unittest.skip("Skipping this test.")
    def test_skip(self):
        """A skipped test case."""
        pass


if __name__ == "__main__":
    # Run tests with the custom test runner
    unittest.main(testRunner=CustomTestRunner, verbosity=2)
