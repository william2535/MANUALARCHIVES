# FESS Manual Archives

Fire, security, access control, CCTV, warden call, telecare and nurse-call manuals and technical references, organised for the FESS onsite guide. This is a growing source catalogue, not a complete collection of every manufacturer or model.

**12,377 document records · 178 brands · 12,135 direct PDF links · 0 PDF files mirrored**

Catalogue build date: 2026-10-28. A check date does not mean a document is the latest revision.
**[New device manuals and category links](DEVICE_COVERAGE.md)** — DTs/PIRs, smokes, sounders, readers, locks, cameras, power supplies and telecare sensors.

## Browse by system

| Category | Documents |
|---|---:|
| [Fire](01-fire/README.md) | 8,794 |
| [Security / intruder](02-security/README.md) | 1,101 |
| [Access control / door entry](03-access-control/README.md) | 992 |
| [CCTV](04-cctv/README.md) | 986 |
| [Warden call / telecare / nurse call](06-warden-call/README.md) | 221 |
| [Building controls / other references](07-other-references/README.md) | 283 |

Each category contains **brand → model / product family → document** navigation. Documents are classified as installation, user guide, programming, quick start, application note, diagram, datasheet or reference. Shared documents are linked under all explicitly associated models without counting each model association as a separate document.

## British Standards: free guides and forms

**13 verified free PDF guides, white papers and model forms**, with direct publisher/author downloads. Links checked 2026-10-28. Search starts with references that have free guides; choose **All reference records** for all 147 standards references across 8 groups. Publisher-status metadata remains dated 2026-10-21.

[Download free standards-related guides](05-british-standards/README.md#free-pdf-downloads) · [Search free guides offline](index.html#standards) · [App data](data/standards.json)

**These are guides and forms, not the full British Standards.** No authorised free full-standard PDFs have been verified. Earlier-edition guidance is marked clearly, and paid publisher records are retained only as labelled source references.

## Complete FACP source collection

All **8,519 public listings across 104 FACP brands** were reconciled against the full brand inventory on 2026-10-21. No document type or non-fire listing was excluded. Exact duplicates and existing records share a catalogue entry while every source listing retains its own audit mapping.

[Collection and brand totals](FACP_COLLECTION.md) · [Exact source-to-record audit](data/source-audits/facp-full-2026-10-21.json)

Select **Collection → FACP Manuals** in the offline browser, or download the collection with:

```bash
python3 scripts/download.py --collection facp --list
python3 scripts/download.py --collection facp
```

This selection includes fire, security, care-call and other references. Add `--category fire` to select the fire section. Source-listed years and titles are retained; the import does not certify the latest edition or UK applicability.

## Search and app data

- Download or clone this repository, then open **`index.html`** in your browser. Its catalogue and search work offline; opening source documents requires a connection until you download them.
- [`data/catalogue.json`](data/catalogue.json) is the structured source for app integration. It contains stable IDs, categories, models, document types, source URLs, direct PDF URLs where found, and availability records.
- [Coverage and gaps](COVERAGE.md) separates confirmed PDF retrieval metadata, published PDF links, online manuals and unresolved sources.

## Phone app foundation

[`data/app-manifest.json`](data/app-manifest.json) is the versioned download feed for a phone app. It keeps stable record IDs, model associations, source provenance, verification dates, file sizes and SHA-256 checksums where known. A direct link alone is not a verified download.

Current evidence: **9,186 complete-file checks**; other records retain their actual evidence level. The feed never claims a manual is saved on a device.

See [app integration](APP_INTEGRATION.md) for the feed contract, download validation, local storage and version retention. The archive remains the catalogue; a phone app must download and retain the selected PDFs before offline use.

[`data/gap-audit.json`](data/gap-audit.json) audits every record and model association, with review flags and counts by brand. It is regenerated with the catalogue.

## Offline downloads

Requires Python 3.10 or later; no extra packages. Download only material you are entitled to use under the publisher’s terms.

Preview a selection:

```bash
python3 scripts/download.py --category fire --brand "C-TEC" --list
```

Download that brand’s available PDFs locally:

```bash
python3 scripts/download.py --category fire --brand "C-TEC"
python3 scripts/download.py --category security --brand Texecom
python3 scripts/download.py --category access-control --brand Paxton
python3 scripts/download.py --category cctv --brand Axis --model P3245
python3 scripts/download.py --category warden-call --brand Tynetec
```

Use `--limit 5` for a small first batch. `--all` selects the whole catalogue and can download many GB. `--refresh` checks the selected sources again; changed contents get a separate file, retaining old versions.

Files go into `downloads/category/brand/model/`. The gitignored `downloads/download-manifest.json` records source URLs, download time, exact byte counts, SHA-256 checksums, results and retained version history. Interrupted or non-PDF responses are removed. Source-only entries, login pages and blocked requests are reported for manual attention. The tool can resolve Axis’s explicit PDF export from its model manual page.

A successful download checks the file header, trailer and integrity; it does not certify technical applicability. Open each required PDF and check it before going on site.

## What is stored here

The repository stores original indexing work and links. Manufacturer sources are preferred; public installer, distributor and independent archive copies are labelled separately with `source_kind`. Some legacy titles and model associations come from abbreviated filenames and need document-level review. It does **not** republish copyrighted manufacturer PDFs. Publicly accessible downloads do not themselves establish permission to redistribute. See [document rights](RIGHTS.md).

This archive includes older editions and multiple languages. Unknown language, market or revision information stays explicitly unverified. Engineering manuals, application notes and datasheets are not interchangeable. No passwords, default-code lists, customer records or paid standards have been extracted into the catalogue.

## Maintain the archive

```bash
python3 scripts/build_index.py
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
node tests/test_browser.cjs
```

See [contribution guidance](CONTRIBUTING.md).
