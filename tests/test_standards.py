import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from standards_data import standards_errors, render_standards_markdown


class StandardsTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'data/standards.json').read_text())
        self.row = next(r for r in self.data['records'] if r['standard'] == 'BS 7671')

    def test_validating_preserves_sources_and_history(self):
        original = copy.deepcopy(self.data)
        self.assertEqual(standards_errors(self.data), [])
        self.assertEqual(standards_errors(self.data), [])
        self.assertEqual(self.data, original)

    def test_draft_cannot_be_presented_as_published_standard(self):
        self.row['edition'] = '26/30510738 DC'
        self.assertTrue(any('drafts' in e for e in standards_errors(self.data)))

    def test_source_status_conflicts_are_preserved(self):
        row = next(r for r in self.data['records'] if r['standard'] == 'BS EN 50131-3')
        self.assertEqual(row['status'], 'current')
        self.assertTrue(any(h['publisher_status'].startswith('Current') for h in row['earlier_records']))
        text = render_standards_markdown(self.data)
        self.assertIn('BS EN 50131-3:2009', text)
        self.assertIn('withdrawal date or transition deadline is inferred', text)

    def test_amendment_labels_must_match_the_exact_edition(self):
        self.row['amendments_in_designation'] = ['A3:2024']
        self.assertTrue(any('amendment labels' in e for e in standards_errors(self.data)))

    def test_evidence_cannot_be_dated_after_the_register(self):
        self.row['source_checked'] = '2099-01-01'
        self.assertTrue(any('evidence is later' in e for e in standards_errors(self.data)))

    def test_standards_cannot_enter_the_manual_pdf_queue(self):
        self.row['download_url'] = 'https://example.com/unlicensed.pdf'
        self.assertTrue(any('manual downloads' in e for e in standards_errors(self.data)))

    def test_summary_needs_its_evidence_label(self):
        self.row['summary_basis'] = 'edition-metadata-only'
        self.assertTrue(any('summary/evidence mismatch' in e for e in standards_errors(self.data)))

    def test_withdrawn_is_not_current_under_review(self):
        self.row.update(status='withdrawn', under_review=True)
        self.assertTrue(any('withdrawn record cannot' in e for e in standards_errors(self.data)))


if __name__ == '__main__':
    unittest.main()
