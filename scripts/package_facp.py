#!/usr/bin/env python3
"""Package privately downloaded FACP PDFs into resumable, verified ZIP volumes.

Never writes PDFs into the public Git tree. Every source listing is mapped in the
volume manifests; identical bytes share one PDF inside each volume. Volumes are
ordinary independent ZIP files, not a split archive requiring every part.
"""
import argparse
import hashlib
import html
import json
import re
import zipfile
from pathlib import Path
from download import file_hash, slug

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--max-mib',type=int,default=400)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    inventory=json.loads((args.workspace/'inventory.json').read_text())
    rows=inventory['records'];checks={}
    for row in rows:
        key=hashlib.sha256(row['s3Url'].encode()).hexdigest()
        meta=args.workspace/'checks'/(key+'.json')
        if not meta.exists():raise ValueError('Download check missing: '+row['id'])
        info=json.loads(meta.read_text())
        if info.get('status')!='complete-file':raise ValueError('Download incomplete: '+row['id'])
        checks[row['id']]={**info,'local_path':args.workspace/'pdfs'/(key+'.pdf')}
    volumes=[];current=[];size=0;hashes=set()
    for row in rows:
        info=checks[row['id']];increment=0 if info['sha256']in hashes else info['bytes']
        if current and size+increment>args.max_mib*1048576:
            volumes.append(current);current=[];size=0;hashes=set();increment=info['bytes']
        current.append(row);size+=increment;hashes.add(info['sha256'])
    if current:volumes.append(current)
    outputs=[]
    for n,entries in enumerate(volumes,1):
        first=slug(entries[0]['brand'])[:30];last=slug(entries[-1]['brand'])[:30]
        name=f'FACP-Manuals-{n:02d}-{first}'+(''if first==last else '-to-'+last)+'.zip'
        target=args.output/name;fingerprint=hashlib.sha256(json.dumps([(r['id'],checks[r['id']]['sha256'])for r in entries]).encode()).hexdigest()
        saved=args.output/(name+'.json')
        if saved.exists()and target.exists():
            cached=json.loads(saved.read_text())
            if cached['input_fingerprint']==fingerprint and cached['sha256']==file_hash(target):outputs.append(cached);continue
        temp=target.with_suffix('.part');manifest=[];paths={};written={}
        with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True)as z:
            for row in entries:
                info=checks[row['id']];digest=info['sha256']
                if digest not in paths:
                    path=info['local_path']
                    if path.stat().st_size!=info['bytes']or file_hash(path)!=digest:raise ValueError('Cached file changed: '+str(path))
                    filename=slug(row['title'])[:80]+'--'+row['id'][:8]+'--'+digest[:12]+'.pdf'
                    member=slug(row['brand'])+'/'+filename;paths[digest]=member;written[member]=info
                    z.write(path,member)
                manifest.append({'source_id':row['id'],'brand':row['brand'],'title':row['title'],
                                 'document_types':row.get('types',[]),'listed_year':row.get('year'),
                                 'source_url':row['source_url'],'download_url':row['s3Url'],
                                 'path':paths[digest],'sha256':digest,'bytes':info['bytes'],'pages':info['page_count']})
            z.writestr('manifest.json',json.dumps({'source':'FACP Manuals','checked_on':'2026-10-21','records':manifest},indent=2,ensure_ascii=False)+'\n')
            z.writestr('README.txt','FACP Manuals — private offline download volume\n\nUnzip this volume to open the PDFs without a connection. Each volume stands alone.\nThe manifest maps every source listing to its PDF, checksum and source URL.\nSource titles, years and model lists may be incomplete or inaccurate; check the original document.\nNo claim is made that a document is the current revision or applies to a UK installation.\nPublic availability does not grant redistribution rights.\n')
        # Read back every archived byte. A valid ZIP header alone is insufficient.
        with zipfile.ZipFile(temp)as z:
            for member,info in written.items():
                digest=hashlib.sha256();count=0
                with z.open(member)as stream:
                    for chunk in iter(lambda:stream.read(1048576),b''):digest.update(chunk);count+=len(chunk)
                if count!=info['bytes']or digest.hexdigest()!=info['sha256']:raise ValueError('ZIP verification failed: '+member)
        temp.replace(target)
        result={'filename':name,'local_path':str(target.resolve()),'bytes':target.stat().st_size,
                'sha256':file_hash(target),'source_listings':len(entries),'pdf_files':len(written),
                'brands':list(dict.fromkeys(r['brand']for r in entries)),
                'input_fingerprint':fingerprint}
        saved.write_text(json.dumps(result,indent=2)+'\n');outputs.append(result)
        print(json.dumps({k:v for k,v in result.items()if k not in ['brands','input_fingerprint']}),flush=True)
    result={'source_count':len(rows),'pdf_files_in_volumes':sum(v['pdf_files']for v in outputs),
            'download_bytes':sum(checks[r['id']]['bytes']for r in rows), 'volumes':outputs}
    (args.output/'FACP-Download-Volumes.json').write_text(json.dumps(result,indent=2)+'\n')
    links=''.join(f'<tr><td><a href="{html.escape(v["filename"])}">{html.escape(v["filename"])}</a></td><td>{v["source_listings"]:,}</td><td>{v["pdf_files"]:,}</td><td>{v["bytes"]/1048576:.1f} MB</td><td>{html.escape(", ".join(v["brands"]))}</td></tr>'for v in outputs)
    document='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>FACP offline manual downloads</title><style>body{font:16px system-ui;max-width:1200px;margin:40px auto;padding:0 20px;color:#172635}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #ddd;padding:12px;text-align:left}a{color:#086bc1}p{line-height:1.6}</style><h1>FACP offline manual downloads</h1><p><strong>'+f'{len(rows):,} source listings · {len(outputs)} independent ZIP volumes · checked 21 October 2026.</strong></p><p>Each volume opens on its own. Save it to Files on your phone and unzip it before going offline. Keep this index and the ZIP files in the same folder to use the links below.</p><p>All FACP document types and brands are included. Every PDF has a complete-file SHA-256, byte-count and PDF-parser check. These checks establish file integrity, not technical applicability or the latest edition. Identical files share a PDF within each volume; every listing remains in its manifest.</p><table><thead><tr><th>Volume</th><th>Listings</th><th>PDFs</th><th>Size</th><th>Brands</th></tr></thead><tbody>'+links+'</tbody></table><p><a href="https://github.com/william2535/MANUALARCHIVES">Searchable archive and individual document links</a></p></html>'
    (args.output/'FACP-Download-Index.html').write_text(document)
    print(json.dumps({'completed':len(outputs),'source_listings':len(rows),'pdf_files':result['pdf_files_in_volumes']}),flush=True)

if __name__=='__main__':main()
