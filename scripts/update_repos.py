"""Regenerate the public repositories table in README.md.

Lists the user's public repositories via the GitHub API, sorts them by
creation date (newest first) and replaces the block between the
REPOS:START and REPOS:END markers. Standard library only.
"""

import json
import os
import re
import urllib.request
from pathlib import Path

USER = "fmcoskun"
README = Path("README.md")
START = "<!-- REPOS:START -->"
END = "<!-- REPOS:END -->"


def fetch_repos():
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "profile-readme-updater",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    repos, page = [], 1
    while True:
        url = (
            f"https://api.github.com/users/{USER}/repos"
            f"?per_page=100&type=owner&page={page}"
        )
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            batch = json.load(response)
        repos.extend(batch)
        if len(batch) < 100:
            return repos
        page += 1


def build_section(repos):
    repos = sorted(repos, key=lambda r: r["created_at"], reverse=True)
    lines = [
        START,
        "",
        "## 📦 Public Repositories",
        "",
        "Sorted by creation date, newest first (oluşturulma tarihine göre, en yeniden en eskiye).",
        "",
        "| Created | Repository |",
        "|---|---|",
    ]
    for repo in repos:
        lines.append(
            f"| {repo['created_at'][:10]} | [{repo['name']}]({repo['html_url']}) |"
        )
    lines += ["", END]
    return "\n".join(lines)


def main():
    text = README.read_text(encoding="utf-8").replace("\r\n", "\n")
    repos = fetch_repos()
    if not repos:
        raise SystemExit("No repositories returned; leaving README unchanged.")

    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        raise SystemExit("REPOS markers not found in README.md.")

    section = build_section(repos)
    updated = pattern.sub(lambda _: section, text, count=1)
    if updated != text:
        README.write_text(updated, encoding="utf-8", newline="\n")
        print(f"README.md updated with {len(repos)} repositories.")
    else:
        print("README.md already up to date.")


if __name__ == "__main__":
    main()
