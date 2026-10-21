import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from app_data import build_manifest, build_gap_audit, download_info
from validate import date_errors


def record(**changes):
    return dict(id='example-123', brand='Example', category='fire', models=['Panel A'],
                title='Panel A installation', document_type='installation', document_number='DOC1',
                source_url='https://example.com/support', document_url='https://example.com/a.pdf',
                download_url='https://example.com/a.pdf', availability='pdf-link-listed',
                source_checked='2026-10-16', language='not-verified', region='not-verified', **changes)


class AppDataTests(unittest.TestCase):
    def test_file_hash_does_not_claim_full_validation_or_offline_storage(self):
        row = record(source_pdf_sha256=hashlib.sha256(b'pdf').hexdigest(), source_pdf_bytes=3,
                     pdf_header_checked='2026-10-16')
        info = download_info(row)
        self.assertEqual(info['status'], 'file-hash')
        self.assertNotIn('saved', str(info))
        row['pdf_eof_checked'] = True
        self.assertEqual(download_info(row)['status'], 'complete-file')

    def test_indexed_pdf_is_not_promoted_to_a_checksum_checked_download(self):
        row = record(page_count=12)
        row['availability'] = 'pdf-indexed'
        info = download_info(row)
        self.assertEqual(info['status'], 'pdf-indexed')
        self.assertIsNone(info['verification']['sha256'])
        self.assertIsNone(info['verification']['bytes'])

    def test_failed_retrieval_takes_precedence_over_older_checksum(self):
        row = record(source_pdf_sha256='a' * 64, source_pdf_bytes=123, pdf_header_checked=True,
                     pdf_eof_checked=True, retrieval_evidence={'checked_on': '2026-10-16'})
        row.update(availability='retrieval-failed', source_checked='2026-10-21')
        info = download_info(row)
        self.assertEqual(info['status'], 'retrieval-failed')
        self.assertEqual(info['verification']['checked_on'], '2026-10-16')

    def test_online_manual_is_a_separate_gap_from_a_failed_download(self):
        row = record()
        row.update(download_url=None, availability='online-manual', document_url='https://example.com/manual')
        audit = build_gap_audit({'generated_on': '2026-10-21', 'records': [row]})
        self.assertEqual(download_info(row)['mode'], 'source-page')
        self.assertEqual(audit['gap_counts']['web-manual-without-direct-pdf'], 1)
        self.assertNotIn('retrieval-failed', audit['gap_counts'])
        self.assertEqual(audit['model_coverage'][0]['document_types'], ['installation'])

    def test_feed_preserves_ids_and_shared_models_and_changes_fingerprint(self):
        row = record()
        row['models'].append('Panel B')
        data = {'generated_on': '2026-10-21', 'records': [row]}
        a = build_manifest(data)
        self.assertEqual(a['records'][0]['id'], row['id'])
        self.assertEqual(a['records'][0]['models'], ['Panel A', 'Panel B'])
        self.assertEqual(a, build_manifest(data))
        row['download_url'] = 'https://example.com/new.pdf'
        self.assertNotEqual(a['catalogue_sha256'], build_manifest(data)['catalogue_sha256'])

    def test_historic_check_dates_are_preserved_and_future_or_invalid_dates_rejected(self):
        row = record()
        data = {'generated_on': '2026-10-21', 'records': [row]}
        self.assertEqual(date_errors(data), [])
        self.assertEqual(row['source_checked'], '2026-10-16')
        for value in ['2026-10-22', '2026-02-30', None]:
            row['source_checked'] = value
            self.assertTrue(date_errors(data))


if __name__ == '__main__':
    unittest.main()
