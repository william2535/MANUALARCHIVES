# Project status

## Complete FACP collection — 21 October 2026

All **8,519 public FACP listings across 104 source brands** are now represented in the archive, with **8,519 successful complete-PDF downloads**. The collection includes manuals, older editions, datasheets, catalogue pages, brochures and non-fire references. Every source UUID, detail page and PDF URL maps to a catalogue record; nothing from the public brand inventory was excluded.

The update adds **8,507 records** and links **12 existing records**, preserving all **3,555 earlier IDs, titles, model associations and original URLs**. The full archive now has **12,062 records across 174 brands**, **11,820 direct PDF references** and **8,874 complete-file catalogue checks**. Source checks and catalogue evidence counts differ when an existing manufacturer record is retained and its FACP mirror is separately checked.

The importer reconciled 428 primary listing pages and 17 supplemental title-search pages. Equal-title pagination had omitted 11 documents; those were recovered before import. The source sitemap includes one renamed URL that redirects to a collected entry and omits two current listing URLs. Exact reconciliation is recorded in `data/source-audits/facp-inventory-reconciliation-2026-10-21.json`.

Select **Collection → FACP Manuals** in the offline browser, or use `python3 scripts/download.py --collection facp`. A new building-controls/other-references category retains non-fire material. Multi-purpose documents retain each source type; plus variants have separate navigation folders. The downloader accepts the collection's large scanned manuals. The public repository contains links and metadata, while downloaded PDFs are packaged separately for private offline use.

All source PDFs have SHA-256, actual byte count, header/EOF and Poppler page-count evidence. FACP's listed size differs from delivered bytes for 8,377 records; the catalogue uses the measured size, retaining the source-listed value in the audit. A repeat download sample returned the same measured hash and size. Source-listed years are not verified editions, and referenced component lists are not treated as primary compatible models.

The British Standards register remains at **147 checked references**. The earlier non-FACP link barriers remain explicit: three Kentec listings, four CDVI viewers and ten failed PDF retrievals. This import is complete against FACP's dated public brand inventory, not every manufacturer publication in existence. The native phone application remains separate from the catalogue and offline download tools.

Validation: 45 Python tests, catalogue/source reconciliation, preservation checks, offline browser logic and Git whitespace checks. No real-device app test is claimed.

# Project checkpoint

Repository: https://github.com/william2535/MANUALARCHIVES

## Goal

Build a comprehensive manual archive for a professional offline onsite guide, ordered by fire / security / access control / CCTV / warden call and telecare, then brand, model/family and document type. Keep continuing useful collection work without repeatedly asking for confirmation.

## Latest completed continuation — warden call and FACP downloads, 21 October 2026

Added **124 distinct, fully downloaded PDFs**, taking the archive to **3,555 records, 92 brands and 3,313 direct PDF references**. The new warden call / telecare / nurse-call category contains 120 records; four rescue-assistance references remain separately under fire. New records: Tynetec 84, Tunstall 28, Cornell Communications 10, Jeron 1 and CSL 1.

All 11 Cornell/Jeron documents on the checked FACP pages downloaded successfully. Tynetec was absent from the checked FACP brand list, so Advent XT, XT2 and Reach-family documents came from Tynetec's own public libraries. Tunstall grouped-living resources include Communicall Digital version 1.4 (printed 30 July 2026), Connect, Vision, Vi IP and related guides. Three byte-identical alternate URLs were merged. Distinct legacy files and unresolved issue marks remain explicit. A mislabelled Cornell PSU listing was corrected against its actual PDF heading; Tunstall PBX/model/cover conflicts are retained.

The public repository contains metadata and source links. Separate download packs contain the retrieved PDFs with filenames and checksums. The app feed records **367 complete-file checks** and does not claim these files are saved on a phone.

The standards register has **147 references across eight groups**, including a dedicated social-alarm group with six existing BS EN 50134 / PD CLC/TS references and newly checked BS 8521-2:2020. Full licensed standard texts and complete revision histories are not included.

Scope limits: FACP collection covered Cornell/Jeron care and rescue documents, not the whole site. TeleAlarm's old TA74 PDF now redirects to an HTML download centre and was not added as a working PDF. Reach IP 4G, Aidcall, Careium, Ascom and Jontek remain documented research gaps. Existing Kentec/CDVI and ten earlier PDF retrieval barriers are unchanged. See `data/source-audits/warden-call-2026-10-21.json` and `data/source-audits/facp-manuals-2026-10-21.json`.

