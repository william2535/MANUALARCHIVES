#!/usr/bin/env python3
"""Reconcile every public FACP listing into the archive, retaining source identity.

Input is a complete collect_facp.py inventory and an optional complete-file cache.
No publication dates, primary model lists or latest editions are inferred from
FACP's filenames. A source listing is retained even when its PDF cannot be fetched.
"""
import argparse
import collections
import copy
import hashlib
import json
import re
from pathlib import Path
from build_index import slug

ROOT = Path(__file__).resolve().parents[1]
BRANDS = {'honeywell_gent': 'Gent', 'cooper': 'Eaton / Cooper',
          'eaton': 'Eaton / Cooper', 'ctec': 'C-TEC', 'morleyias': 'Morley-IAS'}
TYPE_MAP = {'Installation':'installation', 'Programming':'programming',
            'Operations':'user-guide', 'Operating Instructions':'user-guide',
            'User Guide':'user-guide', 'Datasheet':'datasheet',
            'Wiring Diagram':'diagram', 'Technical Reference':'reference',
            'Troubleshooting Guide':'troubleshooting', 'Application Guide':'application-note',
            'Quick Start':'quick-start', 'Catalog Page':'catalogue-page',
            'Brochure':'brochure', 'Compatibility Chart':'compatibility-chart',
            'Submittal Guide':'submittal-guide', 'Manual':'reference'}

def category_for(item):
    """Conservative navigation rules; never excludes a source document."""
    brand, title = item['brand_slug'], item['title'].casefold()
    if brand == 'linear': return 'warden-call'
    if brand == 'cornell_communications':
        return 'fire' if any(x in title for x in ['rescue','area of refuge']) else 'warden-call'
    if brand in {'wattmaster'}: return 'other-reference'
    if brand == 'andover_controls':
        if 'smoke control' in title: return 'fire'
        if title.startswith(('acx ', 'episuite')): return 'access-control'
        return 'other-reference'
    if brand == 'schneider_electric' and title == 'sitestat': return 'other-reference'
    if brand == 'johnson_controls':
        if title.startswith(('ahu ', 'cdt-', 'dx-', 'metasys', 'n1 ', 'n30', 'ncm300', 'site book')): return 'other-reference'
    if brand == 'siemens' and any(x in title for x in ['room automation', 'compact for electrical']): return 'other-reference'
    if brand == 'edwards_est' and any(x in title for x in ['clock','stacklight','industrial timer','industrial intercom','7000-hs','7000-sta','5570m']): return 'other-reference'
    if brand == 'united_security_products' and title == 'ad-2000': return 'security'
    if brand == 'telguard' and title == 'tg-7 series': return 'security'
    if brand == 'valcom': return 'other-reference'
    if brand == 'honeywell':
        if any(x in title for x in ['thermostat', 'air purifier', 'focuspro', 'visionpro', 'voyager', 'xenon']): return 'other-reference'
        if title.startswith(('cm907','c7355b','pro 3000','rth','th5000','th5220','th8000','th8320')): return 'other-reference'
        if title.startswith(('5800,','5878','6160','ademco 5843','lynx','tuxedo','vista-15','vista-20','vista-21','vista-128bpt')): return 'security'
    if brand == 'ge_security':
        if any(x in title for x in ['smoke','est3','vs1 and vs2']): return 'fire'
        if any(x in title for x in ['guardswitch','interlock','door position','291-f7','381-bt']): return 'access-control'
        return 'cctv'
    if brand == 'ditek':
        if any(x in title for x in ['cctv','video','vbnc','vsp','ibnc','vp','tpv']): return 'cctv'
        if 'access control' in title: return 'access-control'
        if 'intrusion' in title: return 'security'
        if any(x in title for x in ['fire','fpk','rm12fp']): return 'fire'
        return 'other-reference'
    if brand in {'paradox','qolsys','dsc'}: return 'security'
    if brand == 'elkron' and title.startswith('mp '): return 'security'
    if brand == 'adt' and 'focus' in title: return 'security'
    if brand == 'bosch':
        if title.startswith('d9210'): return 'access-control'
        if title.startswith(('b6512','b9512','d6412','d9412','conettix','d928')): return 'security'
    if brand == 'dmp' and title.startswith('xr'): return 'security'
    if brand == 'napco' and not any(x in title for x in ['fire','6024','cfb']): return 'security'
    if brand == 'radionics':
        if title.startswith(('easikey','d9210')): return 'access-control'
        if title.startswith(('d10024','d2071','d7024','d9024','d9124')): return 'fire'
        return 'security'
    if brand == 'ademco':
        if any(x in title for x in ['smoke','fire','heat detector']): return 'fire'
        if re.match(r'^(?:5806|5807|5808|vista-(?:32fb|128fb|250fb))\b',title): return 'fire'
        return 'security'
    return 'fire'

