"""Validate and render the independently sourced British Standards register."""
import re
from datetime import date
from urllib.parse import urlparse


def standards_errors(data):
    errors = []
    def error(message):
        errors.append('standards: ' + message)
    def parsed(value, label, optional=False):
        if optional and value is None:
            return None
        try:
            if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                raise ValueError()
            return date.fromisoformat(value)
        except ValueError:
            error(label + ': invalid ISO date')
    def official_url(value):
        p = urlparse(value or '')
        return p.scheme == 'https' and p.hostname in {'knowledge.bsigroup.com', 'www.bsigroup.com', 'bsigroup.com', 'electrical.theiet.org', 'standardsdevelopment.bsigroup.com'} and not p.username and not p.password
    if data.get('schema_version') != 1:
        error('unsupported schema version')
    checked = parsed(data.get('checked_on'), 'checked_on')
    if checked and checked > date.today():
        error('check date is in the future')
    if data.get('coverage', {}).get('complete') is not False:
        error('a complete inventory has not been established')
    ids, editions = set(), set()
    for r in data.get('records', []):
        rid = r.get('id', '')
        if not re.fullmatch(r'[a-z0-9-]+', rid) or rid in ids:
            error('invalid or duplicate id ' + rid)
        ids.add(rid)
        edition = r.get('edition', '')
        if edition in editions or not re.fullmatch(r'(BS(?: EN)?(?: IEC)?|PD(?: CEN/TS| CLC/TS)?|DD CLC/TS) \d+(?:-\d+)*:\d{4}(?:\+A\d+:\d{4})*', edition):
            error(rid + ': duplicate/invalid published designation (drafts must not be current standards)')
        editions.add(edition)
        if r.get('standard') != edition.split(':')[0]:
            error(rid + ': standard/edition mismatch')
        if not r.get('title') or r.get('category') not in data.get('categories', {}):
            error(rid + ': missing title or category')
        if r.get('status') not in {'current', 'withdrawn'}:
            error(rid + ': invalid status')
        if r.get('status') == 'withdrawn' and r.get('under_review'):
            error(rid + ': withdrawn record cannot be current under review')
        expected_status = 'Withdrawn' if r.get('status') == 'withdrawn' else 'Current' + (', Under Review' if r.get('under_review') else '')
        if r.get('publisher_status') != expected_status:
            error(rid + ': publisher status differs from normalized status')
        evidence_date = parsed(r.get('source_checked'), rid + ' source_checked')
        publication = parsed(r.get('publisher_record_date'), rid + ' publisher_record_date', optional=True)
        if checked and evidence_date and evidence_date > checked:
            error(rid + ': evidence is later than register check')
        if publication and evidence_date and publication > evidence_date:
            error(rid + ': future publication cannot be checked as published')
        if r.get('amendments_in_designation') != re.findall(r'\+(A\d+:\d{4})', edition):
            error(rid + ': amendment labels differ from designation')
        if r.get('access') != 'publisher-link-only' or r.get('download_url') or r.get('local_pdf'):
            error(rid + ': standards must not be exposed as manual downloads')
        if r.get('history_complete') is not False:
            error(rid + ': complete history has not been established')
        if r.get('summary_basis') not in {'edition-metadata-only', 'publisher-public-summary'}:
            error(rid + ': invalid summary basis')
        if bool(r.get('change_summary')) != (r.get('summary_basis') == 'publisher-public-summary'):
            error(rid + ': summary/evidence mismatch')
        if edition in r.get('supersedes', []):
            error(rid + ': an edition cannot supersede itself')
        urls = list(r.get('source_urls', []))
        if r.get('source_url') not in urls:
            error(rid + ': primary source missing')
        urls += [x.get('source_url') for x in r.get('earlier_records', [])]
        transition = r.get('transition')
        if transition:
            parsed(transition.get('ends_on'), rid + ' transition ends_on')
            urls.append(transition.get('source_url'))
        if not urls or not all(official_url(url) for url in urls):
            error(rid + ': invalid or non-publisher source')
    if not editions:
        error('empty register')
    draft_ids = set()
    for draft in data.get('draft_watchlist', []):
        reference = draft.get('reference', '')
        if not re.fullmatch(r'\d{2}/\d+ DC', reference) or reference in draft_ids:
            error('invalid or duplicate consultation draft reference')
        draft_ids.add(reference)
        if not official_url(draft.get('source_url')) or not draft.get('note'):
            error(reference + ': draft lacks official evidence or status explanation')
        publication = parsed(draft.get('publisher_record_date'), reference + ' publisher_record_date')
        evidence = parsed(draft.get('source_checked'), reference + ' source_checked')
        if publication and evidence and publication > evidence:
            error(reference + ': future draft cannot be checked as published')
        if checked and evidence and evidence > checked:
            error(reference + ': draft evidence is later than register check')
    return errors


