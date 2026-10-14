"""Polite HTTP helper for the LawCodex Saint Kitts and Nevis scripts.

One connection, a fixed delay between requests, retries with exponential
backoff, and a local cache in ../_raw/kn/ so that re-runs do not re-download.
"""
import hashlib
import os
import subprocess
import sys
import time

import requests

UA = "LawCodex/1.0 (+https://github.com/LawCodex)"
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.abspath(os.path.join(HERE, "..", "..", "_raw", "kn"))
DELAY = 2.5

_s = requests.Session()
_s.headers["User-Agent"] = UA
_last = [0.0]


def _wait():
    d = time.time() - _last[0]
    if d < DELAY:
        time.sleep(DELAY - d)
    _last[0] = time.time()


def get(url, tries=5, timeout=300):
    """GET with retries/backoff; returns requests.Response (status 200) or raises."""
    err = None
    for i in range(tries):
        _wait()
        try:
            r = _s.get(url, timeout=timeout)
            if r.status_code == 200:
                return r
            if r.status_code == 404:
                r.raise_for_status()
            err = "HTTP %d" % r.status_code
        except requests.HTTPError:
            raise
        except requests.RequestException as e:
            err = str(e)
        print("  retry %d %s: %s" % (i + 1, url, err), file=sys.stderr)
        time.sleep(5 * 2 ** i)
    raise RuntimeError("failed %s: %s" % (url, err))


def cached_text(url, sub="html"):
    d = os.path.join(RAW, sub)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, hashlib.sha1(url.encode()).hexdigest() + ".html")
    if os.path.exists(p) and os.path.getsize(p) > 0:
        return open(p, encoding="utf-8").read()
    t = get(url).text
    open(p, "w", encoding="utf-8").write(t)
    return t


def pdf_ok(path):
    if not os.path.exists(path) or os.path.getsize(path) < 100:
        return False
    with open(path, "rb") as f:
        head = f.read(5)
        f.seek(max(0, os.path.getsize(path) - 2048))
        tail = f.read()
    return head == b"%PDF-" and b"%%EOF" in tail and \
        subprocess.run(["pdfinfo", path], capture_output=True).returncode == 0


def cached_pdf(url, path):
    """Download url to path unless a complete PDF is already there. Returns True if OK."""
    if pdf_ok(path):
        return True
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for i in range(3):
        try:
            r = get(url)
        except Exception as e:  # noqa: BLE001
            print("  FAIL", url, e, file=sys.stderr)
            return False
        exp = r.headers.get("Content-Length")
        if exp and int(exp) != len(r.content):
            print("  truncated", url, file=sys.stderr)
            continue
        with open(path + ".part", "wb") as f:
            f.write(r.content)
        os.replace(path + ".part", path)
        if pdf_ok(path):
            return True
        print("  not a complete PDF", url, file=sys.stderr)
    return False