def evidence(row, check, checked_on):
    if check.get('status') == 'complete-file':
        row.update(availability='pdf-indexed', page_count=check['page_count'],
                   source_pdf_sha256=check['sha256'], source_pdf_bytes=check['bytes'],
                   pdf_header_checked=checked_on, pdf_eof_checked=True)
    elif check.get('status') == 'retrieval-failed' and not row.get('source_pdf_sha256'):
        row['availability'] = 'retrieval-failed'

def new_record(item, brand, checked_on):
    types=item.get('types') or ['Manual']
    return {'id':'facp-'+item['id'], 'category':category_for(item), 'brand':brand,
            'models':[item['title'].strip()],
            'model_basis':'FACP title; model applicability not verified.',
            'title':item['title'].strip()+' — '+', '.join(types)+((' ('+str(item['year'])+', source-listed)') if item.get('year') else ''),
            'document_type':TYPE_MAP.get(types[0],'reference'),
            **({'document_types':list(dict.fromkeys(TYPE_MAP.get(t,'reference')for t in types))} if len(types)>1 else {}),
            'document_number':None, 'revision_hint':None, 'revision_basis':'not-verified',
            'language':'not-verified', 'region':'not-verified',
            'source_url':'https://facpmanuals.com/manuals/'+item['brand_slug'], 'document_url':item['s3Url'],
            'download_url':item['s3Url'], 'availability':'pdf-link-listed',
            'page_count':None, 'source_checked':checked_on,
            'distribution':'source-link-only', 'local_pdf':None,
            'source_kind':'archive', 'source_collections':['facp']}

