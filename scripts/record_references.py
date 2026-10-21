"""Preserve old catalogue IDs when two listings resolve to the same PDF."""


def canonical_record(row, by_id):
    if 'duplicate_of' not in row:
        return row
    target_id = row['duplicate_of']
    if not isinstance(target_id, str) or not target_id:
        raise ValueError(f'{row["id"]}: duplicate_of must name a record')
    target = by_id.get(target_id)
    if target is None:
        raise ValueError(f'{row["id"]}: duplicate target is missing')
    if target_id == row['id'] or 'duplicate_of' in target:
        raise ValueError(f'{row["id"]}: duplicate chains and cycles are not allowed')
    if (row['brand'] != target['brand'] or row['category'] != target['category'] or
            not row.get('download_url') or row['download_url'] != target.get('download_url')):
        raise ValueError(f'{row["id"]}: duplicate must reference the same brand, category and PDF URL')
    for key in ('source_pdf_sha256', 'source_pdf_bytes'):
        if row.get(key) is not None and target.get(key) is not None and row[key] != target[key]:
            raise ValueError(f'{row["id"]}: duplicate has conflicting {key}')
    return target


def document_identity_errors(rows):
    by_id = {row['id']: row for row in rows}
    identities, errors = {}, []
    for row in rows:
        try:
            canonical = canonical_record(row, by_id)
        except ValueError as error:
            errors.append(str(error))
            continue
        if row['document_url'] != row['source_url'] or row.get('download_url'):
            identity = (row['brand'], row.get('download_url') or row['document_url'])
            previous = identities.setdefault(identity, canonical['id'])
            if previous != canonical['id']:
                errors.append(f'{row["id"]}: repeated document URL without a confirmed duplicate reference')
    return errors
