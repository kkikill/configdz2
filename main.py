import os
import sys
import subprocess
import tempfile
from datetime import datetime
import toml


def clone_repo(repo_url, temp_dir):
    subprocess.run(["git", "clone", repo_url, temp_dir], check=True)


def get_commit_history(repo_path, since_date):
    result = subprocess.run([
        "git", "log", f"--since={since_date}", "--pretty=format:%H|%ad|%an|%s", "--date=iso"
    ], cwd=repo_path, stdout=subprocess.PIPE, text=True)
    return result.stdout.splitlines()


def build_dependency_graph(commits):
    graph = ["graph TD"]

    for i, commit in enumerate(commits):
        commit_hash, commit_date, commit_author, commit_msg = commit.split("|", 3)
        node_label = (
            f"{commit_hash[:7]}[{commit_date}<br>{commit_author}<br>{commit_msg}]")
        graph.append(f"    {commit_hash[:7]}({node_label})")

        if i > 0:
            prev_commit_hash = commits[i - 1].split("|", 1)[0]
            graph.append(f"    {prev_commit_hash[:7]} --> {commit_hash[:7]}")

    return "\n".join(graph)


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <config-file-path>")
        sys.exit(1)

    config_path = sys.argv[1]

    try:
        config = toml.load(config_path)
    except Exception as e:
        print(f"Error reading config file: {e}")
        sys.exit(1)

    repo_path = config.get("repo_path")
    output_path = config.get("output_path")
    since_date = config.get("since_date")

    if not (repo_path and output_path and since_date):
        print("Invalid configuration. Ensure 'repo_path', 'output_path', and 'since_date' are specified.")
        sys.exit(1)

    if not os.path.isdir(repo_path):
        print(f"Invalid repository path: {repo_path}")
        sys.exit(1)

    try:
        print("Fetching commit history...")
        commits = get_commit_history(repo_path, since_date)

        if not commits:
            print("No commits found after the specified date.")
            sys.exit(0)

        print("Building dependency graph...")
        graph_code = build_dependency_graph(commits)

        print("Writing graph to output file...")
        with open(output_path, "w") as f:
            f.write(graph_code)

        print("Dependency graph written successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing Git command: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
