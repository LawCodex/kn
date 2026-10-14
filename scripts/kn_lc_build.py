#!/usr/bin/env python3
"""Convert the Law Commission PDFs (downloaded by kn_lc_download.py into
../_raw/kn/pdf/) to Markdown in the repository.

Selection rules
  * Revised Acts / Revised Ordinances of Nevis: for each chapter (Cap.) the
    latest edition is used (2020 supplement > 2017 supplement > 2009 edition).
    The "law as at" date printed on the cover goes into `last_amended`.
  * Annual Laws: Acts -> annual-acts/<year>/, S.R.O.s -> sros/<year>/,
    Nevis Ordinances -> nevis-annual-ordinances/<year>/, Nevis S.R.O.s ->
    nevis-sros/<year>/.
  * Repealed-Acts-and-Ordinances -> repealed/ (status: repealed).
  * Scanned PDFs with no text layer are skipped (listed in
    ../_raw/kn/skipped.json and in the README).
Usage: kn_lc_build.py
"""
import collections
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kn_pdf2md  # noqa: E402
from kn_http import RAW, pdf_ok  # noqa: E402
from kn_lc_download import local_path, wanted  # noqa: E402

OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TODAY = datetime.date.today().isoformat()
MONTHS = {m: i for i, m in enumerate(
    "january february march april may june july august september october november december".split(), 1)}
SMALL = set("a an and as at by for from in into of on or the to under with".split())


def yq(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def slug(s, n=90):
    s = s.lower().replace("’", "").replace("'", "").replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:n].rstrip("-")


ACRONYMS = set("OECS ICC CARICOM ECSC ECCB UK US USA UN CBI NIA CSME VAT ICT HIV AIDS OAS ECCAA "
                "CARIFESTA WTO CTO LIAT SKN CCJ CARICAD ECTEL CDB UWI OECS ILO IMF ECCU CXC".split())


def _cap_word(w, first):
    lw = w.lower()
    core = re.sub(r"[^a-z0-9]", "", lw)
    if core.upper() in ACRONYMS:
        return re.sub(core, core.upper(), lw, count=1)
    if not first and core in SMALL and not re.match(r"^\(", w):
        return lw
    if re.fullmatch(r"[ivx]+", core) and len(core) <= 4:
        return w.upper()
    return re.sub(r"[a-z]", lambda m: m.group(0).upper(), lw, count=1)


def titlecase(s):
    words = re.sub(r"\s+", " ", s.strip()).split(" ")
    out = []
    for i, w in enumerate(words):
        parts = w.split("-")
        out.append("-".join(_cap_word(p, i == 0 and j == 0) if p else p for j, p in enumerate(parts)))
    return " ".join(out)


def parse_date(d, m, y):
    mo = next((v for k, v in MONTHS.items() if k.startswith(m.lower()[:3])), 0)
    if not mo:
        return None
    try:
        return datetime.date(int(y), mo, int(d)).isoformat()
    except ValueError:
        return None


def as_at(text):
    head = re.sub(r"\s+", " ", text[:6000])
    m = re.search(r"law as at:?\s*(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+),?\s+(\d{4})", head, re.I)
    if not m:
        m = re.search(r"Revision Date:?\s*(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\.?,?\s+(\d{4})", head, re.I)
    return parse_date(*m.groups()) if m else None


# ---------------------------------------------------------------- revised
CAP_RE = re.compile(r"^Ch-(\d+)_(\d+)(-?N)?[-_]", re.I)


