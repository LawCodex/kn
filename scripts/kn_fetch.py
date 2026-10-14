#!/usr/bin/env python3
"""Refresh the whole Saint Kitts and Nevis corpus.

  1. kn_lc_crawl.py     walk the Law Commission file library -> _raw/kn/inventory.json
  2. kn_lc_download.py  download the PDFs (cached in _raw/kn/pdf/)
  3. kn_lc_build.py     convert them to Markdown
  4. this file          add the few texts that only the Nevis Island
                        Administration (nia.gov.kn) publishes

Usage: kn_fetch.py            (all steps)
       kn_fetch.py --nia-only (step 4 only)
"""
import datetime
import json
import os
import sys
import time

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kn_pdf2md  # noqa: E402
from kn_http import pdf_ok  # noqa: E402

from kn_http import RAW, UA  # noqa: E402
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
BASE = "https://nia.gov.kn/cdl_document/"
TODAY = datetime.date.today().isoformat()

# Texts not available from the Law Commission. Everything else that nia.gov.kn
# offers (revised Caps, Acts of 2010-2011, Nevis Ordinances) is superseded by the
# Law Commission revised editions.
# (slug on nia.gov.kn, output path, title, type, identifier, date)
DOCS = [
    ("the-constitution-of-st-christopher-and-nevis", "constitution/saint-christopher-and-nevis-constitution-order-1983.md",
     "The Saint Christopher and Nevis Constitution Order 1983", "constitution", "S.I. 1983 No. 881", "1983-06-22"),
    ("the-nevis-international-insurance-ordinance-2006",
     "nevis-annual-ordinances/2006/ordinance-2006-001-nevis-international-insurance-amendment-ordinance-2006.md",
     "Nevis International Insurance (Amendment) Ordinance, 2006", "ordinance", "Nevis Ordinance No. 1 of 2006", ""),
    ("the-nevis-international-mutual-funds-ordinance-2007",
     "nevis-annual-ordinances/2007/ordinance-2007-nevis-international-mutual-funds-miscellaneous-amendments-ordinance-2007.md",
     "Nevis International Mutual Funds (Miscellaneous Amendments) Ordinance, 2007", "ordinance", "", ""),
]


def yq(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main():
    os.makedirs(os.path.join(RAW, "pdf", "nia"), exist_ok=True)
    s = requests.Session()
    s.headers["User-Agent"] = UA
    gaps = []
    for slug, rel, title, typ, ident, date in DOCS:
        p = os.path.join(RAW, "pdf", "nia", slug[:100] + ".pdf")
        if not pdf_ok(p):
            for i in range(4):
                try:
                    r = s.get(BASE + slug + "/", timeout=300)
                    if r.content[:5] == b"%PDF-":
                        open(p, "wb").write(r.content)
                    if pdf_ok(p):
                        break
                except requests.RequestException as e:
                    print("retry", slug, e, file=sys.stderr)
                time.sleep(5 * (i + 1))
            time.sleep(2)
        if not pdf_ok(p):
            gaps.append((slug, "download failed"))
            continue
        pages = kn_pdf2md.pages_of(p)
        if kn_pdf2md.is_scan(pages):
            gaps.append((slug, "scanned PDF"))
            continue
        body = kn_pdf2md.convert(pages)
        fm = ["---", "title: " + yq(title)]
        if ident:
            fm.append("identifier: " + yq(ident))
        fm += ["type: " + typ] + (["date: " + date] if date else []) + [ "jurisdiction: kn", "language: en",
               "status: " + ("in_force" if typ == "constitution" else "unknown"),
               "source: " + yq(BASE + slug + "/"), "retrieved: " + TODAY, "---"]
        out = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write("\n".join(fm) + "\n\n# " + title + "\n\n" + body)
        print("ok", rel, len(pages), "pages")
    print("gaps:", gaps)
    json.dump(gaps, open(os.path.join(RAW, "nia_gaps.json"), "w"))


def main_all():
    import kn_lc_build
    import kn_lc_crawl
    import kn_lc_download
    if "--nia-only" not in sys.argv:
        sys.argv = sys.argv[:1]
        kn_lc_crawl.main()
        kn_lc_download.main()
        kn_lc_build.main()
    main()


if __name__ == "__main__":
    main_all()
