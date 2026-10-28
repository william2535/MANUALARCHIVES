# Phone app integration

The archive supplies the catalogue and original download sources. A phone app can browse **system → brand → model → document**, download selected manuals, and keep them on the device for offline use. The repository currently includes an offline catalogue browser and a desktop downloader; it does not yet include a native phone app.

## Stable feeds

| Feed | Purpose |
|---|---|
| [app-manifest.json](data/app-manifest.json) | Versioned, app-facing catalogue and download evidence |
| [app-manifest.schema.json](data/app-manifest.schema.json) | JSON Schema for manifest version 1 |
| [catalogue.json](data/catalogue.json) | Full research record, provenance and alternate sources |
| [gap-audit.json](data/gap-audit.json) | Every indexed record's review flags, brand counts and model/type coverage |
| [standards.json](data/standards.json) | Independent British Standards register, revision notes and publisher links |
| [standards.schema.json](data/standards.schema.json) | JSON Schema for standards register version 1 |
| [research-backlog.json](data/research-backlog.json) | Further source discovery and known missing families |

Live manifest URL:

```
https://raw.githubusercontent.com/william2535/MANUALARCHIVES/main/data/app-manifest.json
```

For a reproducible release, replace `main` with a published commit SHA. Fetch the feed over HTTPS and keep the last valid copy locally. Honour HTTP caching headers when available. Reject unsupported `schema_version` values and malformed responses without discarding the saved catalogue. `catalogue_sha256` fingerprints canonical catalogue JSON; it is a change identifier, not a signature or a PDF checksum. Its encoding is UTF-8, JSON keys sorted, no insignificant whitespace, and non-ASCII characters unescaped.

Use `id` as the durable bookmark and download key. Keep every `models` association; several models can share one PDF. Store a downloaded version under both its record ID and full SHA-256. Never use a model-folder slug as a document identity. A feed update must not delete local PDFs or bookmarks, including when a record disappears from a newer feed.

`generated_on` is the catalogue build date. Each record retains its own `source_checked` date; `download.verification.checked_on` dates the recorded file evidence. Rebuilding the feed does not recheck every source.

Category values now include `other-reference` (building controls and supporting references from the full FACP collection) and `warden-call` (warden call, telecare and related nurse call); source provenance includes `archive` for independent collections such as FACP Manuals. Consumers with fixed enum lists must use the updated version-1 schema and support these added values. Keep US rescue-assistance documents and UK social-alarm equipment distinguishable by the actual title, model and source; a shared archive is not evidence of interchangeability.

## Download contract

`download.mode` is one of:

| Mode | App action |
|---|---|
| `direct-pdf` | Attempt `download.url`; validate the returned bytes before saving |
| `resolve-pdf-export` | Resolve the named exporter from the exact `source_page_url`; currently `axis-manual-pdf` only |
| `source-page` | Open the original page; do not download HTML and rename it `.pdf` |

`download.status` describes source evidence, never device storage:

| Status | Meaning |
|---|---|
| `complete-file` | Recorded SHA-256 and size with PDF header and EOF validation |
| `file-hash` | Recorded checksum and size; the full PDF validation trail is incomplete |
| `pdf-indexed` | A retrieval service identified the PDF and page count; no complete local-file check is implied |
| `pdf-header` | Header checked; complete file not established |
| `listed` | Direct URL identified; successful PDF retrieval not established |
| `retrieval-failed` | A recorded retrieval needs attention; older checksum evidence can still be retained |
| `source-page` | No direct download established |

Unknown byte counts and hashes are `null`, not zero. A PDF's `page_count` is not proof that a phone has downloaded it. Source URLs can change, redirect, expire or return a challenge page. `verified_revision` is an issue actually read in a document where explicitly recorded. `revision_hint` and `revision_basis` retain the original research detail; do not label hints or unknown editions “latest”.

