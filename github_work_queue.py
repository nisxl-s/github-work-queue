"""List open work in public GitHub repositories. Run with Python 3.9+."""

import argparse
import json
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

API = "https://api.github.com"


def list_items(path, **params):
    """Follow GitHub's pagination links until all results have been fetched."""
    url = f"{API}{path}?{urlencode(dict(per_page=100, **params))}"
    while url:
        request = Request(url, headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "github-work-queue",
        })
        with urlopen(request, timeout=15) as response:
            yield from json.load(response)
            next_page = re.search(r'<([^>]+)>;\s*rel="next"', response.headers.get("Link", ""))
        url = next_page.group(1) if next_page else None
        if url and not url.startswith(f"{API}/"):
            raise ValueError("GitHub returned an unexpected pagination URL.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("user", nargs="?", default="nisxl-s", help="GitHub username")
    args = parser.parse_args()

    try:
        repositories = list(list_items(f"/users/{quote(args.user, safe='')}/repos", type="owner"))
        for repo in sorted(repositories, key=lambda item: item["name"].casefold()):
            if repo["archived"] or not repo["open_issues_count"]:
                continue
            owner, name = (quote(part, safe="") for part in repo["full_name"].split("/"))
            work = list(list_items(f"/repos/{owner}/{name}/issues", state="open"))
            if not work:
                continue
            print(f"\n{repo['full_name']}")
            for item in work:
                kind = "PR" if "pull_request" in item else "Issue"
                print(f"  {kind} #{item['number']}  {item['title']}")
                print(f"    {item['html_url']}")
        print(f"\nChecked {len(repositories)} public repositories owned by {args.user}.")
    except HTTPError as error:
        if error.code in (403, 429) and (
            error.headers.get("X-RateLimit-Remaining") == "0"
            or error.headers.get("Retry-After")
        ):
            print("GitHub rate-limited this request. Try again later.", file=sys.stderr)
        else:
            print(f"GitHub returned HTTP {error.code}.", file=sys.stderr)
        return 1
    except (URLError, TimeoutError, ValueError) as error:
        print(f"Could not read GitHub data: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
