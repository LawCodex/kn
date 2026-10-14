# Saint Kitts and Nevis — LawCodex

Legislation of the Federation of Saint Christopher (Saint Kitts) and Nevis as plain Markdown.
Part of [LawCodex](https://github.com/LawCodex).

**Status: full** for what the official source publishes online. That covers the Revised Laws
(Acts and Nevis Ordinances, as at 31 December 2009 with the 2017 and 2020 supplements) and the
annual Acts and S.R.O.s for 2018–2025. Older annual laws (before 2018) are not published online
(see [Gaps](#what-is-not-covered-gaps)).

## What is covered

| Directory | Contents | Files |
|---|---|---|
| `constitution/` | The Constitution of Saint Christopher and Nevis: the Law Commission's consolidated text (extracted from Cap. 1.01), plus the Saint Christopher and Nevis Constitution Order 1983 (S.I. 1983 No. 881) as made (from nia.gov.kn) | 2 |
| `revised-acts/title-NN/` | Revised Acts of Saint Kitts and Nevis, one file per Chapter (Cap.), grouped by title number (`title-01` … `title-25`). Each file is the latest revised edition | 495 |
| `nevis-ordinances/` | Revised Ordinances of Nevis (Cap. x.yy(N)), latest revised edition | 36 |
| `repealed/` | Texts that the Law Commission lists under "Repealed Acts and Ordinances": earlier editions of Caps. 3.10, 4.28, 7.01N, 7.04N and 12.04, which were replaced by later laws under the same Cap. number | 5 |
| `annual-acts/<year>/` | Annual Acts as enacted: 2018 (17), 2019 (14), 2020 (17), 2021 (22), 2022 (7), 2023 (15), 2024 (23), 2025 (24). Also Act No. 22 of 2014 (Domestic Violence Act) and Act No. 10 of 2017 (Land Registry Act), which are filed among the 2019 and 2021 annual laws | 141 |
| `sros/<year>/` | Statutory Rules and Orders (federal): 2018 (30), 2019 (36), 2020 (58), 2021 (43), 2022 (23), 2023 (4), 2024 (37), 2025 (15) | 246 |
| `nevis-annual-ordinances/<year>/` | Nevis Ordinances as enacted: 2018 (7), 2019 (8), 2020 (2), 2023 (5). Also two amendment Ordinances of 2006 and 2007 that only nia.gov.kn publishes | 24 |
| `nevis-sros/<year>/` | Nevis S.R.O.s (Nevis Island Administration): 2018 (9), 2019 (6), 2020 (7), 2021 (5), 2024 (4) | 31 |

**Total: 980 files.**

### Revised editions and dates

The Law Commission publishes the Revised Laws as one PDF per Chapter in three sets:

- **Revised Acts / Ordinances as at 31 December 2009.** This set still includes many Chapters
  whose latest revision is the edition "as at 31 December 2002".
- **2017 supplement**: Chapters re-issued as at 31 December 2017.
- **2020 supplement**: Chapters re-issued as at 31 December 2020.

For each Cap. the newest edition is used (2020 > 2017 > 2009). The "law as at" date printed on
the PDF's cover goes in `last_amended`, and `edition` gives the edition in words. The result:
288 Chapters as at 2002-12-31, 78 as at 2009-12-31, 104 as at 2017-12-31 and 61 as at
2020-12-31 (Acts and Nevis Ordinances combined). Revised-edition PDFs bundle the Chapter's
subsidiary legislation after the Act, and that text is kept as it appears in the PDF.

**Annual laws passed after a Chapter's edition date are not consolidated into it.** To get the
current law, read the revised Chapter together with the later amending Acts in `annual-acts/`
(and, for Nevis, `nevis-annual-ordinances/`). `status: in_force` on a revised Chapter means "in
force at its edition date". Annual Acts and S.R.O.s have `status: unknown`, since many are
amending, commencement or spent instruments.

## Sources

1. **Law Commission of Saint Kitts and Nevis** (Ministry of Justice and Legal Affairs),
   https://lawcommission.gov.kn/. This is the main source for all files except three. Its document
   library is at https://lawcommission.gov.kn/laws/ (a WordPress "Simple File List" listing,
   folders `Revised-Acts-of-St-Kitts-and-Nevis/…-2009|2017|2020`,
   `Revised-Ordinances-of-Nevis/…-2009|2017|2020|2023|2024`, `Annual-Laws/<year>/ACTs|SROs|NEVIS-Ordinances-and-SROs`,
   `Repealed-Acts-and-Ordinances`). The `Act02and09TOC`, `Act17TOC`, `Ord02and09TOC` and `Ord17TOC`
   folders hold byte-identical copies of the revised sets and were not used twice. The
   `Revised-Edition-Indices` (indexes, not laws) and the order form under `Publications` were not
   converted.
2. **Nevis Island Administration** document library, https://nia.gov.kn/documents/. Three files
   come from here: the Constitution Order 1983 as made, the Nevis International Insurance
   (Amendment) Ordinance 2006, and the Nevis International Mutual Funds (Miscellaneous Amendments)
   Ordinance 2007. The other nia.gov.kn texts in the previous version of this repo (Caps. 18.15,
   18.19, 18.27, 18.28, 22.09, Acts 3 and 4 of 2010, Act 31 of 2011, and the Nevis Ordinances
   Caps. 7.01N, 7.03N, 7.04N, 7.05N, 7.06N, 7.08N, 6.12N, 7.07N and 7.09N) were replaced by the
   Law Commission's revised editions of the same Chapters.

Each file's `source` field gives the exact PDF URL. When a law is published as two PDFs (a
separate "Arrangement of Sections" / "prt-1" file plus the body), they are joined in that order and
`source_parts` lists both. Where the Law Commission posts the same law twice (for example in
`Annual-Laws/` and `Annual-Laws/2025/ACTs/`), one copy is kept: 14 duplicate PDFs were dropped.

S.R.O. numbers come from the "STATUTORY RULES AND ORDERS No. X of YYYY" heading printed in the
instrument, because a few file names on the site have the wrong number. Act and Ordinance numbers
come from the file names. Titles are the short title from the "may be cited as" clause. If there
is none, the revised edition's running head or cover title is used. For proclamations and
resolutions, the descriptive heading printed under the S.R.O. number is used, shortened with "…"
when very long.

## Copyright, terms of use and why the Law Commission site was crawled

An earlier build skipped lawcommission.gov.kn because of its Terms of Use. The LawCodex project
owner later reviewed the question and approved crawling the site, for these reasons:

- The site's [Terms of Use](https://lawcommission.gov.kn/home/terms-of-use/) are an unadapted
  generic website template (they even refer to "The Sample Store"). They concern use of "the
  Site" and assert no copyright in legislation.
- The site's `robots.txt` places no restrictions (it only has a `Sitemap` line).
- The Copyright Act 2024 (Act No. 14 of 2024) has no Crown or government copyright provision
  claiming legislation. It also has no express exclusion for official texts.
- Under the Official Gazette Act 2023 (Act No. 1 of 2023), laws are published on a public
  government website (gazette.gov.kn, in maintenance mode at retrieval time). The Law
  Commission is the only working official online source.
- LawCodex is non-commercial. Texts are reproduced faithfully, with attribution to the Law
  Commission and a link to each source PDF. **We will remove material on request from the
  Government of Saint Kitts and Nevis.**

The crawl was polite: one connection, about 2.5 seconds between requests, retries with backoff,
the User-Agent `LawCodex/1.0 (+https://github.com/LawCodex)`, and a local cache so re-runs do not
download again.

This is not an official publication. For authoritative text, consult the Official Gazette or the
Law Commission.

## What is not covered (gaps)

- **Annual laws before 2018** are not on the Law Commission site (its `Annual-Laws` folder starts
  in 2018), except the two filed later. Amendments made between a Chapter's edition date and 2018
  are therefore missing. This affects Chapters whose latest edition is 2002, 2009 or 2017.
- **Nevis annual laws**: no Nevis Ordinances are listed for 2021, 2022, 2024 or 2025, and no Nevis
  S.R.O.s for 2022, 2023 or 2025.
- **Scanned PDFs with no text layer** were skipped (no OCR):
  - `Annual-Laws/2020/SROs/COVID-19-Notice-Extra-Ordinary-Gazette-No_-21-27-March-2020.pdf`
  - `Annual-Laws/2020/SROs/SRO-26-of-2020-International-Trade-in-Wild-Flora-and-Fauna-Amendment-of-Schedule-Order-2020.pdf`
  - `Annual-Laws/2023/SROs/No-41-of-2023-Freedom-of-Information-Act-Appointed-Day-Order-2023.pdf`
  - The Labour Act on nia.gov.kn (https://nia.gov.kn/cdl_document/labour-act/)
- **Act No. 24 of 2024** (Caribbean Community Climate Change Centre (Agreement) Act, 2024): only
  its arrangement of sections is published, not the enacted text. It is not included.
- Subsidiary legislation made before 2018 is included only where a revised Chapter bundles it.

## Format

One Markdown file per law with YAML front matter: `title`, `identifier` (Cap. number, "Act No. X
of YYYY", "S.R.O. No. X of YYYY"), `type`, `jurisdiction`, `language`, `last_amended` (revised
editions), `status`, `edition`, `source`, `retrieved`. The text was extracted from the official
PDFs with `pdftotext` (poppler), without OCR, and kept as extracted. Only these changes were made:

- Running page headers, footers and page numbers were removed.
- CHAPTER / PART / SCHEDULE / ARRANGEMENT lines became level-2 headings.
- Section numbers became level-3 headings.

Marginal notes (section titles printed in the margin) appear as separate lines next to the
section. In annual Acts typeset with side-notes, the cover lines may be jumbled.

File names: `revised-acts/title-20/cap-20-22-income-tax-act.md`,
`nevis-ordinances/cap-07-06n-companies-ordinance.md`, `annual-acts/2024/act-2024-014-copyright-act-2024.md`,
`sros/2024/sro-2024-047-….md`.

## Regenerate

```sh
pip install -r scripts/requirements.txt   # plus poppler-utils (pdftotext, pdfinfo)
python3 scripts/kn_fetch.py               # crawl + download (cached in ../_raw/kn) + convert
```

The scripts:

| Script | Role |
|---|---|
| `kn_lc_crawl.py` | Walks the Law Commission file library (all folders and pages) and writes `../_raw/kn/inventory.json` |
| `kn_lc_download.py` | Downloads the PDFs and checks that each one is complete |
| `kn_lc_build.py` | Picks the editions, groups the files and writes the Markdown |
| `kn_fetch.py` | Runs all of the above, then the nia.gov.kn step (`--nia-only` runs only that step) |
| `kn_http.py` | Polite HTTP helper |
| `kn_pdf2md.py` | PDF-to-Markdown converter |

Retrieved: 2026-10-15.
