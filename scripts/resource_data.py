"""Validated curated AOV collection and official software links (no binaries)."""
from datetime import date
import re
from urllib.parse import urlparse

ACCESS = {
    'public': 'Public download page',
    'account-required': 'Account required',
    'installer-account': 'Installer access required',
    'registration-required': 'Registration required',
    'not-verified': 'Download access not verified',
}
TYPES = {'software': 'Software', 'driver': 'Driver', 'firmware-portal': 'Firmware portal'}


def resource_errors(aov, software, catalogue):
    errors = []
    def check_date(value, label):
        try:
            date.fromisoformat(value)
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value): raise ValueError()
        except (ValueError, TypeError): errors.append(label + ': invalid date')
    for label, data in [('AOV', aov), ('software', software)]:
        if data.get('schema_version') != 1: errors.append(label + ': invalid schema')
        check_date(data.get('checked_on'), label)
        if not data.get('scope'): errors.append(label + ': missing scope')
    ids = aov.get('record_ids', [])
    by_id = {r['id']: r for r in catalogue['records']}
    if len(ids) != len(set(ids)): errors.append('AOV: duplicated record IDs')
    if set(ids) != {r['id'] for r in catalogue['records'] if 'aov' in r.get('source_collections', [])}:
        errors.append('AOV: collection membership differs from catalogue')
    for rid in ids:
        if rid not in by_id: errors.append('AOV: missing catalogue record ' + rid)
    seen = set()
    for row in software.get('records', []):
        rid = row.get('id', '')
        if rid in seen or not re.fullmatch(r'[a-z0-9-]+', rid): errors.append('software: invalid/duplicate ID ' + rid)
        seen.add(rid)
        for key in ['brand', 'name', 'description']:
            if not isinstance(row.get(key), str) or not row[key].strip(): errors.append(rid + ': missing ' + key)
        if row.get('category') not in ['fire', 'security', 'cctv', 'access-control', 'aov', 'other-reference']:
            errors.append(rid + ': invalid category')
        if row.get('access') not in ACCESS: errors.append(rid + ': invalid access')
        if row.get('resource_type') not in TYPES: errors.append(rid + ': invalid resource type')
        for key in ['products', 'platforms']:
            value = row.get(key)
            if not isinstance(value, list) or not all(isinstance(x, str) and x.strip() for x in value):
                errors.append(rid + ': invalid ' + key)
        if not row.get('products'): errors.append(rid + ': missing products / portal scope')
        for key in ['source_url', 'download_url']:
            value = row.get(key)
            if key == 'download_url' and value is None: continue
            parsed = urlparse(value or '')
            if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
                errors.append(rid + ': invalid ' + key)
        if row.get('download_url') and row.get('access') != 'public': errors.append(rid + ': gated download must use source page')
        check_date(row.get('checked_on'), rid)
        if row.get('checked_on', '') > software.get('checked_on', ''): errors.append(rid + ': future source check')
        evidence = row.get('verification', {})
        if not all(evidence.get(k) for k in ['method', 'status', 'final_url', 'note']): errors.append(rid + ': missing source evidence')
    return errors


def render_collections(aov, software, catalogue, write, slug, md):
    rows = {r['id']: r for r in catalogue['records']}
    selected = [rows[rid] for rid in aov['record_ids']]
    aov_lines = ['# AOV / smoke ventilation', '', '[Archive](../README.md) · [Search AOV manuals](../index.html#aov)', '', aov['scope'], '',
                 f"Checked {aov['checked_on']}: {len(selected)} document records. PDFs remain in the Fire catalogue with their original IDs and model folders; this is a curated collection, not extra copies.", '',
                 '| Brand | Documents |', '|---|---:|']
    for brand in sorted({r['brand'] for r in selected}):
        records = [r for r in selected if r['brand'] == brand]
        aov_lines.append(f'| [{md(brand)}]({slug(brand)}/README.md) | {len(records)} |')
        lines = [f'# {md(brand)} — AOV / smoke ventilation', '', '[AOV collection](../README.md) · [Archive](../../README.md)', '',
                 'Check the exact control panel, actuator, document issue and system design. Datasheets and brochures do not replace installation instructions.', '',
                 '| Document / model coverage | Type | Revision | Source |', '|---|---|---|---|']
        for r in records:
            url = r.get('download_url') or r['document_url']
            lines.append(f"| [{md(r['title'])}]({url}) · {md(', '.join(r['models']))} | {md(r['document_type'])} | {md(r.get('verified_revision') or r.get('revision_hint'))} | [{md(r['source_kind'])}]({r['source_url']}) |")
        lines += ['', 'Complete-file verification, dates and source notes: [catalogue](../../data/catalogue.json). PDFs are linked, not mirrored.']
        write(f'08-aov/{slug(brand)}/README.md', '\n'.join(lines))
    aov_lines += ['', '## Download locally', '', '```bash', 'python3 scripts/download.py --collection aov --list', 'python3 scripts/download.py --collection aov', '```', '',
                  'Add `--brand "Haes"` or another listed brand for a smaller batch. This downloads private PDFs, subject to publisher terms; it does not download software.', '',
                  '## Coverage still to check', ''] + ['- ' + gap for gap in aov.get('gaps', [])]
    write('08-aov/README.md', '\n'.join(aov_lines))
    sw_lines = ['# Panel / NVR software and drivers', '', '[Archive](../README.md) · [Search software and drivers](../index.html#software)', '', software['scope'], '',
                f"{len(software['records'])} official resource links, checked {software['checked_on']}. Installer packages are not mirrored, downloaded or executed by this archive. A listed link is not an installed or validated package.", '',
                '| Brand | Resources |', '|---|---:|']
    for brand in sorted({r['brand'] for r in software['records']}):
        records = [r for r in software['records'] if r['brand'] == brand]
        sw_lines.append(f'| [{md(brand)}]({slug(brand)}/README.md) | {len(records)} |')
        lines = [f'# {md(brand)} — software and drivers', '', '[Software collection](../README.md) · [Archive](../../README.md)', '',
                 '| Resource | Products / scope | Access | Platform |', '|---|---|---|---|']
        for r in records:
            lines.append(f"| [{md(r['name'])}]({r['source_url']}) | {md(', '.join(r['products']))} | {ACCESS[r['access']]} | {md(', '.join(r['platforms']) or 'Not verified')} |")
        for r in records:
            lines += ['', '## ' + md(r['name']), '', r['description'], '',
                      f"Checked {r['checked_on']}. {r['verification']['note']}", '',
                      f"Version: {md(r.get('version'))}. Type: {TYPES[r['resource_type']]}. [Official source]({r['source_url']})."]
            if r.get('download_url'): lines += ['', f"[Publisher-listed package link]({r['download_url']}) — package contents, signature and compatibility have not been tested."]
        write(f'09-software-drivers/{slug(brand)}/README.md', '\n'.join(lines))
    sw_lines += ['', '## Using these resources', '',
                 'Use the vendor’s model/firmware and OS requirements before installation. Some tools require a licence, training or an installer account. Firmware portals are links to vendor selection pages, not a recommendation to flash equipment.', '',
                 'The searchable index works offline; obtaining vendor packages and account access requires a connection. Software records are deliberately separate from the PDF download feed.', '',
                 '[Structured feed](../data/software.json) · [Maintenance rules](../CONTRIBUTING.md)', '', '## Coverage still to check', ''] + ['- ' + gap for gap in software.get('gaps', [])]
    write('09-software-drivers/README.md', '\n'.join(sw_lines))