def revised_title(pages, fallback):
    p0 = "\n".join(pages[:1])
    lines = [l.strip() for l in p0.split("\n") if l.strip()]
    cover = None
    for i, l in enumerate(lines):
        if re.match(r"^CHAPTER\s+\d+\.\d+", l):
            t = []
            for l2 in lines[i + 1:i + 6]:
                if re.match(r"^(and Subsidiary|Revised Edition|showing|This is|Prepared)", l2, re.I):
                    break
                t.append(l2)
            cover = " ".join(t)
            break
    head = None
    for l in lines[:7]:
        if re.match(r"^(LAWS OF SAINT|AND NEVIS|Revision Date|CAP\.?\s|\d+$|ST\.? CHRISTOPHER)", l, re.I):
            continue
        head = l
        break
    norm = lambda s: re.sub(r"[^a-z]", "", (s or "").lower())  # noqa: E731
    if cover and head and norm(head) == norm(cover):
        return re.sub(r"\s+", " ", head)
    if cover and cover.upper() == cover and len(cover) > 3:
        return titlecase(cover)
    if cover:
        return re.sub(r"\s+", " ", cover)
    return fallback


def cap_key(name):
    m = CAP_RE.match(name)
    if not m:
        return None
    nev = bool(m.group(3)) or bool(re.match(r"^Ch-\d+_\d+-N-", name))
    return (int(m.group(1)), int(m.group(2)), nev)


def fname_title(name):
    t = PART_RE.sub("", re.sub(r"\.pdf$", "", name, flags=re.I))
    t = re.sub(r"^(Ch-\d+_\d+(-?N)?|Act-\d+-of-\d{4}|SRO-\d+-of-\d{4}(-N)?|No-\d+-of-\d{4}|Ord_-\d+-o[fF]-\d{4})-", "", t, flags=re.I)
    t = t.replace("St_-", "St. ").replace("No_-", "No. ").replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", t).strip()


def cited_title(text):
    """Short title from the 'may be cited as the ...' clause, if any."""
    t = re.sub(r"\s+", " ", text[:20000])
    m = re.search(r"may be cited as (?:the )?[“\"]?((?=[A-Z])(?:No\. ?\d|St\. |[^.;“”\"]){4,160}?(?:\d{4}|Act|Ordinance|Order|Regulations|Rules|Notice|Resolution|Proclamation)(?:,? \d{4})?)[”\"]?\s*(?:[.;,]|and\b)", t)
    if not m:
        return None
    title = m.group(1).strip()
    if re.search(r"\b(section|subsection|paragraph)\b", title, re.I):
        return None
    return title


def sro_desc(text):
    """Descriptive heading printed under 'STATUTORY RULES AND ORDERS No. X of Y'."""
    lines = [l.strip() for l in text[:4000].split("\n") if l.strip()]
    for i, l in enumerate(lines):
        if re.match(r"^No\.?\s*\d+[A-Z]?\s+of\s+\d{4}$", l, re.I) and i and \
                re.search(r"STATUTORY RULES|ISLAND OF NEVIS", " ".join(lines[max(0, i - 2):i]), re.I):
            out = []
            for l2 in lines[i + 1:i + 8]:
                if re.match(r"^(\[Published|BY THE|WHEREAS|In exercise|A PROCLAMATION|This Order is made|"
                            r"This Notice|The Minister|IN EXERCISE|\d+\.?$|ARRANGEMENT)", l2, re.I):
                    break
                out.append(l2)
            d = re.sub(r"\s+", " ", " ".join(out)).strip().rstrip(".")
            d = re.sub(r"(\d) (st|nd|rd|th)\b", r"\1\2", d)
            d = re.sub(r"^(ISLAND OF NEVIS\s+)?(RESOLUTION\s+)(?=RESOLUTION|Resolution)", "", d)
            d = re.sub(r"^ISLAND OF NEVIS\s+", "", d)
            if len(d) > 220:
                d = d[:200].rsplit(" ", 1)[0] + "…"
            return d or None
    return None


def nice(t):
    if t and t.upper() == t and re.search(r"[A-Z]{3}", t):
        return titlecase(t)
    return t


def write(rel, fm, title, body):
    out = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    lines = ["---", "title: " + yq(title)]
    for k, v in fm:
        if v:
            lines.append("%s: %s" % (k, v))
    lines.append("---")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n\n# " + title + "\n\n" + body)