An optional `duplicate_of` preserves an earlier record ID when two listings are confirmed to link to the same PDF. Keep both IDs usable for bookmarks, but resolve the reference before queuing or storing a download. Store one file under the canonical ID; the command-line downloader also does this, including when selecting an older ID. References are one hop only and must match the canonical record's brand, category and direct PDF URL. Missing targets, chains, cycles and conflicting known file hashes are rejected by validation. Counts remain catalogue records, so duplicate listings are not additional unique PDFs. `possible_duplicate_of` in the source catalogue is an unresolved review flag and must never be used for automatic deduplication.

## Save and open offline

1. Let the user select documents or a model pack. Show known byte totals separately from files of unknown size. Provide progress, cancellation and a storage limit.
2. Download to a temporary file using the platform's networking API. Follow ordinary public HTTP(S) redirects. Record the final URL, response status and actual byte count. Treat HTML, sign-in pages and unsuccessful responses as failures.
3. Require a PDF header and EOF marker, enforce the configured size limit, calculate SHA-256, and open the result with the PDF renderer. A parser/open failure must not become “saved offline”.
4. Compare actual size and SHA-256 with the manifest when known. If they differ, retain the existing version and mark the new file **source changed — review edition**. If no expected checksum exists, record the calculated hash but label the source match unverified.
5. Move the validated file into persistent app-managed document storage. Commit its local database entry only after the file move succeeds. Keep its title, issue, models, source and checksum with it. Use a separate export/share action for user-managed files.
6. Open the local file when offline. Recheck its existence before showing **saved on this phone**. Keep metadata and search available without a network connection. Deleting a download should remove only the chosen local copy.

Suggested local fields: `record_id`, `sha256`, `bytes`, `local_uri`, `downloaded_at`, `requested_url`, `resolved_url`, `catalogue_sha256`, `catalogue_match`, `record_snapshot`, and `state`. Suggested states: `queued`, `downloading`, `saved`, `failed`, `needs-review`, `missing-file`. Interrupted downloads stay outside `saved`. The archive feed contains none of these device-local states.

[scripts/download.py](scripts/download.py) demonstrates file validation, checksum comparison, content-addressed filenames and retained versions. It is a Python reference tool, not phone application code. It reports changed source contents and keeps both versions when refreshed.

For a native phone app, use persistent file storage with an explicit PDF viewer and download queue. A browser/PWA implementation must also account for cross-origin download restrictions and browser storage eviction; opening a third-party PDF URL does not prove it was cached for offline use. Test the real implementation in airplane mode after an app restart, with an interrupted download, a changed source file, low storage and a removed local file.

