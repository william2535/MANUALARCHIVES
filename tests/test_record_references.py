import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from download import matching
from record_references import document_identity_errors


def records():
    canonical = dict(id='panel-guide', brand='Example', category='fire', models=['Panel'],
                     source_url='https://example.com/support',
                     document_url='https://example.com/guide.pdf',
                     download_url='https://example.com/guide.pdf')
    alias = dict(canonical, id='old-guide', models=['Earlier listing'], duplicate_of='panel-guide')
    return canonical, alias


class RecordReferenceTests(unittest.TestCase):
    def test_batch_downloads_one_copy_and_old_id_still_selects_it(self):
        canonical, alias = records()
        for rows in ([canonical, alias], [alias, canonical]):
            self.assertEqual(matching(rows), [canonical])
            self.assertEqual(matching(rows, record_id='old-guide'), [canonical])
            self.assertEqual(matching(rows, model='Earlier listing'), [canonical])
            self.assertEqual(document_identity_errors(rows), [])

    def test_duplicate_url_requires_an_explicit_reference(self):
        canonical, alias = records()
        del alias['duplicate_of']
        self.assertIn('repeated document URL', document_identity_errors([canonical, alias])[0])

    def test_missing_targets_cycles_and_unrelated_documents_are_rejected(self):
        canonical, alias = records()
        cases = [
            [dict(alias, duplicate_of='missing'), canonical],
            [dict(alias, duplicate_of='old-guide'), canonical],
            [alias, dict(canonical, duplicate_of='old-guide')],
            [dict(alias, download_url='https://example.com/different.pdf'), canonical],
            [dict(alias, brand='Another'), canonical],
            [dict(alias, category='cctv'), canonical],
            [dict(alias, source_pdf_sha256='a' * 64), dict(canonical, source_pdf_sha256='b' * 64)],
        ]
        for rows in cases:
            with self.subTest(rows=rows):
                self.assertTrue(document_identity_errors(rows))
                with self.assertRaises(ValueError):
                    matching(rows, record_id='old-guide')


if __name__ == '__main__':
    unittest.main()
