# Project checkpoint

Repository: https://github.com/william2535/MANUALARCHIVES

## Goal

Build a comprehensive manual archive for a professional offline onsite guide, ordered by fire / security / access control / CCTV, then brand, model/family and document type. Keep continuing useful collection work without repeatedly asking for confirmation.

## Saved progress — 16 October 2026

The prepared **309 records are published on main**, in commit `fff64dc8668ebd6f78c30e39d275eec6697c4b35`. The connected GitHub app was used because command-line Git has read access but no push credentials. The local checkpoint branch `checkpoint/prepared-309-local` preserves the equivalent original local commit.

The gap-fill batch is published on main in commit `0714ba5637df3b1a9c84e23fba50ac47d254137f`. It adds **70 records**, taking the catalogue to **3,281 records across 72 brands**: Advanced 22, Hochiki 16, FireClass 9, TDSi 9, Siemens 5, Kentec 4, C-TEC 3 and Protec 2. Every addition was retrieved as a complete PDF, parsed for page count and SHA-256 hashed. Three duplicate candidates were merged and all previous record IDs retained. See `data/gap-fill-log-2026-10-16.json` for exact additions, sources, duplicates and held candidates.

Protec 6300 installation is now present as **93-509-09 Issue 2 Rev 2**. TDSi additions are controller/PSU/extension datasheets; UM0120 installation instructions remain unresolved. The Bosch MAP 5000 download still failed. Older Kentec issues were retained separately from unresolved manufacturer listings. Two misleading Advanced files were held for review instead of indexed under incorrect identities.

Validation for both batches: catalogue/model navigation/offline embedded index checks passed, and all nine downloader tests passed. Both published batch trees were fetched and verified against the local files. The local checkpoint branch `checkpoint/gap-fill-70-local` preserves the original local gap-fill commit; main is aligned with GitHub.

### Earlier prepared-batch checkpoint

The catalogue contains **3,211 records across 70 brands**. This checkpoint adds **309 records** to the previous published total of 2,902: Apollo 174, Nittan 82, Bosch 47, Protec 3, Dahua 3. The new batch includes 257 records with PDF retrieval page-count evidence, 48 listed PDF links and four explicitly failed retrievals. Shared document URLs have one record with multiple model associations. All earlier record IDs are retained.

Read `data/continuation-log.json`, `COVERAGE.md`, `data/coverage-audit.json` and `data/research-backlog.json` for exact sources and remaining gaps. A failed link is not a confirmed working download.

The public repository stores source links and metadata, not manufacturer PDF binaries. `scripts/download.py` downloads PDFs locally for offline use and records checksums. `index.html` searches the catalogue offline; documents must be downloaded before onsite offline use.

## Next work

1. Start from the current GitHub main branch; inspect status and preserve any newer changes. Do not rerun older scratch merge scripts blindly.
2. Resolve the remaining identified links and collect missing model/revision families. Priorities include C-TEC/Kentec unresolved links, Bosch MAP 5000 (identified URL still fails), newer Advanced MxPro editions, further Hochiki devices, current Hikvision/Dahua, Comelit pagination, TDSi UM0120 hardware instructions and Salto software. Siemens and FireClass now have initial records; full English FC360 technical and FireClass FC600 installation/user manuals remain gaps.
3. Prefer manufacturer sources; label public installer/distributor copies, retain actual model and version evidence, and do not invent download URLs or call unknown editions current.
4. Rebuild with `python3 scripts/build_index.py`, run `python3 scripts/validate.py`, and publish useful additions to this repository. Avoid prolonged research without saving additions.
5. To publish through the connected GitHub app, create a tree from the current main tree plus changed file contents, create its commit with the current main as parent, then update main with `force=false` and the expected head SHA. Verify remote/local tree equality before aligning the local branch. Do not force-push. PDF binaries stay local and excluded from Git.

The broader FESS onsite app is separate from this archive. This pass changed only MANUALARCHIVES.
