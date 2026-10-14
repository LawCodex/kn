#!/usr/bin/env python3
"""Walk the Law Commission file library (https://lawcommission.gov.kn/laws/,
a "Simple File List" WordPress plugin) and write an inventory of every file
to ../_raw/kn/inventory.json: [{folder, name, url, size, added, changed}].

Usage: kn_lc_crawl.py [root-folder ...]   (default: the whole library)
"""
import json
import os
import re
import sys
import urllib.parse

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kn_http import RAW, cached_text  # noqa: E402

BASE = "https://lawcommission.gov.kn/laws/"


def listing_url(folder, page=None):
    q = "?ee=1&eeListID=1"
    if folder:
        q += "&eeFolder=" + urllib.parse.quote(folder, safe="")
    if page is not None:
        q += "&eePage=%d" % page
    return BASE + q


def parse(html):
    soup = BeautifulSoup(html, "lxml")
    files, dirs, pages = [], [], set()
    for tr in soup.select("tr.eeSFL_Item"):
        def sp(cls):
            e = tr.select_one("span." + cls)
            return e.get_text(strip=True) if e else ""
        a = tr.select_one("a.eeSFL_FileName")
        if not a:
            continue
        if sp("eeSFL_FileMimeType") == "directory":
            q = urllib.parse.parse_qs(urllib.parse.urlparse(a["href"]).query)
            dirs.append(q["eeFolder"][0])
        else:
            files.append({"name": sp("eeSFL_RealFileName"), "url": a["href"],
                          "size": sp("eeSFL_FileSize"), "added": sp("eeSFL_FileDateAdded"),
                          "changed": sp("eeSFL_FileDateChanged")})
    for a in soup.find_all("a", href=True):
        m = re.search(r"eePage=(\d+)", a["href"])
        if m:
            pages.add(int(m.group(1)))
    return files, dirs, pages


def crawl(roots):
    inv, seen = [], set()
    todo = list(roots)
    while todo:
        folder = todo.pop(0)
        if folder in seen:
            continue
        seen.add(folder)
        html = cached_text(listing_url(folder), "listings")
        files, dirs, pages = parse(html)
        # eePage is 0-based; the default listing is page 0
        for p in sorted(pages - {0}):
            f2, d2, _ = parse(cached_text(listing_url(folder, p), "listings"))
            files += f2
            dirs += d2
        uniq = {f["url"]: f for f in files}
        print("%-90s %4d files %3d dirs %d pages" % (folder or "/", len(uniq), len(set(dirs)), len(pages)))
        for f in uniq.values():
            f["folder"] = folder
            inv.append(f)
        todo += [d for d in dict.fromkeys(dirs) if d not in seen]
    return inv


def main():
    roots = sys.argv[1:] or [""]
    inv = crawl(roots)
    dedup = list({f["url"]: f for f in inv}.values())
    json.dump(dedup, open(os.path.join(RAW, "inventory.json"), "w"), indent=1)
    print(len(dedup), "files")


if __name__ == "__main__":
    main()
