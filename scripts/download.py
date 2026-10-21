#!/usr/bin/env python3
"""Download selected manufacturer PDFs locally, retaining content-addressed versions.

Uses Python's standard library. Downloads and reports are gitignored. Never signs in,
bypasses a gate, or treats an HTML download/challenge page as a PDF.
"""
import argparse,hashlib,json,re,sys,time,urllib.error,urllib.request
from datetime import datetime,timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin,urlparse

ROOT=Path(__file__).resolve().parents[1]
MAX_BYTES=100*1024*1024
def slug(value):return re.sub(r'[^a-z0-9]+','-',value.lower()).strip('-')[:100]or 'unspecified'
def read_catalogue(path=ROOT/'data/catalogue.json'):return json.loads(Path(path).read_text())['records']
def matching(records,category=None,brand=None,model=None,record_id=None):
    return [r for r in records if (not category or r['category']==category)and(not brand or slug(r['brand'])==slug(brand))and(not model or model.casefold()in ' '.join(r['models']).casefold())and(not record_id or r['id']==record_id)]
def http_url(url):
    p=urlparse(url)
    if p.scheme not in ('http','https')or not p.hostname or p.username or p.password:raise ValueError('Expected a public HTTP(S) manufacturer URL')
    return url
class PDFLinks(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a'and re.search(r'/download/[^?]+\.pdf(?:\?|$)',a.get('href',''),re.I):self.links.append(a['href'])
def pdf_url(record,opener=urllib.request.urlopen):
    if record.get('download_url'):return http_url(record['download_url'])
    url=record['document_url']
    # Axis publishes one explicit PDF export on each model's online manual page.
    # Never choose the first PDF from a manufacturer index with unrelated documents.
    if record['brand']=='Axis'and urlparse(url).hostname=='help.axis.com':
        with opener(http_url(url),timeout=20)as response:
            if response.status!=200:raise ValueError(f'Online manual returned HTTP {response.status}')
            parser=PDFLinks();parser.feed(response.read(1024*1024).decode('utf-8',errors='replace'))
            if parser.links:return http_url(urljoin(response.url,parser.links[0]))
    return None
def file_hash(path):
    digest=hashlib.sha256()
    with Path(path).open('rb')as source:
        for chunk in iter(lambda:source.read(1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()
def fetch_pdf(url,temp,opener=urllib.request.urlopen,max_bytes=MAX_BYTES):
    digest=hashlib.sha256();size=0;head=b'';tail=b''
    try:
        with opener(http_url(url),timeout=30)as response,temp.open('xb')as target:
            if response.status!=200:raise ValueError(f'HTTP {response.status}; no PDF saved')
            declared=response.headers.get('Content-Length')
            if declared and int(declared)>max_bytes:raise ValueError('PDF exceeds size limit')
            for chunk in iter(lambda:response.read(65536),b''):
                size+=len(chunk)
                if size>max_bytes:raise ValueError('PDF exceeds size limit')
                head=(head+chunk)[:1024];tail=(tail+chunk)[-4096:]
                if size<=65536 and b'%PDF-'not in head:raise ValueError('Response is not a PDF (possibly a login or challenge page)')
                digest.update(chunk);target.write(chunk)
            if not size or b'%PDF-'not in head or b'%%EOF'not in tail:raise ValueError('PDF is empty, incomplete or lacks its expected trailer')
            if declared and size!=int(declared):raise ValueError('Incomplete response: byte count differs from Content-Length')
            return {'sha256':digest.hexdigest(),'bytes':size,'resolved_url':response.url}
    except BaseException:
        temp.unlink(missing_ok=True);raise
def atomic_json(path,value):
    temporary=path.with_suffix('.tmp');temporary.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n');temporary.replace(path)
def catalogue_comparison(record,sha256,size):
    expected=record.get('source_pdf_sha256');expected_size=record.get('source_pdf_bytes')
    state='unverified'if not expected else 'matched'if sha256==expected and(expected_size is None or size==expected_size)else 'changed'
    return {'catalogue_match':state,'catalogue_sha256':expected,'catalogue_bytes':expected_size}
def download_record(record,output,previous=None,refresh=False,opener=urllib.request.urlopen):
    output=Path(output).resolve();previous=previous or {}
    if not refresh and previous.get('path'):
        existing=(output/previous['path']).resolve()
        if existing.is_relative_to(output)and existing.is_file()and file_hash(existing)==previous.get('sha256'):
            return {**previous,**catalogue_comparison(record,previous['sha256'],existing.stat().st_size),'result':'already-saved'}
    url=pdf_url(record,opener)
    if not url:return {'id':record['id'],'result':'manual-download-needed','source_url':record['document_url']}
    folder=output/record['category']/slug(record['brand'])/slug(record['models'][0]);folder.mkdir(parents=True,exist_ok=True)
    # Record IDs and generated path segments cannot supply arbitrary local paths.
    record_id=slug(record['id']);temp=folder/(record_id+f'.{time.time_ns()}.part')
    info=fetch_pdf(url,temp,opener)
    name=slug(record.get('document_number')or record['title'])[:75]+'--'+record_id+'--'+info['sha256'][:12]+'.pdf'
    target=folder/name
    if target.exists():
        if file_hash(target)!=info['sha256']:temp.unlink(missing_ok=True);raise ValueError('An existing version has changed locally; it was not overwritten')
        temp.unlink()
    else:temp.replace(target)
    return {'id':record['id'],'title':record['title'],'models':record['models'],'path':target.relative_to(output).as_posix(),'downloaded_at':datetime.now(timezone.utc).isoformat(),'source_url':record['source_url'],'requested_url':url,**info,**catalogue_comparison(record,info['sha256'],info['bytes']),'result':'saved','validation':'PDF header, EOF marker, byte count and SHA-256; exact model/revision still needs human review'}
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--category',choices=['fire','security','access-control','cctv']);parser.add_argument('--brand');parser.add_argument('--model');parser.add_argument('--id')
    parser.add_argument('--all',action='store_true',help='Select the whole catalogue; may download many GB')
    parser.add_argument('--limit',type=int);parser.add_argument('--list',action='store_true',help='Print matching records without downloading')
    parser.add_argument('--refresh',action='store_true',help='Fetch again and preserve a new file if source contents changed')
    parser.add_argument('--output',type=Path,default=ROOT/'downloads');parser.add_argument('--delay',type=float,default=.5)
    args=parser.parse_args()
    if not any([args.category,args.brand,args.model,args.id,args.all]):parser.error('Choose a category, brand, model, id or --all')
    if args.limit is not None and args.limit<1:parser.error('--limit must be positive')
    if args.delay<0:parser.error('--delay cannot be negative')
    rows=matching(read_catalogue(),args.category,args.brand,args.model,args.id)
    if args.limit:rows=rows[:args.limit]
    if not rows:print('No matching records.');return 1
    if args.list:
        for row in rows:print(row['id'],row['brand'],' / '.join(row['models']),row['title'],sep=' | ')
        print(f'{len(rows)} records');return 0
    args.output.mkdir(parents=True,exist_ok=True);manifest=args.output/'download-manifest.json'
    data=json.loads(manifest.read_text())if manifest.exists()else {'schema_version':1,'files':{},'history':[],'attempts':[]}
    failures=0
    for i,row in enumerate(rows,1):
        try:
            previous=data['files'].get(row['id']);result=download_record(row,args.output,previous,args.refresh)
            if result['result']in ['saved','already-saved']:
                if previous and previous.get('sha256')!=result['sha256']:data['history'].append(previous)
                data['files'][row['id']]=result
            if result['result']=='manual-download-needed':failures+=1
        except Exception as error:
            failures+=1;result={'id':row['id'],'result':'failed','error':str(error),'source_url':row['document_url']}
        data['attempts'].append({**result,'attempted_at':datetime.now(timezone.utc).isoformat()});atomic_json(manifest,data)
        review=' (source differs from catalogue; review edition)'if result.get('catalogue_match')=='changed'else ''
        print(f"{i}/{len(rows)} {result['result']}{review}: {row['brand']} — {row['title']}",flush=True)
        if i<len(rows):time.sleep(args.delay)
    print(f'Local manifest: {manifest}. {failures} records need attention.');return 2 if failures else 0
if __name__=='__main__':sys.exit(main())
