#!/usr/bin/env python3
"""Download public FACP PDF candidates to a resumable local evidence cache.

Run beside collect_facp.py to overlap collection and byte checks. Private local
PDFs and extracted cover text are never copied into the public repository.
"""
import argparse, concurrent.futures, hashlib, json, re, subprocess, time
from pathlib import Path
from urllib.parse import urlparse
from collect_facp import initial_data
from download import fetch_pdf, file_hash

def check(item,directory):
    url=item['s3Url'];key=hashlib.sha256(url.encode()).hexdigest();path=directory/'pdfs'/(key+'.pdf');meta=directory/'checks'/(key+'.json');cover=directory/'covers'/(key+'.txt')
    if meta.exists():
        cached=json.loads(meta.read_text())
        if cached.get('status')=='complete-file'and path.exists()and path.stat().st_size==cached['bytes']and file_hash(path)==cached['sha256']:return cached
    result={'source_url':url,'checked_on':'2026-10-21'}
    if urlparse(url).scheme!='https'or urlparse(url).hostname!='docs.facpmanuals.com':
        result.update(status='needs-review',error='Unexpected document host; not followed automatically')
    else:
        errors=[]
        for attempt in range(2):
            temporary=path.with_suffix('.'+str(time.time_ns())+'.part')
            try:
                info=fetch_pdf(url,temporary,max_bytes=512*1024*1024)
                parsed=subprocess.run(['pdfinfo',str(temporary)],capture_output=True,text=True,timeout=45)
                match=re.search(r'^Pages:\s+(\d+)',parsed.stdout,re.M)
                if parsed.returncode or not match:raise ValueError('PDF parser rejected file')
                if temporary.stat().st_size!=info['bytes']or file_hash(temporary)!=info['sha256']:raise ValueError('Saved bytes differ from received content')
                temporary.replace(path)
                # Two pages are enough to identify obvious non-fire documents and
                # inspect title/edition metadata. Do not publish extracted text.
                subprocess.run(['pdftotext','-f','1','-l',str(min(2,int(match[1]))),'-layout',str(path),str(cover)],capture_output=True,timeout=30)
                result.update(status='complete-file',**info,page_count=int(match[1]),pdf_header_checked=True,pdf_eof_checked=True)
                break
            except Exception as error:
                temporary.unlink(missing_ok=True);errors.append(str(error))
                if attempt==0:time.sleep(1)
        if result.get('status')!='complete-file':result.update(status='retrieval-failed',errors=errors)
    temp=meta.with_suffix('.'+str(time.time_ns())+'.tmp');temp.write_text(json.dumps(result,indent=2)+'\n');temp.replace(meta);time.sleep(.15);return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--workspace',type=Path,required=True);p.add_argument('--workers',type=int,default=6);p.add_argument('--watch',action='store_true');a=p.parse_args()
    for name in ['pdfs','checks','covers']:(a.workspace/name).mkdir(exist_ok=True)
    seen_pages=set();seen_urls=set();pending={};counts={'complete-file':0,'retrieval-failed':0,'needs-review':0};download_bytes=0;finished=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(max(a.workers,1),32))as pool:
        while True:
            inventory=a.workspace/'inventory.json'
            for page in [*(a.workspace/'brand-pages').glob('*.html'),*(a.workspace/'supplemental-pages').glob('*.html')]:
                if page in seen_pages:continue
                try:data=initial_data(page.read_text())
                except Exception:continue
                seen_pages.add(page)
                for item in data['manuals']:
                    if not item.get('s3Url')or item['s3Url']in seen_urls:continue
                    seen_urls.add(item['s3Url']);pending[pool.submit(check,item,a.workspace)]=item['id']
            done=[future for future in pending if future.done()]
            for future in done:
                result=future.result();pending.pop(future);counts[result['status']]+=1;download_bytes+=result.get('bytes',0);finished+=1
                if finished%100==0:print(json.dumps({'finished':finished,'queued':len(seen_urls),'pending':len(pending),'bytes':download_bytes,**counts}),flush=True)
            progress={'finished':finished,'queued':len(seen_urls),'pending':len(pending),'bytes':download_bytes,**counts}
            (a.workspace/'download-progress.json').write_text(json.dumps(progress)+'\n')
            if not pending and(inventory.exists()or not a.watch):break
            time.sleep(1)
    print(json.dumps({'done':True,**progress}),flush=True)

if __name__=='__main__':main()
