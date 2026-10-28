# Device documentation additions

[Archive](README.md) · [Coverage and gaps](COVERAGE.md)

Checked 28 October 2026: **314 additional document records**, taking the catalogue to **12,377 records**. **311 have complete-file checks**; three Orisec originals have remotely checked PDF identity but their full downloads returned HTTP 403. Document counts are not unique-device counts; shared manuals appear under each verified model association.

## Start with the devices

- **DTs and PIRs:** [Pyronix KX series](02-security/pyronix/README.md), [Bosch TriTech](02-security/bosch/README.md), [Honeywell](02-security/honeywell/README.md), [Optex RXC](02-security/optex/README.md), [Risco iWISE / BWare](02-security/risco/README.md), [Orisec DT-200](02-security/orisec/README.md).
- **Smokes, heat and CO:** [Aico / Ei Electronics](01-fire/aico/README.md) and [Protec detectors and bases](01-fire/protec/README.md).
- **Readers and door hardware:** [TDSi](03-access-control/tdsi/README.md), [CDVI](03-access-control/cdvi/README.md) and [RGL](03-access-control/rgl/README.md).
- **Cameras:** [Dahua](04-cctv/dahua/README.md) and [Hikvision](04-cctv/hikvision/README.md).
- **Telecare devices:** [Tynetec](06-warden-call/tynetec/README.md) and [Tunstall](06-warden-call/tunstall/README.md).
- **Power supplies:** [Elmdene fire supplies](01-fire/elmdene/README.md) and [other Elmdene supplies](07-other-references/elmdene/README.md).

## Additions by category

| Category | Added documents | Included device families |
|---|---:|---|
| [Fire](01-fire/README.md) | 107 | Aico smoke/heat/CO alarms and accessories; Protec detectors, bases, call points, sounders/VADs and interfaces; Elmdene fire PSUs |
| [Security / intruder](02-security/README.md) | 28 | Bosch TriTech, Honeywell DT8000/IS3000, Pyronix KX detectors and Deltabell-WE, Risco iWISE/BWare, Optex RXC and Orisec DT-200 instructions |
| [Access control / door entry](03-access-control/README.md) | 44 | TDSi and CDVI readers; RGL maglocks, bolts, strikes, handles, brackets and exit buttons |
| [CCTV](04-cctv/README.md) | 13 | Dahua and Hikvision camera datasheets, installation, quick-start and configuration guides |
| [Warden call / telecare / nurse call](06-warden-call/README.md) | 100 | Tynetec and Tunstall pendants, PIRs, fall/smoke/heat/CO/flood sensors, contacts and occupancy devices |
| [Building controls / other references](07-other-references/README.md) | 22 | Elmdene power supplies, battery boxes and supporting modules |

## Additions by brand

| Brand | Added documents |
|---|---:|
| Aico — [Fire](01-fire/aico/README.md) | 39 |
| Bosch — [Security / intruder](02-security/bosch/README.md) | 4 |
| CDVI — [Access control / door entry](03-access-control/cdvi/README.md) | 1 |
| Dahua — [CCTV](04-cctv/dahua/README.md) | 9 |
| Elmdene — [Fire](01-fire/elmdene/README.md) / [Building controls / other references](07-other-references/elmdene/README.md) | 40 |
| Hikvision — [CCTV](04-cctv/hikvision/README.md) | 4 |
| Honeywell — [Security / intruder](02-security/honeywell/README.md) | 2 |
| Optex — [Security / intruder](02-security/optex/README.md) | 8 |
| Orisec — [Security / intruder](02-security/orisec/README.md) | 3 |
| Protec — [Fire](01-fire/protec/README.md) | 50 |
| Pyronix — [Security / intruder](02-security/pyronix/README.md) | 9 |
| RGL — [Access control / door entry](03-access-control/rgl/README.md) | 28 |
| Risco — [Security / intruder](02-security/risco/README.md) | 2 |
| TDSi — [Access control / door entry](03-access-control/tdsi/README.md) | 15 |
| Tunstall — [Warden call / telecare / nurse call](06-warden-call/tunstall/README.md) | 35 |
| Tynetec — [Warden call / telecare / nurse call](06-warden-call/tynetec/README.md) | 65 |

## Verification and retained editions

Complete-file checks include a SHA-256 checksum, actual byte count, header/EOF and PDF page count. Printed title/model information was checked using extracted text or rendered pages. Manufacturer sources are preferred; supplier-hosted originals are labelled. These checks do not establish the latest edition or technical suitability for a particular installation.

The three Orisec DT-200, DT-200-PET and DT-200-AM INCERT instructions are explicitly marked `retrieval-failed`: the original PDFs were readable through the retrieval service, but complete-file download attempts returned HTTP 403. They are not included in the 311 fully checked additions.

Different Aico Ei140e/Ei603/Ei605 and Optex RXC-DT editions remain separate. Byte-identical shared documents are merged with their models and source associations. Inconsistent source labels are recorded: for example the Optex RXC-DT page points to RXC-RDT, and one RGL G-EBGB listing points to EBGBWC02. The catalogue uses the actual primary model shown in each PDF.

The offline `index.html` search and app feed are rebuilt from the same records. Search a model such as `KX10DTP`, `DT-200`, `Ei3030`, `RXC-DT`, `6000PLUS`, `ML600` or a Tynetec product code.

## Existing device coverage

The archive already includes [Texecom Capture and legacy Premier detector manuals](02-security/texecom/README.md), [Apollo devices](01-fire/apollo/README.md), [Hochiki devices](01-fire/hochiki/README.md), [Nittan devices](01-fire/nittan/README.md) and [Paxton access equipment](03-access-control/paxton/README.md). Those earlier records are retained and are not counted again as new additions. Their previous check dates and evidence levels remain unchanged.

## Remaining gaps

This completes the collected device expansion batch across the six equipment categories. Coverage is still partial within brands: current Pyronix share-page resources, further Risco/BWare variants, the three Orisec full-file downloads and additional camera firmware/region editions remain in the research queue. Common trade and legacy service families were selected from publisher/supplier catalogues; no sales ranking or exhaustive worldwide coverage is claimed. The British Standards register remains at 147 references.

[Per-document source audit, held model conflicts and unresolved links](data/source-audits/devices-2026-10-28.json).