Validation: catalogue/generated-data consistency, Python unit tests and offline browser logic are checked for this update. No real-device offline test or full JSON Schema runtime validation is claimed.

## Earlier continuation — 21 October 2026

The archive has **3,431 manual/reference records across 87 brands and 3,189 direct PDF references**. This continuation resolves **50 previously source-only Kentec listings to 49 distinct PDF URLs**, corrects document titles/numbers and records readable printed issues. The Man-1099 duplicate keeps both stable IDs; an explicit `duplicate_of` reference makes the downloader save one copy, including when selected through the older ID. Counts are catalogue references, not a guarantee of unique file contents.

The MIOU manual and a recovered **24-page Paxton ins-20603 distributor copy** have complete-file hashes, sizes, header/EOF and PDF-parser evidence. Other recovered Kentec files retain retrieval-service evidence without claiming complete local-file checks. Man-1494 now has its publisher-published download URL, but retrieval remains unsuccessful. All 3,431 prior IDs and model associations are preserved.

The requested British Standards section remains published with **146 checked references**, 28 amended designations, 25 public revision summaries, 24 earlier publisher records and four separate consultation drafts. It is a dated, source-linked register; complete BS histories and licensed full texts are not claimed.

The remaining link barriers are individually recorded: **three Kentec source-only listings**, **four CDVI public viewers reporting download disabled**, and **ten failed PDF retrievals** (nine earlier failures plus newly identified Man-1494). Another 235 entries are valid online manuals. The eight unresolved supplier candidates retain their identity/file-quality explanations. See `data/source-audits/kentec-legacy-2026-10-21.json`, `data/source-audits/paxton-20603-recovery-2026-10-21.json`, `data/source-audits/cdvi-viewers-2026-10-21.json` and the refreshed research backlog.

Validation: **33 Python tests**, catalogue/generated-data consistency, offline JavaScript logic, preservation of previous IDs/models/source links and Git whitespace checks passed. The browser checks include duplicate labels and printed-issue display. No real-browser/mobile visual or persistent-phone-storage test is claimed; the native application remains separate from this archive and app feed.

## Previous completed archive update — 21 October 2026

The archive now contains **3,431 manual/reference records across 87 brands, with 3,138 direct PDF links**. This continuation adds **69 records** (39 reviewed supplier documents and 30 distinct manufacturer-hosted FFE guides), enriches existing records, recovers **28 of the 38 failed PDF retrievals**, and restores the manufacturer PDF for the existing Apollo XPander commissioning guide. All 3,362 earlier record IDs are preserved.

The British Standards section now contains **146 checked references**, **28 amended designations**, **25 public revision summaries**, **24 earlier publisher records** and a separate **four-entry consultation draft watchlist**. The expansion covers additional fire detector/application, intruder, intercom, access protocol, video protocol, cabling, social alarm, gas suppression, sprinkler, extinguisher and powered-entrance references. New 2026 intercom, bonding and sprinkler editions retain the earlier publisher statuses rather than assuming withdrawal. PD/DD technical specifications are explicitly distinguished from consultation drafts.

All **67 previously unclassified supplier candidates have been reviewed**: 39 new records, ten existing records enriched, nine duplicate source links retained, one misleading non-manual rejected and eight candidates left unresolved with specific identity/file-quality reasons. Of 35 checked FFE resource links, 30 contain distinct complete PDFs; the remaining five are byte-identical alternate paths. See `data/supplier-candidate-audit.json`, `data/source-audits/ffe-2026-10-21.json` and `data/source-audits/retrieval-retries-2026-10-21.json`.

Validation: **29 Python tests**, catalogue/generated-data consistency, offline JavaScript UI checks, preservation of earlier IDs and Git whitespace checks passed. The UI checks exercise both sections, draft separation, search, category/status filters, pagination, empty results and transition evidence. A real-browser/mobile visual and persistent-phone-storage check has not run; this repository supplies the archive and app data, not a finished native app.

Remaining source barriers are explicit: **ten failed PDF retrievals**, **54 Kentec listings and four CDVI viewers without direct PDFs**, plus the **eight reviewed supplier candidates**. Another **235 entries are valid online manuals**, not failed PDF downloads. The larger manufacturer inventory and complete British Standards histories cannot be declared exhaustive from the available public evidence. The standards register is a dated snapshot, without automatic monitoring.

