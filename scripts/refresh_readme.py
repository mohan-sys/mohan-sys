#!/usr/bin/env python3
"""Rewrite the auto-generated blocks in README.md from the GitHub API.

Blocks are delimited by HTML comments:
  <!-- recent:start --> ... <!-- recent:end -->      latest pushed public repos
  <!-- updated:start --> ... <!-- updated:end -->    last refresh date

Run locally with `python3 scripts/refresh_readme.py` or via the weekly workflow.
Set GITHUB_TOKEN to avoid the anonymous rate limit.
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER = os.environ.get("GH_USER", "mohan-sys")
README = Path(__file__).resolve().parent.parent / "README.md"
LIMIT = 5

# Repos that shouldn't show up in "recent": the profile repo, the two featured as
# cards above, and coursework. Forks and repos with no description are skipped too.
SKIP = {USER, "multi-tenant-saas", "incident-platform", "junit-in-5-steps", "learn-spring-aop", "learn-jpa-and-hibernate",
        "Practising-java-springboot", "restful-web-services"}

# Nicer names / one-liners for repos without a GitHub description.
OVERRIDES = {
    "multi-tenant-saas": ("PulseAPI", "Multi-tenant API platform on ECS Fargate, Terraform-managed"),
    "incident-platform": ("Incident Platform", "Serverless on-call paging with tiered escalation"),
    "personal_3D_portfolio": ("3D Portfolio", "Interactive portfolio in React Three Fiber and GSAP"),
    "storypoints-data-pipeline": ("ETL Pipeline", "Chunked extract, clean and partitioned load to GCS"),
    "mohans_crossword": ("Crossword", "Playable crossword in the browser, built with React"),
    "spotify_popularity_pred": ("Song Popularity Model", "Predicts how popular a track will be from Spotify data"),
    "spotify_genre_pred": ("Genre Classifier", "Classifies a track's genre from Spotify data"),
    "Voting-System-Blockchain-Ethereum": ("On-chain Voting", "Ethereum voting contract written in Solidity"),
}


def api(path):
    req = urllib.request.Request(f"https://api.github.com{path}",
                                 headers={"Accept": "application/vnd.github+json",
                                          "User-Agent": "profile-readme-refresh"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def recent_rows():
    repos = api(f"/users/{USER}/repos?per_page=100&sort=pushed&type=owner")
    rows = []
    for r in repos:
        if r["fork"] or r["archived"] or r["private"] or r["name"] in SKIP:
            continue
        name, blurb = OVERRIDES.get(r["name"], (r["name"], r["description"] or ""))
        if not blurb:
            continue
        lang = r["language"] or "—"
        if lang == "Jupyter Notebook":
            lang = "Python"
        pushed = datetime.fromisoformat(r["pushed_at"].replace("Z", "+00:00")).strftime("%b %Y")
        rows.append(f"| [**{name}**]({r['html_url']}) | {blurb} | `{lang}` | {pushed} |")
        if len(rows) == LIMIT:
            break
    head = "| Project | What it is | Stack | Last push |\n|:--|:--|:--|--:|"
    return head + "\n" + "\n".join(rows)


def replace_block(text, tag, body):
    pattern = re.compile(rf"(<!-- {tag}:start -->)(.*?)(<!-- {tag}:end -->)", re.S)
    if not pattern.search(text):
        sys.exit(f"marker '{tag}' not found in README.md")
    return pattern.sub(lambda m: f"{m.group(1)}\n{body}\n{m.group(3)}", text)


def main():
    text = README.read_text()
    new = replace_block(text, "recent", recent_rows())
    if new != text:
        stamp = datetime.now(timezone.utc).strftime("%d %b %Y")
        new = replace_block(new, "updated", f"<sub>Runs on coffee &nbsp;·&nbsp; synced from the GitHub API {stamp}</sub>")
        README.write_text(new)
        print("README updated")
    else:
        print("no changes")


if __name__ == "__main__":
    main()
