# Project checkpoint

Repository: https://github.com/william2535/MANUALARCHIVES

## Goal

Build a comprehensive manual archive for a professional offline onsite guide, ordered by fire / security / access control / CCTV, then brand, model/family and document type. Keep continuing useful collection work without repeatedly asking for confirmation.

## Saved progress — 21 October 2026

The archive now contains **3,354 records across 72 brands and 3,038 direct PDF links**. The prepared 309 records were already published. The phone-app data foundation and first October 21 batch are published in `59467f3dca2918cd190e16936fe153c9fc919733`; its fetched tree matched the local checkpoint.

The next batch adds **25 C-TEC manuals/technical references**, resolves all **14 remaining source-only C-TEC entries**, and recovers both older C-TEC failed downloads. Five manufacturer resource tables were inventoried, covering 72 listed entries; three publisher document-number/revision conflicts remain explicit. See `data/continuation-log-2026-10-21-c-tec.json` and `data/source-audits/c-tec-2026-10-21.json`.

All 310 other failed links were rechecked: **272 now return indexed PDFs**, leaving **38 unresolved retrievals**. The remaining outcomes comprise 10 service size limits, 19 HTML verification pages, eight inaccessible responses and one unsupported content type. These results are not proof of missing publisher files. Exact URLs and results are in `data/source-audits/failed-retrievals-2026-10-21.json`. Historical retrieval evidence is retained.

There are **316 records without direct PDF links**: 235 web manuals, four viewers and 77 unresolved listings. These are separate from failed PDF retrievals. Original IDs, source/download URLs and model associations are preserved. The archive retains **130 complete-file checks and 271 further recorded file hashes**. No new local byte counts or checksums are claimed in this pass: local requests failed upstream; retrieval-service page counts are recorded separately. The bulk retry did not reverify identity, applicability or edition.

The phone-app foundation includes `data/app-manifest.json`, its JSON Schema, `APP_INTEGRATION.md`, and a generated `data/gap-audit.json` covering every indexed record and model association. The browser filters download evidence; the local downloader compares known checksums and retains changed versions. Source dates remain attached to their original checks. Manufacturer metadata conflicts and possible duplicates now appear in the gap audit.

Validation: catalogue, model navigation, embedded browser data and both generated app feeds passed; all **18 downloader/feed/date tests passed**. A native phone app and persistent device storage still need implementation and real-device testing. The archive supplies source links and evidence, not hosted PDF binaries.

## Earlier progress — 16 October 2026

Resumed collection checkpoint: **45 more complete-PDF records**, bringing the archive to **3,326 records across 72 brands**. Added Dahua 7, Hikvision 13, Siemens 16, TDSi 4, FireClass 4 and Salto 1. TDSi **UM0120 Issue 2** and the **FC600 installation/user manuals, version 3.0** are now present. Original IDs, source URLs and models were preserved; duplicate hashes were merged. See `data/continuation-log-2026-10-16-b.json`. Kentec and C-TEC collection continues after this checkpoint.

The prepared **309 records are published on main**, in commit `fff64dc8668ebd6f78c30e39d275eec6697c4b35`. The connected GitHub app was used because command-line Git has read access but no push credentials. The local checkpoint branch `checkpoint/prepared-309-local` preserves the equivalent original local commit.

The gap-fill batch is published on main in commit `0714ba5637df3b1a9c84e23fba50ac47d254137f`. It adds **70 records**, taking the catalogue to **3,281 records across 72 brands**: Advanced 22, Hochiki 16, FireClass 9, TDSi 9, Siemens 5, Kentec 4, C-TEC 3 and Protec 2. Every addition was retrieved as a complete PDF, parsed for page count and SHA-256 hashed. Three duplicate candidates were merged and all previous record IDs retained. See `data/gap-fill-log-2026-10-16.json` for exact additions, sources, duplicates and held candidates.

Protec 6300 installation is now present as **93-509-09 Issue 2 Rev 2**. That batch's TDSi additions were controller/PSU/extension datasheets; UM0120 was subsequently resolved in the 45-record batch. The Bosch MAP 5000 download still failed. Older Kentec issues were retained separately from unresolved manufacturer listings. Two misleading Advanced files were held for review instead of indexed under incorrect identities.

Validation for both batches: catalogue/model navigation/offline embedded index checks passed, and all nine downloader tests passed. Both published batch trees were fetched and verified against the local files. The local checkpoint branch `checkpoint/gap-fill-70-local` preserves the original local gap-fill commit; main is aligned with GitHub.

### Earlier prepared-batch checkpoint

The catalogue contains **3,211 records across 70 brands**. This checkpoint adds **309 records** to the previous published total of 2,902: Apollo 174, Nittan 82, Bosch 47, Protec 3, Dahua 3. The new batch includes 257 records with PDF retrieval page-count evidence, 48 listed PDF links and four explicitly failed retrievals. Shared document URLs have one record with multiple model associations. All earlier record IDs are retained.

Read `data/continuation-log.json`, `COVERAGE.md`, `data/coverage-audit.json` and `data/research-backlog.json` for exact sources and remaining gaps. A failed link is not a confirmed working download.

The public repository stores source links and metadata, not manufacturer PDF binaries. `scripts/download.py` downloads PDFs locally for offline use and records checksums. `index.html` searches the catalogue offline; documents must be downloaded before onsite offline use.

## Next work

1. Start from the current GitHub main branch; inspect status and preserve any newer changes. Do not rerun older scratch merge scripts blindly.
2. Use `data/gap-audit.json` for every indexed record's download/metadata flags and model/type coverage. Continue the manufacturer inventory research in `data/research-backlog.json`; the automated audit cannot discover products absent from the catalogue. Priorities include remaining Kentec links and C-TEC metadata conflicts, Bosch MAP 5000, Advanced MxPro editions, Hochiki devices, current Hikvision/Dahua, Comelit pagination, further TDSi editions and current Salto software guides. Full English FC360 technical manuals from a verified source and further FireClass editions remain gaps.
3. Prefer manufacturer sources; label public installer/distributor copies, retain actual model and version evidence, and do not invent download URLs or call unknown editions current.
4. Rebuild with `python3 scripts/build_index.py`, run `python3 scripts/validate.py` and all tests, and publish useful additions to this repository. Keep original source-check dates; only date newly checked evidence. Both app feeds rebuild with the catalogue. Avoid prolonged research without saving additions.
5. To publish through the connected GitHub app, create a tree from the current main tree plus changed file contents, create its commit with the current main as parent, then update main with `force=false` and the expected head SHA. Verify remote/local tree equality before aligning the local branch. Do not force-push. PDF binaries stay local and excluded from Git.

The broader FESS onsite app is separate from this archive. This pass changed only MANUALARCHIVES.