## Previous addition — British Standards, 21 October 2026

The new `05-british-standards/README.md` section and `index.html#standards` browser view contain **93 checked references across seven subjects**, **20 amended designations**, **11 public revision summaries** and **15 earlier publisher records**. Sources are BSI public product records and the IET's own BS 7671 update/transition information. `data/standards.json` is the independent phone-app feed, with `data/standards.schema.json` and integration notes.

Recent entries include BS 5839-1:2025, BS 5266-1:2025, BS EN 50131-3:2026, BS EN IEC 62676-4:2025, BS EN IEC 62676-6:2026 and BS 7671:2018+A4:2026. The IET-confirmed 15 October 2026 A2/A3 transition end is recorded separately from publication dates. The section also includes relevant EN/IEC adoptions and clearly labelled PD 6662/6669 companion documents. Licensed standard PDFs are not mirrored or queued by the manual downloader.

Coverage remains explicitly partial: this is not every British Standard or a complete amendment/corrigendum history. Detailed revision summaries are present only where public publisher evidence was checked. BSI record dates are preserved even where they differ from edition years. Earlier pages that still report current status remain visible; withdrawal or coexistence deadlines are not inferred. `coverage.remaining_checks` lists remaining families and histories.

Validation: all **26 Python tests** passed, along with catalogue/standards consistency and offline JavaScript UI logic checks for deep links, search, filters, pagination, empty results, transition evidence and preservation of the manuals view. The existing **3,362 manuals, 72 brands and 3,068 direct PDF links** remain unchanged. A real-browser/mobile visual check could not run because this environment has no browser executable; real-device and native-phone-storage testing remain outstanding. The register is a manually checked snapshot, with no automatic monitoring.

## Previous checkpoint — 21 October 2026

The archive contains **3,362 records across 72 brands and 3,068 direct PDF links**. This continuation adds **eight documents** (seven Kentec lockdown-device guides and the correctly identified Sigma ZSi DS145 datasheet), resolves **22 existing source-only Kentec entries**, and enriches the existing Syncro networking manual. All earlier record IDs, model associations, source URLs, download URLs and complete-file evidence are retained.

The batch checks manufacturer product pages and the actual PDF titles, printed revisions and page counts. It records **three publisher link/number conflicts**: Man-1200 currently links to a PNG cover; a Man-1453 product-page link supplies DS145; and a Man-1252 link supplies the already indexed MAN-1252KE. These are flagged rather than presented as resolved manual downloads. The original Man-1453 manual and unqualified Man-1252 listing still need review. See `data/continuation-log-2026-10-21-kentec.json` and `data/source-audits/kentec-2026-10-21.json`.

There are now **294 records without direct PDF links**, including **54 Kentec entries**. The previous 38 unresolved PDF retrievals remain separate. No new local byte counts or checksums are claimed: this batch has retrieval-service PDF evidence. The browser index, brand/model navigation, phone-app feed and gap audit were rebuilt; catalogue validation and **all 18 tests passed**. The native phone app and persistent phone storage still need implementation and device testing.

Publication verified: the Kentec continuation is on GitHub main as `4ca5d866195788257daa29cfa183ffdb5cb7f453`. Its fetched Git tree matches all 78 changed local files. The earlier C-TEC/retrieval-audit batch is published as `f5d2af911495fe039eac9508e11f6916f124cc8b`. The local branch is aligned with the published work.

## Earlier checkpoint — 21 October 2026

At this earlier checkpoint the archive contained **3,354 records across 72 brands and 3,038 direct PDF links**. The prepared 309 records were already published. The phone-app data foundation and first October 21 batch are published in `59467f3dca2918cd190e16936fe153c9fc919733`; its fetched tree matched the local checkpoint.

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
5. To publish through the connected GitHub app, upload large changed files individually with `create_blob`, compare each returned SHA with its local Git blob hash, and use those SHAs in a small `create_tree` request based on the current main tree. The tool gateway rejects requests over 16 MiB, including JSON encoding overhead; sending the full catalogue, app feed, audit and browser together exceeded that limit. Create the commit with current main as parent, then update main with `force=false` and the expected head SHA. Verify remote/local tree equality before aligning the local branch. Do not force-push. PDF binaries stay local and excluded from Git.

The broader FESS onsite app is separate from this archive. This pass changed only MANUALARCHIVES.
