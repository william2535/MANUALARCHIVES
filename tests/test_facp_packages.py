import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from package_facp import main

class FACPPackageTests(unittest.TestCase):
    def prepare(self,root):
        for name in ['pdfs','checks']:(root/name).mkdir()
        payload=b'%PDF-1.4\nfixture bytes\n%%EOF\n';digest=hashlib.sha256(payload).hexdigest();rows=[]
        for n in [1,2]:
            url=f'https://docs.facpmanuals.com/manuals/Example/{n}.pdf';key=hashlib.sha256(url.encode()).hexdigest()
            rows.append({'id':str(n),'title':'../../Panel +','brand':'Example','s3Url':url,'source_url':'https://facpmanuals.com/example/'+str(n)})
            (root/'pdfs'/(key+'.pdf')).write_bytes(payload)
            (root/'checks'/(key+'.json')).write_text(json.dumps({'status':'complete-file','sha256':digest,'bytes':len(payload),'page_count':1}))
        (root/'inventory.json').write_text(json.dumps({'records':rows}))
        return rows

    def test_every_listing_survives_same_file_deduplication_and_paths_are_safe(self):
        with tempfile.TemporaryDirectory()as d:
            root=Path(d);self.prepare(root);out=root/'volumes'
            with patch.object(sys,'argv',['package_facp','--workspace',str(root),'--output',str(out)]),contextlib.redirect_stdout(io.StringIO()):main()
            zips=list(out.glob('*.zip'));self.assertEqual(len(zips),1)
            with zipfile.ZipFile(zips[0])as z:
                self.assertEqual(len([n for n in z.namelist()if n.endswith('.pdf')]),1)
                self.assertTrue(all('..'not in Path(n).parts and not Path(n).is_absolute()for n in z.namelist()))
                rows=json.loads(z.read('manifest.json'))['records'];self.assertEqual(len(rows),2)
                self.assertEqual(rows[0]['path'],rows[1]['path'])

    def test_corrupt_cached_pdf_is_not_packaged(self):
        with tempfile.TemporaryDirectory()as d:
            root=Path(d);rows=self.prepare(root);key=hashlib.sha256(rows[0]['s3Url'].encode()).hexdigest()
            (root/'pdfs'/(key+'.pdf')).write_bytes(b'truncated')
            with patch.object(sys,'argv',['package_facp','--workspace',str(root),'--output',str(root/'out')]),self.assertRaisesRegex(ValueError,'Cached file changed'):main()

if __name__=='__main__':unittest.main()
