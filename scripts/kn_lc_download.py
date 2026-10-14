#!/usr/bin/env python3
"""Download every PDF listed in ../_raw/kn/inventory.json (written by
kn_lc_crawl.py) to ../_raw/kn/pdf/<folder>/<name>, skipping the *TOC folders
(byte-identical duplicates of the revised-edition folders) and the order form.
Already-complete PDFs are not re-downloaded."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kn_http import RAW, cached_pdf  # noqa: E402

SKIP_FOLDERS = {"Act02and09TOC", "Act17TOC", "Ord02and09TOC", "Ord17TOC", "Publications"}


def local_path(f):
    return os.path.join(RAW, "pdf", f["folder"], f["name"])


def wanted(inv):
    return [f for f in inv if f["folder"] not in SKIP_FOLDERS]


def main():
    inv = wanted(json.load(open(os.path.join(RAW, "inventory.json"))))
    bad = []
    for i, f in enumerate(inv):
        ok = cached_pdf(f["url"], local_path(f))
        if not ok:
            bad.append(f["url"])
        if i % 25 == 0:
            print(i, len(inv), f["name"], flush=True)
    json.dump(bad, open(os.path.join(RAW, "download_failed.json"), "w"), indent=1)
    print("done; failed:", len(bad))


if __name__ == "__main__":
    main()
