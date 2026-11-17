# AOV / smoke ventilation

[Archive](../README.md) · [Search AOV manuals](../index.html#aov)

A curated UK smoke-ventilation collection: AOV control-panel installation and user instructions, configuration/menu references and wiring guides. Brand grouping is navigation, not a declaration of component compatibility or a complete brand inventory. Region, installed variant and latest edition still need checking in the original document.

Checked 2026-11-17: 28 document records. PDFs remain in the Fire catalogue with their original IDs and model folders; this is a curated collection, not extra copies.

| Brand | Documents |
|---|---:|
| [Custom Electronics](custom-electronics/README.md) | 5 |
| [D+H](d-plus-h/README.md) | 3 |
| [Haes](haes/README.md) | 5 |
| [SE Controls](se-controls/README.md) | 3 |
| [WindowMaster](windowmaster/README.md) | 12 |

## Download locally

```bash
python3 scripts/download.py --collection aov --list
python3 scripts/download.py --collection aov
```

Add `--brand "Haes"` or another listed brand for a smaller batch. This downloads private PDFs, subject to publisher terms; it does not download software.

## Coverage still to check

- Group SCS: current IP54 and legacy EV panel generations remain separate. Seven official links were identified, but direct retrieval returned HTTP 202 HTML; they are recorded in the source audit and excluded from complete-file counts.
- Colt and Adexon: no usable manufacturer manual was verified in this batch.
- Custom Electronics includes two image-only guides; visual identity was checked, but searchable text/OCR is not claimed.
- No complete inventory of every UK brand, product, firmware or historical edition is claimed.