Platform references: [Apple background downloads](https://developer.apple.com/documentation/foundation/downloading-files-in-the-background), [Android app-specific storage](https://developer.android.com/training/data-storage/app-specific), [browser CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS), [browser storage quotas and eviction](https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria).

The catalogue links to publisher files; it does not host or license those PDFs. Keep source notices and follow [RIGHTS.md](RIGHTS.md) when downloading or proposing a mirrored archive.

## British Standards register

`data/standards.json` is an independent version-1 feed. Keep it separately from downloadable manufacturer manuals. Its `records` have edition-specific stable IDs, a `standard` family key, an exact `edition`, category, publisher status, source-check date, official source URLs and optional public change summaries. Titles are short subject labels, not necessarily the full formal title.

`publisher_record_date` is exactly the date displayed on the cited BSI record, or `null` if not established. It may be a corrected issue/product date, and can differ from the edition or amendment year. Never turn it into an effective date. `under_review` is independent of `current`/`withdrawn`. `amendments_in_designation` records only explicit A-labels; an empty array is not proof of no amendments or corrigenda. `summary_basis` distinguishes public revision summaries from edition metadata alone.

`earlier_records` preserves the status displayed by the earlier source. BSI can list both earlier and later records as current; do not infer withdrawal. `supersedes` contains only publisher-confirmed predecessors. `transition` is null unless a separately sourced deadline is known. The current register records the IET's 15 October 2026 transition end for BS 7671 A2/A3. Evaluate dates against the feed's check date before showing past/future wording.

Cache the register and search it offline. Keep bookmarks keyed by edition ID, and retain earlier editions when adding revisions. Show the source-check date beside status and keep `coverage.complete` and `history_complete` visible to consumers. The root `checked_on` is the latest register evidence date, not a claim that every row was checked on that date. This is a manually checked snapshot, not an automatic update service or a complete historical register. Pending families and histories are listed in `coverage.remaining_checks`.

Every standard record retains `access: publisher-link-only`. Its `source_url` is a metadata reference and may require payment; never present it as a free download or queue it as a manufacturer PDF. A metadata update must not imply a standard is saved on the phone. The IET requires links to its updates page rather than direct update-PDF links. Full standard texts are not mirrored by this archive.

`free_resources` and `free_resources_checked_on` are optional additions to the version-1 feed. An absent array means no verified free resources. Each resource has a stable ID, `related_standard_ids`, title, publisher, `resource_type` (`full-standard`, `guide`, `white-paper`, `model-forms`), printed `document_issue`, `edition_relation`, `scope_note`, source and direct PDF URLs. Every resource has `access: free-direct-pdf`. Guides, white papers and forms have `is_full_standard: false`; their relationships mean related guidance, not equivalence to the full standard. A `full-standard` resource has `is_full_standard: true` and must match one exact edition record with `edition_relation: same-edition`. Its `edition`, `isbn`, `source_host`, `complete_text_checked`, `completeness_note` and `rights_note` are required. Preserve the linked record’s withdrawn status and never attach an older full copy to a current edition as if they were identical. Preserve scope notes and earlier-edition warnings beside the download action.

Show free PDFs as the primary actions and default to references with a related free resource. Put full standards first and offer **Full standards only**, **All reference records** and **No verified free PDF** filters. Where none is verified, show that state without a download button. Keep publisher purchase links inside clearly labelled source details. Never imply that every reference has a free full-standard PDF. The historical BS 5839-6:2013 resource is a public inquiry exhibit, not Part 1 or the current Part 6 edition.

Free-resource evidence is independent of standard-status evidence: `checked_on`, `verification_method: complete-file`, `sha256`, `bytes`, `page_count`, `pdf_header_checked` and `pdf_eof_checked` describe an anonymously retrieved PDF. Rechecking a guide URL does not recheck a standard’s status or establish its technical currency. Free access does not grant redistribution rights. Only an explicit user download saved to persistent storage makes the PDF available offline. The manuals downloader remains separate; apps may use the free-resource URLs in their own download queue with their titles, scope and source notices retained.

`draft_watchlist` is optional in the version-1 feed. Its entries use a DC reference, subject, publisher record date, check date and source URL. Show these separately as proposals; do not mix them into published-standard counts or infer that consultation remains open. Published PD CEN/TS, PD CLC/TS and DD CLC/TS entries remain explicitly labelled companion documents in `records`; a DD publication is not a DC consultation draft.


## FACP collection provenance

`source_collections` is an optional array; `facp` identifies a catalogue record represented in the complete FACP source inventory. Treat an absent or null value as an empty array. A record can retain manufacturer provenance while also belonging to this collection when a byte-identical FACP mirror was found.

[`data/source-audits/facp-full-2026-10-21.json`](data/source-audits/facp-full-2026-10-21.json) maps every FACP listing UUID and detail URL to a catalogue record. This is the reconciliation contract: source-listing counts can exceed catalogue-record counts when exact duplicates or earlier records are reused. Every listed PDF URL remains available in the audit and, where different from the selected download, in the record's alternate sources.

Imported titles and source-listed years are navigation aids. The FACP `modelNumber` field includes incidental referenced devices and must not be treated as a list of primary compatible models. Imported records leave revision, language and market unverified unless independently established. A complete-file hash does not establish engineering applicability.

Large catalogue and manifest JSON files use one compact record per line. Their JSON structure and version-1 field semantics are unchanged. The source collection is a dated snapshot, not automatic synchronization with FACP.

`document_types` optionally preserves multiple source classifications for a document, such as installation and programming. Fall back to the existing singular `document_type` when absent or null; filters should match any listed type.
