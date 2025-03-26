import os
import subprocess
import sys
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


def main():
    """Main function to push project to a private repository."""
    # Default repository URL
    repo_url = "https://github.com/iihtmahesh/node.git"
    print(f"Using default repository URL: {repo_url}")

    # Generate a unique branch name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    branch_name = f"branch_{timestamp}"
    print(f"Creating a new branch: {branch_name}")

    # Initialize git repository if not already done
    if not os.path.exists(".git"):
        print("Initializing a new git repository...")
        run_command(["git", "init"])

    # Add all files to the repository
    print("Adding files to the repository...")
    run_command(["git", "add", "."])

    # Commit changes
    commit_message = f"Auto commit on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    print(f"Committing changes with message: {commit_message}")
    run_command(["git", "commit", "-m", commit_message])

    # Check and update remote origin if necessary
    try:
        existing_remote = run_command(["git", "remote", "get-url", "origin"]).strip()
        if existing_remote != repo_url:
            print(f"Updating remote origin from {existing_remote} to {repo_url}...")
            run_command(["git", "remote", "set-url", "origin", repo_url])
    except subprocess.CalledProcessError:
        print(f"Adding remote repository: {repo_url}")
        run_command(["git", "remote", "add", "origin", repo_url])

    # Create and switch to the new branch
    try:
        print(f"Creating and switching to branch: {branch_name}")
        run_command(["git", "checkout", "-b", branch_name])
    except subprocess.CalledProcessError as e:
        print(f"Failed to create or switch to branch: {branch_name}.")
        print(f"Detailed error: {e.stderr}")
        sys.exit(1)

    # Push to the private repository
    try:
        print(f"Pushing to branch: {branch_name}")
        run_command(["git", "push", "-u", "origin", branch_name])
    except subprocess.CalledProcessError as e:
        print("Failed to push changes. Please check your credentials and branch settings.")
        print(f"Detailed error: {e.stderr}")
        sys.exit(1)

    print(f"Project successfully pushed to the private repository on branch {branch_name}!")


if __name__ == "__main__":
    main()