def plan(inv):
    """Return list of jobs: dict(item, kind, rel...)"""
    jobs = []
    revised = collections.defaultdict(list)
    for f in inv:
        fo, name = f["folder"], f["name"]
        m = re.match(r"Revised-(Acts-of-St-Kitts-and-Nevis|Ordinances-of-Nevis)/.*-(\d{4})$", fo)
        if m and cap_key(name):
            revised[cap_key(name)].append((int(m.group(2)), f))
            continue
        if m:  # Revised-Ordinances-of-Nevis-2023/2024: annual Nevis Ordinances and SROs
            year = m.group(2)
            if name.upper().startswith("SRO"):
                jobs.append(dict(item=f, kind="nevis-sro", year=year))
            else:
                jobs.append(dict(item=f, kind="nevis-ordinance", year=year))
            continue
        if fo == "Repealed-Acts-and-Ordinances":
            jobs.append(dict(item=f, kind="repealed"))
            continue
        if fo == "Revised-Edition-Indices":
            continue
        if name.startswith("The-Constitution"):
            jobs.append(dict(item=f, kind="constitution"))
            continue
        m = re.match(r"Annual-Laws(?:/(\d{4})/(.*))?$", fo)
        if m:
            year = m.group(1) or re.search(r"(\d{4})", name).group(1)
            sub = (m.group(2) or "ACTs").lower()
            if sub == "acts":
                kind = "act"
            elif sub == "sros" and not re.search(r"-of-\d{4}-N-", name, re.I):
                kind = "sro"
            elif name.upper().startswith("SRO"):
                kind = "nevis-sro"
            else:
                kind = "nevis-ordinance"
            jobs.append(dict(item=f, kind=kind, year=year))
            continue
        print("unclassified", fo, name, file=sys.stderr)
    for key, eds in sorted(revised.items()):
        eds.sort(key=lambda e: (e[0], e[1]["changed"], len(e[1]["name"])))
        year, f = eds[-1]
        # "_1" duplicates inside the same edition: prefer the later-changed file
        same = [e for e in eds if e[0] == year]
        if len(same) > 1:
            same.sort(key=lambda e: (e[1]["changed"], os.path.getsize(local_path(e[1])) if os.path.exists(local_path(e[1])) else 0))
            f = same[-1][1]
        jobs.append(dict(item=f, kind="revised", key=key, edition=year,
                         editions=sorted({e[0] for e in eds})))
    return jobs


PART_RE = re.compile(r"[-_](?:prt|part)[-_]?\d|[-_](?:Arrangements|AoS)\b", re.I)
ARR_RE = re.compile(r"[-_](?:prt|part)[-_]?1(?!\d)|[-_](?:Arrangements|AoS)\b", re.I)


def fname_num(name, folder_year):
    n = PART_RE.sub("", re.sub(r"\.pdf$", "", name, flags=re.I))
    m = re.search(r"(\d+[A-Z]?)[-_]?o[fd][-_](\d{4})", n, re.I)
    if m:
        return m.group(1).upper(), m.group(2)
    m = re.match(r"(?:Act|SRO|No|Ord_?)[-_]+(\d+[A-Z]?)[-_]", n, re.I)
    if m:
        ys = re.findall(r"(?<!\d)((?:19|20)\d{2})(?!\d)", n[m.end():])
        return m.group(1).upper(), (ys[-1] if ys else folder_year)
    return None


def text_num(text, kind):
    head = text[:2500]
    if kind in ("sro", "nevis-sro"):
        m = re.search(r"STATUTORY\s+RULES\s+AND\s+ORDERS\s+No\.?\s*(\d+[A-Z]?)\s+of\s+(\d{4})", head, re.I)
        if m:
            return m.group(1).upper(), m.group(2)
    m = re.search(r"\bNo\.?\s*(\d+[A-Z]?)\s+of\s+(\d{4})", head)
    return (m.group(1).upper(), m.group(2)) if m else None


