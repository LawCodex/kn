#!/usr/bin/env python3
"""Fetch the legislation of Saint Kitts and Nevis that is published on the
Nevis Island Administration document library (https://nia.gov.kn), then
convert it to Markdown.

The complete Revised Laws are published by the Law Commission
(lawcommission.gov.kn), but that site's Terms of Use forbid reproducing,
copying, distributing or publishing any portion of the site for any public
or commercial purpose, so it is NOT crawled (see README).

nia.gov.kn's robots.txt only disallows /wp-admin/. Each /cdl_document/<slug>/
URL below returns the PDF directly. We wait 2 s between requests.
Usage: kn_fetch.py
"""
import datetime
import json
import os
import re
import subprocess
import sys
import time

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kn_pdf2md  # noqa: E402

UA = "LawCodex/1.0 (+https://github.com/LawCodex)"
RAW = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_raw", "kn"))
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
BASE = "https://nia.gov.kn/cdl_document/"
TODAY = datetime.date.today().isoformat()

# (slug on nia.gov.kn, output path, title, type, jurisdiction note)
DOCS = [
    ("the-constitution-of-st-christopher-and-nevis", "constitution/saint-christopher-and-nevis-constitution-order-1983.md",
     "The Saint Christopher and Nevis Constitution Order 1983", "constitution", "S.I. 1983 No. 881"),
    ("labour-act", "acts/labour-act.md", "Labour Act", "act", ""),
    ("protection-of-employment-act", "acts/protection-of-employment-act.md", "Protection of Employment Act", "act", "Cap. 18.27"),
    ("labour-minimum-wage-act", "acts/labour-minimum-wage-act.md", "Labour (Minimum Wage) Act", "act", "Cap. 18.19"),
    ("holidays-with-pay-act", "acts/holidays-with-pay-act.md", "Holidays with Pay Act", "act", "Cap. 18.15"),
    ("protection-of-wages", "acts/protection-of-wages-act.md", "Protection of Wages Act", "act", "Cap. 18.28"),
    ("public-service-act", "acts/public-service-act.md", "Public Service Act", "act", "Cap. 22.09"),
    ("the-co-operative-societies-act-2011", "acts/co-operative-societies-act-2011.md", "Co-operative Societies Act, 2011", "act", "No. 31 of 2011"),
    ("excise-tax-act", "acts/excise-tax-act.md", "Excise Tax Act, 2010", "act", "No. 4 of 2010"),
    ("value-added-tax-vat-act", "acts/value-added-tax-act.md", "Value Added Tax Act, 2010", "act", "No. 3 of 2010"),
    ("companies-ordinance-cap-7-06-of-the-revised-laws-2017-ch-07-_06n-companies-ordinance",
     "nevis-ordinances/cap-07-06-companies-ordinance.md", "Companies Ordinance (Cap. 7.06, Nevis)", "ordinance", "Cap. 7.06"),
    ("multiform-foundations-ordinance", "nevis-ordinances/multiform-foundations-ordinance.md", "Multiform Foundations Ordinance, 2004", "ordinance", "Nevis No. 2 of 2004"),
    ("nbco-1984-as-amended-to-2002", "nevis-ordinances/nevis-business-corporation-ordinance-1984.md",
     "Nevis Business Corporation Ordinance, 1984 (as amended to 2002)", "ordinance", ""),
    ("nieto-1994-as-amended-to-2002", "nevis-ordinances/nevis-international-exempt-trust-ordinance-1994.md",
     "Nevis International Exempt Trust Ordinance, 1994 (as amended to 2002)", "ordinance", ""),
    ("nllco-1995-as-amended-to-2002", "nevis-ordinances/nevis-limited-liability-company-ordinance-1995.md",
     "Nevis Limited Liability Company Ordinance, 1995 (as amended to 2002)", "ordinance", ""),
    ("nevis-investment-promotion-agency-ordinance-2008", "nevis-ordinances/nevis-investment-promotion-agency-ordinance-2008.md",
     "Nevis Investment Promotion Agency Ordinance, 2008", "ordinance", "Nevis No. 2 of 2008"),
    ("nevis-offshore-banking-ordinance-1996-as-amended", "nevis-ordinances/nevis-offshore-banking-ordinance-1996.md",
     "Nevis Offshore Banking Ordinance, 1996 (as amended)", "ordinance", ""),
    ("the-nevis-international-insurance-ordinance-2004", "nevis-ordinances/nevis-international-insurance-ordinance-2004.md",
     "Nevis International Insurance Ordinance, 2004", "ordinance", "Nevis No. 1 of 2004"),
    ("the-nevis-international-insurance-ordinance-2006", "nevis-ordinances/nevis-international-insurance-amendment-ordinance-2006.md",
     "Nevis International Insurance (Amendment) Ordinance, 2006", "ordinance", "Nevis No. 1 of 2006"),
    ("the-nevis-international-mutual-funds-ordinance-2007", "nevis-ordinances/nevis-international-mutual-funds-miscellaneous-amendments-ordinance-2007.md",
     "Nevis International Mutual Funds (Miscellaneous Amendments) Ordinance, 2007", "ordinance", ""),
]


def pdf_ok(path):
    if not os.path.exists(path) or os.path.getsize(path) < 100:
        return False
    with open(path, "rb") as f:
        head = f.read(5)
        f.seek(max(0, os.path.getsize(path) - 2048))
        tail = f.read()
    return head == b"%PDF-" and b"%%EOF" in tail and \
        subprocess.run(["pdfinfo", path], capture_output=True).returncode == 0


def yq(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main():
    os.makedirs(os.path.join(RAW, "pdf"), exist_ok=True)
    s = requests.Session()
    s.headers["User-Agent"] = UA
    gaps = []
    for slug, rel, title, typ, ident in DOCS:
        p = os.path.join(RAW, "pdf", slug[:100] + ".pdf")
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
        fm += ["type: " + typ, "jurisdiction: kn", "language: en", "status: in_force",
               "source: " + yq(BASE + slug + "/"), "retrieved: " + TODAY, "---"]
        out = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write("\n".join(fm) + "\n\n# " + title + "\n\n" + body)
        print("ok", rel, len(pages), "pages")
    print("gaps:", gaps)
    json.dump(gaps, open(os.path.join(RAW, "gaps.json"), "w"))


if __name__ == "__main__":
    main()