def import_records(catalogue, inventory, checks, checked_on):
    if inventory.get('failed_pages') or inventory.get('conflicts') or not all(x['complete'] for x in inventory['by_brand']):
        raise ValueError('FACP inventory is incomplete or conflicted; import refused')
    rows=copy.deepcopy(catalogue['records']); existing_ids={r['id'] for r in rows}
    # Collection membership describes this dated snapshot. Historical records and
    # earlier audits remain available if the source later removes a listing.
    for row in rows:
        if 'facp' in row.get('source_collections',[]):row['source_collections']=[c for c in row['source_collections']if c!='facp']
    names={r['brand'].casefold():r['brand'] for r in rows}; urls={}; hashes={}
    for r in rows:
        if r.get('duplicate_of'): continue
        for u in [r.get('download_url'),r.get('document_url'),*r.get('alternate_source_urls',[])]:
            if u: urls[(r['brand'],u)]=r
        if r.get('source_pdf_sha256'): hashes.setdefault((r['brand'],r['source_pdf_sha256']),r)
    outcomes=[]
    for item in inventory['records']:
        brand=BRANDS.get(item['brand_slug'],names.get(item['brand'].casefold(),item['brand']))
        check=checks.get(item['s3Url'],{}); digest=check.get('sha256') if check.get('status')=='complete-file' else None
        row=urls.get((brand,item['s3Url'])); match='same-url' if row else None
        if row is None and digest:
            row=hashes.get((brand,digest)); match='identical-complete-file' if row else None
        if row is None:
            row=new_record(item,brand,checked_on); rows.append(row); match='new'
        else:
            row.setdefault('source_collections',[])
            if 'facp' not in row['source_collections']: row['source_collections'].append('facp')
            if item['s3Url'] not in [row.get('download_url'),row.get('document_url')]:
                row.setdefault('alternate_source_urls',[])
                if item['s3Url'] not in row['alternate_source_urls']: row['alternate_source_urls'].append(item['s3Url'])
            if row['id'] in existing_ids and not row['id'].startswith('facp-') and item['source_url']!=row['source_url']:
                row.setdefault('associated_source_pages',[])
                if item['source_url'] not in row['associated_source_pages']: row['associated_source_pages'].append(item['source_url'])
        # A different mirror's full-file check must not be assigned to an unchecked
        # original URL. Identical hashes may identify mirrors without changing provenance.
        if row.get('download_url')==item['s3Url']: evidence(row,check,checked_on)
        urls[(brand,item['s3Url'])]=row
        if digest: hashes.setdefault((brand,digest),row)
        outcomes.append({'source_id':item['id'], 'source_url':item['source_url'],
                         'title':item['title'], 'brand':item['brand'], 'brand_slug':item['brand_slug'],
                         'download_url':item['s3Url'], 'document_types':item.get('types',[]),
                         'listed_year':item.get('year'), 'listed_bytes':item.get('fileSize'), 'record_id':row['id'], 'category':row['category'],
                         'result':match, 'download_status':check.get('status','not-checked'),
                         **({'sha256':digest,'bytes':check['bytes'],'page_count':check['page_count']} if digest else {}),
                         **({'errors':check.get('errors',[])} if check.get('status')=='retrieval-failed' else {})})
    if len({r['id'] for r in rows})!=len(rows): raise ValueError('Duplicate record ID')
    if not existing_ids.issubset({r['id'] for r in rows}): raise ValueError('Existing IDs lost')
    catalogue={**catalogue,'generated_on':checked_on,'records':rows}
    audit={'checked_on':checked_on,'source_url':inventory['source_url'],
           'scope':'Every public FACP brand listing, including non-fire documents, all types, languages and listed editions.',
           'classification_note':'Categories are navigation aids based on titles and source families. Primary models, language, region and current edition remain unverified unless separately evidenced. FACP referenced model lists are not promoted to primary applicability.',
           'source_count':len(outcomes),'source_brand_count':len(inventory['by_brand']),
           'listing_pages':inventory['page_count'],'supplemental_pages':inventory.get('supplemental_pages',0),'by_brand':inventory['by_brand'],
           'new_records':len(rows)-len(existing_ids),'mapped_records':len({x['record_id']for x in outcomes}),
           'download_status_counts':dict(collections.Counter(x['download_status']for x in outcomes)),
           'listed_size_differs_from_download_count':sum(x.get('bytes')is not None and x.get('listed_bytes')!=x['bytes']for x in outcomes),
           'size_note':'Source-listed sizes are preserved separately. Catalogue sizes and checksums describe the bytes actually delivered by the PDF URL, validated against its HTTP Content-Length when present.',
           'records':outcomes}
    return catalogue,audit

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--workspace',required=True,type=Path);p.add_argument('--checked-on',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
    inv=json.loads((a.workspace/'inventory.json').read_text())
    checks={d['source_url']:d for f in(a.workspace/'checks').glob('*.json') for d in [json.loads(f.read_text())]}
    catalogue,audit=import_records(json.loads((ROOT/'data/catalogue.json').read_text()),inv,checks,a.checked_on)
    dest=ROOT/'data' if a.apply else a.workspace/'preview';dest.mkdir(exist_ok=True)
    (dest/'catalogue.json').write_text(json.dumps(catalogue,ensure_ascii=False,separators=(',',':'))+'\n')
    target=dest/'source-audits'/('facp-full-'+a.checked_on+'.json') if a.apply else dest/'facp-audit.json';target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in audit.items() if k not in ['records','by_brand']},indent=2))

if __name__=='__main__': main()
