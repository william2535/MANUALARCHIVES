"""Build deterministic mobile catalogue data and audit every indexed record.

No network requests and no claims that a device has downloaded a document.
"""
import collections
import hashlib
import json
import re
from urllib.parse import urlparse


def catalogue_digest(catalogue):
    encoded = json.dumps(catalogue, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def download_info(row):
    evidence = row.get('retrieval_evidence') or {}
    digest = row.get('source_pdf_sha256')
    size = row.get('source_pdf_bytes')
    has_hash = bool(digest and isinstance(size, int) and size > 0)
    complete = bool(has_hash and row.get('pdf_header_checked') and row.get('pdf_eof_checked'))
    indexed = bool(row.get('page_count') and row.get('availability') == 'pdf-indexed')
    level = ('complete-file' if complete else 'file-hash' if has_hash else
             'pdf-indexed' if indexed else 'pdf-header' if row.get('pdf_header_checked') else 'unverified')
    url = row.get('download_url')
    axis = (not url and row['brand'] == 'Axis' and
            urlparse(row['document_url']).hostname == 'help.axis.com')
    mode = 'direct-pdf' if url else 'resolve-pdf-export' if axis else 'source-page'
    state = ('retrieval-failed' if row['availability'] == 'retrieval-failed' else
             level if url and level != 'unverified' else 'listed' if url else 'source-page')
    service_check = row.get('pdf_indexing_evidence') or {}
    header_date = row.get('pdf_header_checked')
    checked_on = (evidence.get('checked_on') or
                  (header_date if isinstance(header_date, str) else None) or
                  service_check.get('checked_on') or row.get('source_checked'))
    return {
        'mode': mode, 'status': state, 'url': url,
        'source_page_url': row['document_url'],
        'resolver': 'axis-manual-pdf' if axis else None,
        'verification': {
            'level': level, 'checked_on': checked_on if level != 'unverified' else None,
            'sha256': digest if has_hash else None, 'bytes': size if has_hash else None,
            'page_count': row.get('page_count'),
        },
    }


def build_manifest(catalogue):
    keys = ['id', 'category', 'brand', 'models', 'title', 'document_type',
            'document_number', 'revision_hint', 'revision_basis', 'verified_revision',
            'language', 'region', 'source_kind', 'source_url', 'source_checked',
            'model_basis', 'retrieval_note']
    records = [{**{k: row.get(k) for k in keys}, 'download': download_info(row),
                **({'duplicate_of': row['duplicate_of']} if 'duplicate_of' in row else {})}
               for row in sorted(catalogue['records'], key=lambda row: row['id'])]
    states = collections.Counter(r['download']['status'] for r in records)
    return {
        'schema_version': 1, 'generated_on': catalogue['generated_on'],
        'catalogue_sha256': catalogue_digest(catalogue),
        'repository_url': 'https://github.com/william2535/MANUALARCHIVES',
        'distribution': 'source-link-only',
        'record_count': len(records), 'download_status_counts': dict(sorted(states.items())),
        'records': records,
    }


def record_gaps(row):
    """Review flags, not a claim that all models need every document type."""
    info = download_info(row)
    gaps = []
    if not row.get('download_url'):
        gaps.append('web-manual-without-direct-pdf' if row['availability'] == 'online-manual'
                    else 'viewer-without-direct-pdf' if row['availability'] == 'document-viewer'
                    else 'download-url-unresolved')
    if row['availability'] == 'retrieval-failed':
        gaps.append('retrieval-failed')
    if row.get('download_url') and info['verification']['level'] != 'complete-file':
        gaps.append('complete-file-check-needed')
    for key in ['language', 'region']:
        if row.get(key) in (None, '', 'not-verified'):
            gaps.append(key + '-unverified')
    if not row.get('document_number'):
        gaps.append('document-number-unrecorded')
    basis = row.get('revision_basis') or ''
    if not row.get('verified_revision') and (not row.get('revision_hint') or not basis or
                                            re.search(r'filename|not.verified', basis, re.I)):
        gaps.append('revision-review-needed')
    if re.search(r'filename|not.*verified', row.get('model_basis', ''), re.I):
        gaps.append('model-applicability-review-needed')
    if row.get('metadata_conflicts'):
        gaps.append('source-metadata-conflict')
    if row.get('possible_duplicate_of'):
        gaps.append('possible-duplicate-review-needed')
    return gaps


def build_gap_audit(catalogue):
    rows = catalogue['records']
    flagged, brands, model_groups = [], {}, {}
    for row in sorted(rows, key=lambda r: r['id']):
        gaps = record_gaps(row)
        if gaps:
            flagged.append({'id': row['id'], 'brand': row['brand'], 'category': row['category'], 'gaps': gaps,
                            **{k: row[k] for k in ['metadata_conflicts', 'possible_duplicate_of', 'duplicate_of'] if row.get(k)}})
        brand = brands.setdefault(row['brand'], {'records': 0, 'categories': set(),
                                               'document_types': collections.Counter(),
                                               'download_status': collections.Counter(),
                                               'gap_counts': collections.Counter()})
        brand['records'] += 1
        brand['categories'].add(row['category'])
        brand['document_types'].update([row['document_type']])
        brand['download_status'].update([download_info(row)['status']])
        brand['gap_counts'].update(gaps)
        for model in row['models']:
            key = (row['category'], row['brand'], model)
            group = model_groups.setdefault(key, {'record_ids': [], 'document_types': set()})
            group['record_ids'].append(row['id'])
            group['document_types'].add(row['document_type'])
    return {
        'schema_version': 1, 'generated_on': catalogue['generated_on'],
        'catalogue_sha256': catalogue_digest(catalogue),
        'scope': 'Every indexed record and model association. Products absent from the catalogue require further manufacturer inventory research. Flags are review tasks, not proof of a broken link or a missing publication.',
        'record_count': len(rows),
        'gap_counts': dict(sorted(collections.Counter(g for r in flagged for g in r['gaps']).items())),
        'by_brand': [{'brand': name, **{k: sorted(v) if isinstance(v, set) else dict(sorted(v.items()))
                                     if isinstance(v, collections.Counter) else v for k, v in summary.items()}}
                     for name, summary in sorted(brands.items())],
        'records': flagged,
        'model_coverage': [{'category': category, 'brand': brand, 'model': model,
                            'record_ids': group['record_ids'], 'document_types': sorted(group['document_types'])}
                           for (category, brand, model), group in sorted(model_groups.items())],
    }