def numkey(n):
    m = re.match(r"(\d+)(.*)", n)
    return "%03d%s" % (int(m.group(1)), m.group(2).lower())


def words(text):
    return set(re.findall(r"[a-z]{4,}", text.lower()))


def similar(a, b):
    wa, wb = words(a), words(b)
    return len(wa & wb) / max(1, len(wa), len(wb)) > 0.8


def annual_units(jobs, texts):
    """Group annual items by (kind, number, year); put arrangement PDFs
    (prt-1 / Arrangements / AoS) in front of the body; drop duplicates."""
    groups = collections.OrderedDict()
    for j in jobs:
        f = j["item"]
        t = texts.get(f["url"], "")
        num = None
        if j["kind"] in ("sro", "nevis-sro"):
            num = text_num(t, j["kind"]) or fname_num(f["name"], j["year"])
        else:
            num = fname_num(f["name"], j["year"]) or text_num(t, j["kind"])
        if not num:
            num = ("0", j["year"])
        groups.setdefault((j["kind"], num), []).append(j)
    units = []
    for (kind, num), js in groups.items():
        arr = [j for j in js if ARR_RE.search(j["item"]["name"])]
        mains = [j for j in js if j not in arr]
        if not mains:
            for j in arr:
                units.append(dict(skip=j["item"]["url"]))
            continue
        clusters = []
        for j in mains:
            for c in clusters:
                if similar(texts.get(c[0]["item"]["url"], ""), texts.get(j["item"]["url"], "")):
                    c.append(j)
                    break
            else:
                clusters.append([j])
        for c in clusters:
            c.sort(key=lambda j: (-len(texts.get(j["item"]["url"], "")), j["item"]["folder"] == "Annual-Laws"))
            best = c[0]
            items = [best["item"]]
            head = texts.get(best["item"]["url"], "")[:8000]
            if len(clusters) == 1 and arr and not re.search(r"ARRANGEMENT\s+OF", head, re.I):
                items = [arr[0]["item"]] + items
            units.append(dict(kind=kind, num=num, year=best["year"], items=items,
                              dropped=[j["item"]["url"] for j in c[1:]]))
    return units


