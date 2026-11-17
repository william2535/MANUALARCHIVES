import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from resource_data import resource_errors
from download import matching


class ResourceTests(unittest.TestCase):
    def setUp(self):
        self.aov = json.loads((ROOT / 'data/aov.json').read_text())
        self.software = json.loads((ROOT / 'data/software.json').read_text())
        self.catalogue = json.loads((ROOT / 'data/catalogue.json').read_text())

    def test_curated_selection_preserves_existing_pdf_download_contract(self):
        selected = matching(self.catalogue['records'], collection='aov')
        self.assertEqual(set(self.aov['record_ids']), {r['id'] for r in selected})
        self.assertTrue(all(r['category'] == 'fire' for r in selected))
        self.assertFalse({r['id'] for r in self.software['records']} & {r['id'] for r in selected})
        self.assertEqual([], resource_errors(self.aov, self.software, self.catalogue))

    def test_stale_or_missing_collection_membership_is_rejected(self):
        self.aov['record_ids'].append('missing-record')
        errors = resource_errors(self.aov, self.software, self.catalogue)
        self.assertTrue(any('missing catalogue record' in e for e in errors))
        self.assertTrue(any('membership differs' in e for e in errors))

    def test_unsafe_links_and_gated_direct_packages_are_rejected(self):
        row = self.software['records'][0]
        row.update(source_url='javascript:alert(1)', access='installer-account', download_url='https://example.com/setup.zip')
        errors = resource_errors(self.aov, self.software, self.catalogue)
        self.assertTrue(any('invalid source_url' in e for e in errors))
        self.assertTrue(any('gated download' in e for e in errors))

    def test_source_evidence_and_dates_cannot_silently_disappear(self):
        row = self.software['records'][0]
        row['checked_on'] = 'not-a-date'
        row['verification'] = {}
        errors = resource_errors(self.aov, self.software, self.catalogue)
        self.assertTrue(any('invalid date' in e for e in errors))
        self.assertTrue(any('missing source evidence' in e for e in errors))

    def test_original_haes_model_paths_still_exist(self):
        for path in ['aov', 'aov-instruction-manual', 'szaov', 'mzaov']:
            self.assertTrue((ROOT / '01-fire/haes' / path / 'README.md').is_file())


if __name__ == '__main__':
    unittest.main()
