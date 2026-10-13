# Saint Kitts and Nevis — LawCodex

Legislation of the Federation of Saint Christopher (Saint Kitts) and Nevis as plain Markdown.
Part of [LawCodex](https://github.com/LawCodex).

**Status: minimal.** This repo has the Constitution and a small set of Acts and Nevis
Ordinances. It does not have the full Revised Laws, because the only complete online source
does not allow republication (see below).

## What is covered

| Directory | Contents | Files |
|---|---|---|
| `constitution/` | The Saint Christopher and Nevis Constitution Order 1983 (S.I. 1983 No. 881), with Schedule 1 (the Constitution) and Schedule 2 (transitional provisions) | 1 |
| `acts/` | Federal Acts: revised-edition chapters (Cap. 18.15, 18.19, 18.27, 18.28, 22.09) and Acts No. 3 and 4 of 2010 and No. 31 of 2011 | 8 |
| `nevis-ordinances/` | Ordinances of the Nevis Island Assembly: Companies Ordinance (Cap. 7.06), Nevis Business Corporation Ordinance, LLC Ordinance, International Exempt Trust Ordinance, Multiform Foundations Ordinance, Offshore Banking, International Insurance, Mutual Funds and Nevis Investment Promotion Agency Ordinances | 10 |

That makes 19 texts in total. The PDFs come from the
[Nevis Island Administration document library](https://nia.gov.kn/documents/). Some are revised
editions prepared by the Law Revision Commissioner (the "as at" date is stated in each text).
Others are the Acts or Ordinances as enacted, or "as amended" compilations published by the
NIA. Each file's `source` field gives the exact URL.

## What is not covered (gaps)

- **The Revised Laws of Saint Kitts and Nevis** are not included: the Revised Acts as at
  31 December 2009, 2017 and 2020, the Revised Ordinances of Nevis, the annual laws and the
  subsidiary legislation. They are published by the Law Commission at
  https://lawcommission.gov.kn/. That site's
  [Terms of Use](https://lawcommission.gov.kn/home/terms-of-use/) say users agree not to
  "reproduce, copy, distribute, modify, publish, transmit, display, use, reuse, re-publicize,
  … or exploit for any public or commercial purpose, any portion of the Site". Under the LawCodex
  rules the site was therefore **not crawled**. Including that corpus would need written
  permission from the Law Commission (Ministry of Justice and Legal Affairs).
- The Labour Act PDF on nia.gov.kn
  (https://nia.gov.kn/cdl_document/labour-act/) is a scan with no text layer. It was not OCR'd
  and is not included.
- Subsidiary legislation (regulations, S.R.O.s) is not included. Where a revised-edition PDF
  bundles subsidiary legislation after the Act, that text is kept as it appears in the PDF.

## Format

One Markdown file per law with YAML front matter (`title`, `identifier`, `type`,
`jurisdiction`, `language`, `status`, `source`, `retrieved`). The text was extracted from the
official PDFs with `pdftotext` (poppler), without OCR, and kept as extracted. Only page
headers, footers and page numbers were removed. CHAPTER/PART/SCHEDULE lines and section
numbers were turned into headings. Some PDFs typeset running headers in margins, so stray
fragments such as "No. 4 of 2010." may appear near the top of a file.

## Licence / copyright

Statutes of Saint Kitts and Nevis are official government texts. The Markdown here reproduces
documents that the Nevis Island Administration publishes for public download on nia.gov.kn.
This is not an official publication. For authoritative text, consult the official Gazette or the
Law Commission.

## Regenerate

```sh
pip install -r scripts/requirements.txt   # plus poppler-utils (pdftotext, pdfinfo)
python3 scripts/kn_fetch.py               # downloads to ../_raw/kn/pdf and writes the Markdown
```

Retrieved: 2026-10-13.
