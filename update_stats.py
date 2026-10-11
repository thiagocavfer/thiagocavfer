#!/usr/bin/env python3
"""Refresh public GitHub stats in Andrew-inspired SVGs using GitHub REST API."""
import json, os, re, urllib.request
from pathlib import Path
from xml.etree import ElementTree as ET

USER = "thiagocavfer"
BASE = Path(__file__).resolve().parent
TOKEN = os.environ.get("GH_TOKEN", "")
headers = {"Accept": "application/vnd.github+json", "User-Agent": "github-profile-readme"}
if TOKEN:
    headers["Authorization"] = "Bearer " + TOKEN

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=20) as res:
        return json.load(res)

def main():
    user = get(f"https://api.github.com/users/{USER}")
    repos = []
    page = 1
    while True:
        batch = get(f"https://api.github.com/users/{USER}/repos?type=owner&per_page=100&page={page}")
        repos += batch
        if len(batch) < 100: break
        page += 1
    stars = sum(r.get("stargazers_count",0) for r in repos if not r.get("fork"))
    vals = {"repos": user.get("public_repos", 0), "followers": user.get("followers", 0), "stars": stars}
    for file in (BASE/"dark_mode.svg", BASE/"light_mode.svg"):
        tree = ET.parse(file)
        root = tree.getroot()
        ns = {"svg": "http://www.w3.org/2000/svg"}
        for k,v in vals.items():
            el = root.find(f".//*[@id='{k}']")
            if el is not None:
                el.text = k.capitalize() + ": " + str(v)
        ET.register_namespace("", "http://www.w3.org/2000/svg")
        tree.write(file, encoding="unicode", xml_declaration=True)
    print(vals)

if __name__ == "__main__": main()
