import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from collect_facp import initial_data, reconcile
from import_facp import import_records, new_record, category_for
from download import matching
from build_index import slug

def item(rid='one',url='https://docs.facpmanuals.com/manuals/Example/guide.pdf'):
    return dict(id=rid,title='Panel',slug='panel',brand='Example',brand_slug='example',
                s3Url=url,source_url='https://facpmanuals.com/manuals/example/'+rid,
                types=['Installation'],year='1999',fileSize=100,
                modelNumber='Panel, Unrelated peripheral, Referenced detector')

def inventory(items):
    return dict(records=items,by_brand=[dict(complete=True)],conflicts=[],failed_pages=[],
                source_url='https://facpmanuals.com/brands',page_count=1)

class FACPTests(unittest.TestCase):
    def test_plus_variant_keeps_its_own_navigation_folder(self):
        self.assertNotEqual(slug('VisorALARM'),slug('VisorALARM+'))

    def test_flight_payload_crossing_script_boundaries(self):
        data={'manuals':[item()], 'total':1}
        text='12:["component",{"initialData":'+json.dumps(data)+'}]\n'
        html=''.join('<script>self.__next_f.push('+json.dumps([1,s])+')</script>'for s in [text[:37],text[37:90],text[90:]])
        self.assertEqual(initial_data(html),data)
        with self.assertRaises(ValueError):initial_data('<html>temporary failure</html>')

    def test_duplicate_pagination_requires_unique_reconciliation(self):
        brands=[dict(slug='example',name='Example',manualCount=2)]
        page=dict(brand='Example',brand_slug='example',status='collected',total=2,page=1,manuals=[item(),item()])
        self.assertFalse(reconcile([page],brands)['by_brand'][0]['complete'])
        fixed=reconcile([page],brands,[dict(brand='Example',brand_slug='example',manuals=[item('two')])])
        self.assertTrue(fixed['by_brand'][0]['complete'])

    def test_flight_model_references_do_not_create_false_conflicts(self):
        a=item(); b=dict(a,modelNumber='$66')
        page=dict(brand='Example',brand_slug='example',status='collected',total=1,page=1,manuals=[a,b])
        result=reconcile([page],[dict(slug='example',name='Example',manualCount=1)])
        self.assertEqual(result['conflicts'],[])
        self.assertNotIn('modelNumber',result['records'][0])

    def test_source_year_and_referenced_parts_are_not_verified_metadata(self):
        row=new_record(item(),'Example','2026-10-21')
        self.assertEqual(row['models'],['Panel'])
        self.assertIsNone(row['revision_hint'])
        self.assertEqual(row['availability'],'pdf-link-listed')
        self.assertNotIn('source_pdf_sha256',row)

    def test_multi_purpose_document_retains_each_source_type(self):
        source=dict(item(),types=['Installation','Programming'])
        row=new_record(source,'Example','2026-10-21')
        self.assertEqual(row['document_types'],['installation','programming'])

    def test_existing_record_survives_byte_identical_mirror(self):
        source=item(); old=new_record(source,'Example','2026-10-01')
        old.update(id='existing',download_url='https://manufacturer.example/guide.pdf',
                   document_url='https://manufacturer.example/guide.pdf',source_kind='manufacturer',
                   source_pdf_sha256='a'*64,source_pdf_bytes=100,models=['Confirmed primary model'])
        check=dict(status='complete-file',sha256='a'*64,bytes=100,page_count=2)
        cat,audit=import_records({'records':[old]},inventory([source]),{source['s3Url']:check},'2026-10-21')
        self.assertEqual(len(cat['records']),1)
        result=cat['records'][0]
        self.assertEqual(result['id'],'existing');self.assertEqual(result['models'],old['models'])
        self.assertEqual(result['download_url'],old['download_url'])
        self.assertNotIn('pdf_eof_checked',result)
        self.assertEqual(audit['records'][0]['record_id'],'existing')
        self.assertEqual(result['alternate_source_urls'],[source['s3Url']])

    def test_failed_download_keeps_listing_and_all_categories_are_imported(self):
        entries=[item(),dict(item('two'),brand='WattMaster',brand_slug='wattmaster')]
        cat,audit=import_records({'records':[]},inventory(entries),{entries[0]['s3Url']:{'status':'retrieval-failed'}},'2026-10-21')
        self.assertEqual(len(cat['records']),2);self.assertEqual(audit['source_count'],2)
        self.assertEqual(cat['records'][0]['availability'],'retrieval-failed')
        self.assertEqual(cat['records'][1]['category'],'other-reference')
        self.assertEqual(len(matching(cat['records'],collection='facp')),2)

    def test_incomplete_inventory_cannot_be_declared_imported(self):
        inv=inventory([item()]);inv['by_brand'][0]['complete']=False
        with self.assertRaises(ValueError):import_records({'records':[]},inv,{},'2026-10-21')

    def test_reimport_keeps_ids(self):
        inv=inventory([item()]);a,_=import_records({'records':[]},inv,{},'2026-10-21')
        b,_=import_records(a,inv,{},'2026-10-21')
        self.assertEqual([r['id']for r in a['records']],[r['id']for r in b['records']])

if __name__=='__main__':unittest.main()
