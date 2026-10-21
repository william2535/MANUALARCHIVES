import io,json,tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import download

PDF=b'%PDF-1.4\n1 0 obj << /Type /Catalog >> endobj\ntrailer << /Root 1 0 R >>\n%%EOF\n'
class Response(io.BytesIO):
    def __init__(self,data,status=200,declared=None,url='https://manufacturer.example/manual.pdf'):
        super().__init__(data);self.status=status;self.url=url;self.headers={'Content-Length':str(len(data)if declared is None else declared)}
def opener(data=PDF,status=200,declared=None):return lambda *a,**k:Response(data,status,declared)
def record():return {'id':'example-123','category':'fire','brand':'Example','models':['Panel A'],'title':'Panel A manual','download_url':'https://manufacturer.example/manual.pdf','document_url':'https://manufacturer.example/manual.pdf','source_url':'https://manufacturer.example/support/','document_number':'DOC-1'}
class DownloadTests(unittest.TestCase):
    def test_html_challenge_is_not_saved_as_pdf(self):
        with tempfile.TemporaryDirectory()as directory:
            target=Path(directory)/'temp.part'
            with self.assertRaisesRegex(ValueError,'not a PDF'):download.fetch_pdf('https://manufacturer.example/manual.pdf',target,opener(b'<html>Please log in</html>'))
            self.assertFalse(target.exists())
    def test_non_success_status_is_not_saved(self):
        with tempfile.TemporaryDirectory()as directory:
            target=Path(directory)/'temp.part'
            with self.assertRaisesRegex(ValueError,'HTTP 202'):download.fetch_pdf('https://manufacturer.example/manual.pdf',target,opener(PDF,status=202))
            self.assertFalse(target.exists())
    def test_truncated_or_oversized_files_leave_no_partial(self):
        for data,declared,limit in [(PDF[:-7],None,10000),(PDF,len(PDF)+20,10000),(PDF,None,8)]:
            with self.subTest(data=data,limit=limit),tempfile.TemporaryDirectory()as directory:
                target=Path(directory)/'temp.part'
                with self.assertRaises(ValueError):download.fetch_pdf('https://manufacturer.example/manual.pdf',target,opener(data,declared=declared),max_bytes=limit)
                self.assertFalse(target.exists())
    def test_saved_file_has_exact_hash_and_resumes_without_network(self):
        with tempfile.TemporaryDirectory()as directory:
            result=download.download_record(record(),directory,opener=opener())
            self.assertEqual((Path(directory)/result['path']).read_bytes(),PDF)
            self.assertEqual(download.file_hash(Path(directory)/result['path']),result['sha256'])
            self.assertEqual(result['bytes'],len(PDF))
            def offline(*args,**kwargs):raise AssertionError('Resume unexpectedly used the network')
            resumed=download.download_record(record(),directory,result,opener=offline)
            self.assertEqual(resumed['result'],'already-saved')
    def test_changed_source_preserves_both_editions(self):
        with tempfile.TemporaryDirectory()as directory:
            a=download.download_record(record(),directory,opener=opener())
            b=download.download_record(record(),directory,a,refresh=True,opener=opener(PDF.replace(b'1.4',b'1.5')))
            self.assertNotEqual(a['sha256'],b['sha256']);self.assertNotEqual(a['path'],b['path'])
            self.assertTrue((Path(directory)/a['path']).is_file());self.assertTrue((Path(directory)/b['path']).is_file())
    def test_source_index_is_not_treated_as_an_arbitrary_pdf_download(self):
        r=record();r['download_url']=None;r['document_url']='https://manufacturer.example/all-manuals/'
        def network(*args,**kwargs):raise AssertionError('Must not choose an unrelated PDF from a source index')
        with tempfile.TemporaryDirectory()as directory:
            result=download.download_record(r,directory,opener=network)
            self.assertEqual(result['result'],'manual-download-needed')
    def test_download_compares_catalogue_hash_and_keeps_changed_source_for_review(self):
        import hashlib
        r=record();r.update(source_pdf_sha256=hashlib.sha256(PDF).hexdigest(),source_pdf_bytes=len(PDF))
        with tempfile.TemporaryDirectory()as directory:
            first=download.download_record(r,directory,opener=opener())
            self.assertEqual(first['catalogue_match'],'matched')
            changed=download.download_record(r,directory,first,refresh=True,opener=opener(PDF.replace(b'1.4',b'1.5')))
            self.assertEqual(changed['catalogue_match'],'changed')
            self.assertTrue((Path(directory)/first['path']).is_file())
            self.assertTrue((Path(directory)/changed['path']).is_file())
    def test_cached_file_is_compared_against_updated_catalogue_without_network(self):
        r=record()
        with tempfile.TemporaryDirectory()as directory:
            first=download.download_record(r,directory,opener=opener())
            self.assertEqual(first['catalogue_match'],'unverified')
            r.update(source_pdf_sha256='0'*64,source_pdf_bytes=len(PDF))
            def offline(*args,**kwargs):raise AssertionError('Unexpected network request')
            resumed=download.download_record(r,directory,first,opener=offline)
            self.assertEqual(resumed['result'],'already-saved')
            self.assertEqual(resumed['catalogue_match'],'changed')
    def test_axis_export_is_resolved_from_exact_model_page(self):
        r=record();r.update(brand='Axis',download_url=None,document_url='https://help.axis.com/en-us/example')
        def page(*args,**kwargs):return Response(b'<a href="/download/example.pdf">Download PDF</a>',url=r['document_url'])
        self.assertEqual(download.pdf_url(r,page),'https://help.axis.com/download/example.pdf')
    def test_filters_are_category_and_model_specific(self):
        a=record();b={**a,'id':'b','category':'cctv','brand':'Other','models':['Camera Z']}
        self.assertEqual(download.matching([a,b],category='fire',brand='example',model='panel'),[a])
        self.assertEqual(download.matching([a,b],record_id='b'),[b])
    def test_non_web_url_is_rejected(self):
        for value in ['file:///etc/passwd','javascript:alert(1)','https://user:password@example.com/manual.pdf']:
            with self.assertRaises(ValueError):download.http_url(value)
if __name__=='__main__':unittest.main()