def main():
    inv = wanted(json.load(open(os.path.join(RAW, "inventory.json"))))
    jobs = plan(inv)
    skipped, written, counts = [], [], collections.Counter()
    pages_of, texts = {}, {}
    ok_jobs = []
    for j in jobs:
        f = j["item"]
        p = local_path(f)
        if not pdf_ok(p):
            skipped.append((f["url"], "download failed / incomplete"))
            continue
        pg = kn_pdf2md.pages_of(p)
        if kn_pdf2md.is_scan(pg):
            skipped.append((f["url"], "scanned PDF (no text layer)"))
            continue
        pages_of[f["url"]] = pg
        texts[f["url"]] = "".join(pg)
        ok_jobs.append(j)
    annual_kinds = ("act", "sro", "nevis-sro", "nevis-ordinance")
    units = [dict(j, items=[j["item"]]) for j in ok_jobs if j["kind"] not in annual_kinds]
    units += annual_units([j for j in ok_jobs if j["kind"] in annual_kinds], texts)
    used = set()
    dropped = []
    for u in units:
        if "skip" in u:
            skipped.append((u["skip"], "only the arrangement of sections is published (no enacted text)"))
            continue
        items = u["items"]
        f = items[-1]
        pages = pages_of[f["url"]]
        text = texts[f["url"]]
        body = "\n".join(kn_pdf2md.convert(pages_of[i["url"]]) for i in items)
        kind = u["kind"]
        date_as_at = as_at(text)
        fm = []
        if kind in ("revised", "repealed"):
            key = cap_key(f["name"])
            nev = key[2]
            cap = "%d.%02d%s" % (key[0], key[1], "N" if nev else "")
            title = revised_title(pages, fname_title(f["name"]))
            if kind == "repealed":
                rel = "repealed/cap-%02d-%02d%s-%s.md" % (key[0], key[1], "n" if nev else "", slug(title))
                status = "repealed"
            elif nev:
                rel = "nevis-ordinances/cap-%02d-%02dn-%s.md" % (key[0], key[1], slug(title))
                status = "in_force"
            else:
                rel = "revised-acts/title-%02d/cap-%02d-%02d-%s.md" % (key[0], key[0], key[1], slug(title))
                status = "in_force"
            if kind == "revised":
                ed = "Revised Edition as at 31 December 2009" if u["edition"] == 2009 else \
                    "Revised Edition, %d Supplement (as at 31 December %d)" % (u["edition"], u["edition"])
                if u["edition"] == 2009 and date_as_at and not date_as_at.startswith("2009"):
                    ed = "Revised Edition as at %s (as included in the Revised Acts/Ordinances as at 31 December 2009)" % date_as_at
            else:
                ed = "Revised Edition as at %s (listed by the Law Commission under Repealed Acts and Ordinances)" % (date_as_at or "unknown")
            fm = [("identifier", yq("Cap. " + cap)),
                  ("type", "ordinance" if nev else "act"),
                  ("jurisdiction", "kn"), ("language", "en"),
                  ("last_amended", date_as_at),
                  ("status", status),
                  ("edition", yq(ed))]
        elif kind == "constitution":
            title = "The Constitution of Saint Christopher and Nevis"
            rel = "constitution/constitution-of-saint-christopher-and-nevis.md"
            fm = [("identifier", yq("Schedule 1 to the Saint Christopher and Nevis Constitution Order 1983 "
                                    "(S.I. 1983 No. 881), as extracted from Cap. 1.01")),
                  ("type", "constitution"), ("jurisdiction", "kn"), ("language", "en"),
                  ("date", "1983-06-23"), ("status", "in_force")]
        else:
            n, y = u["num"]
            title = cited_title(text)
            if kind in ("sro", "nevis-sro") and (not title or re.fullmatch(r"(A )?(Proclamation|Resolution|Order|Notice)", title, re.I)):
                title = sro_desc(text) or title
            title = nice(title or fname_title(f["name"]))
            labels = {"act": ("Act No. %s of %s", "act", "annual-acts/%s/act-%s-%s-%s.md"),
                      "sro": ("S.R.O. No. %s of %s", "regulation", "sros/%s/sro-%s-%s-%s.md"),
                      "nevis-sro": ("S.R.O. No. %s of %s (Nevis)", "regulation", "nevis-sros/%s/sro-%s-%s-n-%s.md"),
                      "nevis-ordinance": ("Nevis Ordinance No. %s of %s", "ordinance",
                                          "nevis-annual-ordinances/%s/ordinance-%s-%s-%s.md")}
            ident, typ, pat = labels[kind]
            rel = pat % (y, y, numkey(n), slug(title, 70))
            fm = [("identifier", yq(ident % (n, y))), ("type", typ),
                  ("jurisdiction", "kn"), ("language", "en"), ("status", "unknown")]
            dropped += u.get("dropped", [])
        base = rel
        k = 2
        while rel in used:
            rel = base[:-3] + "-%d.md" % k
            k += 1
        used.add(rel)
        fm.append(("source", yq(f["url"])))
        if len(items) > 1:
            fm.append(("source_parts", "[" + ", ".join(yq(i["url"]) for i in items) + "]"))
        fm.append(("retrieved", TODAY))
        write(rel, fm, title, body)
        written.append(rel)
        counts[rel.split("/")[0]] += 1
    json.dump(skipped, open(os.path.join(RAW, "skipped.json"), "w"), indent=1)
    json.dump(written, open(os.path.join(RAW, "written.json"), "w"), indent=1)
    json.dump(dropped, open(os.path.join(RAW, "duplicates_dropped.json"), "w"), indent=1)
    print(dict(counts), "skipped:", len(skipped), "duplicates dropped:", len(dropped))
    for s in skipped:
        print("  skip", *s)


if __name__ == "__main__":
    main()
