# Adding and correcting records

1. Prefer the manufacturer's original download or an explicitly manufacturer-linked document host. When an older document is only located on a public supplier site, retain that exact source and set `source_kind` to `installer` or `distributor`; use `archive` for an independent manual archive. Never label it a manufacturer source.
2. Open the exact document and check its title, model applicability, issue, language and market where accessible. If only a listing or filename is available, describe that limitation in `model_basis` and `retrieval_note`, and keep unknown fields unverified. A similar model name or a directory date is not sufficient.
3. Add or correct an entry in `data/catalogue.json`. Keep unknown fields null or `not-verified`. `revision_hint` is display metadata; state its evidence in `revision_basis` and populate `verified_revision` only after checking the printed document.
4. Use a separate record for a distinct edition or language. Reuse one record with multiple `models` when the manufacturer explicitly associates the same document with them.
5. Run `python3 scripts/build_index.py`, then `python3 scripts/validate.py` and `python3 -m unittest discover -s tests -v`.

Keep the category keys stable: `fire`, `security`, `access-control`, `cctv`, `warden-call`. The last group covers warden call, telecare and clearly identified related nurse-call systems; standalone rescue assistance stays under fire. Door entry and intercoms live under access control; intrusion and related security equipment live under security. Source PDFs and observations take precedence over inferred folder names. Model folders are navigation aids and do not certify compatibility.

Generated category, brand and model README files should be rebuilt from the JSON, not edited individually. Report broken links by identifying the record ID and source URL. Do not silently replace an older edition with a newer one or label a document “latest” without evidence.

Keep existing record IDs when correcting a URL. Merge records that share an exact source URL, or whose complete files have identical SHA-256 hashes, retaining alternate source URLs and model associations. Similar filenames alone do not establish identical contents or editions. Counts describe catalogue records; unverified mirror copies may still overlap.

Update `data/coverage-audit.json` and `data/research-backlog.json` when resolving gaps. A public PDF link, a PDF header check, a complete-file checksum and a technical applicability review are different levels of evidence. Report them separately.

`generated_on` dates the catalogue build. Preserve older `source_checked` and file-evidence dates for records not rechecked. Record a document's actually inspected issue in `verified_revision`; retain `revision_hint` and its basis. Retrieval-service PDF parsing belongs in `pdf_indexing_evidence` and must not invent a local checksum or byte count.

The build generates `data/app-manifest.json` and `data/gap-audit.json` from the same catalogue. Keep manifest version 1 compatible with `data/app-manifest.schema.json`; see [app integration](APP_INTEGRATION.md). Never put device-local download states, paths or customer selections in the public feed.


## Reconcile the full FACP collection

Use `scripts/collect_facp.py` in a fresh private working directory; it collects the current public brand inventory. Resume in the same directory to reuse successful page and download checks. Start a new directory for a later source snapshot. It reads the site's public listing HTML and checks unique source IDs against every brand total. Titles at pagination boundaries are searched again because FACP's equal-title ordering can repeat one document and omit a sibling. A successfully fetched page is not proof that a brand is complete.

Keep raw source pages, PDFs and extracted text outside Git. `scripts/check_facp_downloads.py` downloads only the publicly listed PDF host, checks the complete bytes and parses each PDF. The cache is resumable and revalidates cached hashes. `scripts/import_facp.py` refuses incomplete or conflicted inventories; it retains every document type and maps every source listing to an existing or new record. Similar titles alone never justify merging files.

The private `scripts/package_facp.py` workflow creates independent ZIP volumes only when every source has a complete-file check. It verifies each archived PDF against the recorded hash. These volumes are for the requesting user's offline files, not a public PDF mirror.

Example commands (paths must point to a private working directory):

```bash
python3 scripts/collect_facp.py --output /path/to/facp-work
python3 scripts/check_facp_downloads.py --workspace /path/to/facp-work --workers 6
python3 scripts/import_facp.py --workspace /path/to/facp-work --checked-on YYYY-MM-DD
# Review the preview and evidence before applying:
python3 scripts/import_facp.py --workspace /path/to/facp-work --checked-on YYYY-MM-DD --apply
python3 scripts/build_index.py
python3 scripts/validate.py
```
