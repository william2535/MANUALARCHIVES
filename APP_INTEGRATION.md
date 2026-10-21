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

Cache the register and search it offline. Keep bookmarks keyed by edition ID, and retain earlier editions when adding revisions. Show the source-check date beside status and keep `coverage.complete` and `history_complete` visible to consumers. This is a manually checked snapshot, not an automatic update service or a complete historical register. Pending families and histories are listed in `coverage.remaining_checks`.

Every entry has `access: publisher-link-only`. Open the official publisher page for licensed access; never queue it as a manufacturer PDF download. A metadata update must not imply a standard is saved on the phone. The IET requires links to its updates page rather than direct update-PDF links. Full standard texts are not mirrored by this archive.

`draft_watchlist` is optional in the version-1 feed. Its entries use a DC reference, subject, publisher record date, check date and source URL. Show these separately as proposals; do not mix them into published-standard counts or infer that consultation remains open. Published PD CEN/TS, PD CLC/TS and DD CLC/TS entries remain explicitly labelled companion documents in `records`; a DD publication is not a DC consultation draft.
