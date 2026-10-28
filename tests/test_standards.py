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

    def test_published_dd_is_separate_from_consultation_drafts(self):
        self.assertTrue(any(r['edition'].startswith('DD CLC/TS ') for r in self.data['records']))
        self.assertTrue(all(d['reference'].endswith(' DC') for d in self.data['draft_watchlist']))
        self.assertEqual(standards_errors(self.data), [])
        self.assertIn('Consultation draft watchlist', render_standards_markdown(self.data))

    def test_draft_evidence_cannot_be_from_the_future(self):
        self.data['draft_watchlist'][0]['source_checked'] = '2099-01-01'
        self.assertTrue(any('draft evidence is later' in e for e in standards_errors(self.data)))

    def test_draft_requires_publisher_source(self):
        self.data['draft_watchlist'][0]['source_url'] = 'https://example.com/draft'
        self.assertTrue(any('draft lacks official evidence' in e for e in standards_errors(self.data)))

    def test_free_downloads_reject_purchase_pages_and_incomplete_files(self):
        resource = self.data['free_resources'][0]
        resource['download_url'] = self.row['source_url']
        resource['sha256'] = ''
        resource['pdf_eof_checked'] = False
        errors = standards_errors(self.data)
        self.assertTrue(any('direct PDF' in e for e in errors))
        self.assertTrue(any('complete-file verification' in e for e in errors))

    def test_free_guidance_cannot_be_a_full_standard_or_hide_edition_scope(self):
        resource = self.data['free_resources'][0]
        resource['is_full_standard'] = True
        resource['scope_note'] = ''
        errors = standards_errors(self.data)
        self.assertTrue(any('full standard' in e for e in errors))
        self.assertTrue(any('issue or scope' in e for e in errors))

    def test_free_resources_need_real_unique_relationships_and_pdfs(self):
        self.data['free_resources'][0]['related_standard_ids'] = ['nonexistent-standard']
        self.data['free_resources'].append(copy.deepcopy(self.data['free_resources'][1]))
        errors = standards_errors(self.data)
        self.assertTrue(any('related standard' in e for e in errors))
        self.assertTrue(any('duplicate free-resource id' in e for e in errors))
        self.assertTrue(any('duplicate free-resource PDF' in e for e in errors))

    def test_pdf_check_date_does_not_refresh_standard_status(self):
        self.assertLess(self.data['checked_on'], self.data['free_resources_checked_on'])
        self.assertEqual(standards_errors(self.data), [])
        self.data['free_resources'][0]['checked_on'] = '2099-01-01'
        self.assertTrue(any('PDF evidence is later' in e for e in standards_errors(self.data)))

    def test_markdown_downloads_are_free_guidance_with_limited_scope(self):
        text = render_standards_markdown(self.data)
        downloads = text.split('## Free PDF downloads', 1)[1].split('## How to use this register', 1)[0]
        for resource in self.data['free_resources']:
            self.assertIn(resource['download_url'], downloads)
            self.assertIn(resource['scope_note'], downloads)
        self.assertNotIn('knowledge.bsigroup.com', downloads)
        self.assertIn('does not cover A2:2026', text)
        self.assertIn('no verified free download', text)
        for row in self.data['records']:
            self.assertIn(f'[{row["edition"]}](#ref-{row["id"]})', text)
            self.assertIn(f'<a id="ref-{row["id"]}"></a>', text)

    def test_older_version_one_feed_without_free_resources_remains_valid(self):
        self.data.pop('free_resources')
        self.data.pop('free_resources_checked_on')
        self.assertEqual(standards_errors(self.data), [])
        self.assertIn('0 free PDF guides', render_standards_markdown(self.data))


if __name__ == '__main__':
    unittest.main()
