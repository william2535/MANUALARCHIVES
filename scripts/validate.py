#!/usr/bin/env python3
"""Validate catalogue identity, links, paths, generated navigation and embedded data."""
import collections,json,re,sys
from datetime import date
from pathlib import Path,PurePosixPath
from urllib.parse import urlparse
from app_data import build_manifest, build_gap_audit
from standards_data import standards_errors, render_standards_markdown
ROOT=Path(__file__).resolve().parents[1]
def date_errors(data):
    errors=[]
    def parse(value,label):
        try:
            if not isinstance(value,str)or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):raise ValueError()
            return date.fromisoformat(value)
        except ValueError:errors.append(f'{label}: invalid ISO date');return None
    generated=parse(data.get('generated_on'),'generated_on')
    for row in data['records']:
        values={'source_checked':row.get('source_checked')}
        for key in ['retrieval_evidence','pdf_indexing_evidence']:
            if row.get(key,{}).get('checked_on'):values[key]=row[key]['checked_on']
        if isinstance(row.get('pdf_header_checked'),str):values['pdf_header_checked']=row['pdf_header_checked']
        for label,value in values.items():
            checked=parse(value,f'{row["id"]}: {label}')
            if generated and checked and checked>generated:errors.append(f'{row["id"]}: {label} is later than catalogue build')
    return errors
def validate(root=ROOT):
    data=json.loads((root/'data/catalogue.json').read_text());rows=data['records'];errors=[];ids=set();identities=set()
    if data.get('schema_version')!=1:errors.append('Unexpected schema version')
    for row in rows:
        rid=row.get('id','')
        if rid in ids or not re.fullmatch(r'[a-z0-9-]+',rid):errors.append(f'Invalid or duplicated id {rid}')
        ids.add(rid)
        if row.get('category')not in ['fire','security','access-control','cctv']:errors.append(f'{rid}: invalid category')
        if row.get('source_kind')not in ['manufacturer','installer','distributor']:errors.append(f'{rid}: missing or invalid source provenance')
        if row.get('source_pdf_sha256')and not re.fullmatch(r'[0-9a-f]{64}',row['source_pdf_sha256']):errors.append(f'{rid}: invalid source checksum')
        if row.get('source_pdf_sha256')and not isinstance(row.get('source_pdf_bytes'),int):errors.append(f'{rid}: checksum lacks byte count')
        if not row.get('models')or not all(isinstance(m,str)and m.strip()for m in row['models']):errors.append(f'{rid}: missing models/family')
        if row.get('local_pdf')is not None:errors.append(f'{rid}: public catalogue unexpectedly claims a mirrored PDF')
        if row.get('distribution')!='source-link-only':errors.append(f'{rid}: distribution review required')
        for field in ['source_url','document_url','download_url']:
            url=row.get(field)
            if not url and field=='download_url':continue
            p=urlparse(url or '')
            if p.scheme not in ['https','http']or not p.hostname or p.username or p.password:errors.append(f'{rid}: invalid {field}')
        identity=row['brand']+'|'+(row.get('download_url')or row['document_url'])
        if row['document_url']!=row['source_url']or row.get('download_url'):
            if identity in identities:errors.append(f'{rid}: repeated document URL')
            identities.add(identity)
        for folder in row.get('folders',[]):
            parts=PurePosixPath(folder).parts
            if len(parts)!=3 or '..'in parts or PurePosixPath(folder).is_absolute():errors.append(f'{rid}: unsafe folder')
            elif not(root/folder/'README.md').is_file():errors.append(f'{rid}: missing model folder {folder}')
        if not row.get('folders'):errors.append(f'{rid}: missing folder navigation')
    for path in json.loads((root/'data/generated-files.json').read_text()):
        if not(root/path).is_file():errors.append(f'Missing generated file {path}')
    page=(root/'index.html').read_text();match=re.search(r'<script id="catalogue" type="application/json">(.*?)</script>',page,re.S)
    embedded=json.loads(match.group(1))if match else []
    if {r['id']for r in embedded}!=ids:errors.append('Browser index differs from catalogue')
    errors.extend(date_errors(data))
    standards=json.loads((root/'data/standards.json').read_text())
    errors.extend(standards_errors(standards))
    embedded_standards=re.search(r'<script id="standards-data" type="application/json">(.*?)</script>',page,re.S)
    if not embedded_standards or json.loads(embedded_standards.group(1))!=standards:errors.append('Browser standards register differs from source')
    standard_doc=root/'05-british-standards/README.md'
    if not standard_doc.is_file()or standard_doc.read_text()!=render_standards_markdown(standards).rstrip()+'\n':errors.append('Standards navigation is missing or stale')
    for filename,expected in [('app-manifest.json',build_manifest(data)),('gap-audit.json',build_gap_audit(data))]:
        path=root/'data'/filename
        if not path.is_file()or json.loads(path.read_text())!=expected:errors.append(f'{filename}: missing or stale generated data')
    return errors,{'records':len(rows),'brands':len({r['brand']for r in rows}),'categories':dict(collections.Counter(r['category']for r in rows)),'direct_pdf_links':sum(bool(r.get('download_url'))for r in rows)}
if __name__=='__main__':
    errors,summary=validate()
    print(json.dumps(summary,indent=2))
    if errors:
        for error in errors:print('ERROR:',error)
        sys.exit(1)
    print('Catalogue, model folders and offline browser index are consistent.')
