# Project checkpoint

Repository: https://github.com/william2535/MANUALARCHIVES

## Goal

Build a comprehensive manual archive for a professional offline onsite guide, ordered by fire / security / access control / CCTV, then brand, model/family and document type. Keep continuing useful collection work without repeatedly asking for confirmation.

## Saved progress — 16 October 2026

The catalogue contains **3,211 records across 70 brands**. This checkpoint adds **309 records** to the previous published total of 2,902: Apollo 174, Nittan 82, Bosch 47, Protec 3, Dahua 3. The new batch includes 257 records with PDF retrieval page-count evidence, 48 listed PDF links and four explicitly failed retrievals. Shared document URLs have one record with multiple model associations. All earlier record IDs are retained.

Read `data/continuation-log.json`, `COVERAGE.md`, `data/coverage-audit.json` and `data/research-backlog.json` for exact sources and remaining gaps. A failed link is not a confirmed working download.

The public repository stores source links and metadata, not manufacturer PDF binaries. `scripts/download.py` downloads PDFs locally for offline use and records checksums. `index.html` searches the catalogue offline; documents must be downloaded before onsite offline use.

## Next work

1. Start from the current GitHub main branch; inspect status and preserve any newer changes. Do not rerun older scratch merge scripts blindly.
2. Resolve the remaining identified links and collect missing model/revision families. Priorities include C-TEC/Kentec unresolved links, Bosch MAP 5000 (identified URL currently fails), Protec 6300 installation, Advanced MxPro, Hochiki devices, current Hikvision/Dahua, Comelit pagination, TDSi hardware and Salto software. Siemens and FireClass were researched briefly but no manuals from those searches were added.
3. Prefer manufacturer sources; label public installer/distributor copies, retain actual model and version evidence, and do not invent download URLs or call unknown editions current.
4. Rebuild with `python3 scripts/build_index.py`, run `python3 scripts/validate.py`, and publish useful additions to this repository. Avoid prolonged research without saving additions.

The broader FESS onsite app is separate from this archive. This pass changed only MANUALARCHIVES.