def render_standards_markdown(data):
    def md(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    rows = data['records']
    lines = ['# British Standards — updates and revisions', '', '[Archive](../README.md) · [Search offline](../index.html#standards) · [App data](../data/standards.json)', '',
             f'**{len(rows)} checked references · {len(data["categories"])} groups · checked {data["checked_on"]}**', '', data['coverage']['scope'], '',
             '## How to use this register', '']
    lines += ['- ' + item for item in data['coverage']['limits']]
    lines += ['', '## Recent editions and amendments', '', '| Edition | Subject | BSI record date | Public revision note |', '|---|---|---|---|']
    recent = sorted((r for r in rows if max(map(int, re.findall(r':(\d{4})', r['edition']))) >= 2024), key=lambda r: r['publisher_record_date'] or '', reverse=True)
    for r in recent:
        note = r['change_summary'] or 'Edition metadata checked; detailed changes require the original.'
        lines.append(f'| [{md(r["edition"])}]({r["source_url"]}) | {md(r["title"])} | {r["publisher_record_date"] or "Not established"} | {md(note)} |')
    for category, label in data['categories'].items():
        lines += ['', '## ' + label, '', '| Edition | Subject | Publisher status | BSI record date | Amendment labels |', '|---|---|---|---|---|']
        for r in rows:
            if r['category'] != category:
                continue
            lines.append(f'| [{md(r["edition"])}]({r["source_url"]}) | {md(r["title"])} | {r["publisher_status"]} | {r["publisher_record_date"] or "Not established"} | {", ".join(r["amendments_in_designation"]) or "None in designation"} |')
    lines += ['', '## Revision notes and earlier records', '']
    for r in rows:
        if not any(r[k] for k in ['change_summary', 'earlier_records', 'notes', 'transition']):
            continue
        lines += ['### ' + r['edition'], '', f'[Publisher record]({r["source_url"]}) · checked {r["source_checked"]}', '']
        if r['change_summary']:
            lines += [r['change_summary'], '']
        if r['supersedes']:
            lines += ['Publisher-confirmed predecessor(s): ' + ', '.join(r['supersedes']) + '.', '']
        if r['transition']:
            t = r['transition']
            lines += [f'Transition end: **{t["ends_on"]}** for {t["previous_edition"]}. {t["note"]} [IET source]({t["source_url"]}).', '']
        lines += ['- ' + note for note in r['notes']]
        for h in r['earlier_records']:
            lines += [f'- Earlier record: [{h["edition"]}]({h["source_url"]}) — publisher status: {h["publisher_status"]}. {h["note"]}']
        if len(r['source_urls']) > 1:
            lines += ['', 'Additional official sources: ' + ' · '.join(f'[source {i+1}]({url})' for i, url in enumerate(r['source_urls'][1:]))]
        lines += ['']
    if data.get('draft_watchlist'):
        lines += ['## Consultation draft watchlist', '', 'These are proposals, not published replacements. A catalogue listing does not establish whether public comments remain open.', '', '| Draft reference | Subject | BSI record date |', '|---|---|---|']
        for draft in data['draft_watchlist']:
            lines.append(f'| [{md(draft["reference"])}]({draft["source_url"]}) | {md(draft["subject"])} | {draft["publisher_record_date"]} |')
        lines += ['']
    lines += ['## Coverage still to verify', ''] + ['- ' + x for x in data['coverage']['remaining_checks']]
    lines += ['', '## Maintenance', '', 'Edit `data/standards.json`, retaining earlier records and their evidence. Verify the exact edition on its publisher page, record the check date, and distinguish publication, amendment and withdrawal dates. Do not promote a consultation draft to a published standard or infer withdrawal from age. Run `python3 scripts/build_index.py`, `python3 scripts/validate.py` and the tests. Rebuilding does not recheck sources.', '', 'The register is a dated snapshot, with no automatic monitoring. Full standards are obtained from the publisher under its licence; the manuals downloader does not download them.']
    return '\n'.join(lines)
