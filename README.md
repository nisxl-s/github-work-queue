# github-work-queue
A Python CLI that lists open issues and pull requests across public GitHub repositories.


## Usage

Run with Python 3.9 or later. No dependencies or GitHub token are required.

```sh
python github_work_queue.py
python github_work_queue.py octocat
```

The CLI reads the GitHub REST API and groups open issues and pull requests by public repository. It defaults to `nisxl-s`, skips archived repositories, and makes no changes to GitHub data.
