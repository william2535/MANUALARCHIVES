#!/usr/bin/env python3
"""Inventory FACP Manuals' public brand pages without login or private APIs.

The cache is resumable. This command only gathers candidates; it does not modify
the catalogue, infer primary model applicability, or claim files are downloaded.
"""
import argparse, concurrent.futures, hashlib, json, math, re, time, urllib.request
from pathlib import Path
from urllib.parse import urlencode

BASE='https://facpmanuals.com'

def flight_text(html):
    chunks=[]
    for script in re.findall(r'<script>(self\.__next_f\.push\(.*?)</script>',html,re.S):
        try:value=json.loads(script.removeprefix('self.__next_f.push(').removesuffix(')'))
        except (ValueError,TypeError):continue
        if isinstance(value,list)and len(value)>1 and value[0]==1 and isinstance(value[1],str):chunks.append(value[1])
    return ''.join(chunks)

def initial_data(html):
    text=flight_text(html)
    for match in re.finditer(r'"initialData":',text):
        try:value,_=json.JSONDecoder().raw_decode(text[match.end():])
        except ValueError:continue
        if isinstance(value,dict)and isinstance(value.get('manuals'),list)and isinstance(value.get('total'),int):return value
    raise ValueError('Public page contains no complete manual listing; not treated as an empty result')

def initial_brands(html):
    text=flight_text(html)
    for match in re.finditer(r'"initialBrands":',text):
        try:value,_=json.JSONDecoder().raw_decode(text[match.end():])
        except ValueError:continue
        if isinstance(value,list)and value and all(isinstance(b,dict)and all(k in b for k in ['name','slug','manualCount'])for b in value):return value
    raise ValueError('Public brand inventory missing; not treated as an empty collection')

def get(url,path,refresh=False):
    if path.exists()and not refresh:return path.read_text()
    errors=[]
    for attempt in range(3):
        try:
            request=urllib.request.Request(url,headers={'User-Agent':'ManualArchives public catalogue inventory','Accept':'text/html'})
            with urllib.request.urlopen(request,timeout=35)as response:
                if response.status!=200:raise ValueError('HTTP '+str(response.status))
                data=response.read(8*1024*1024+1)
            if len(data)>8*1024*1024:raise ValueError('Listing exceeds expected page size')
            text=data.decode('utf-8');temporary=path.with_suffix('.part');temporary.write_text(text);temporary.replace(path);return text
        except Exception as error:
            errors.append(str(error))
            if attempt<2:time.sleep(1+attempt)
    raise RuntimeError('; '.join(errors))

def collect_page(brand,number,cache,delay=.2):
    url=BASE+'/manuals/'+brand['slug']+'?'+urlencode({'page':number,'sortBy':'title','sortOrder':'asc'})
    path=cache/(brand['slug']+'-'+str(number)+'.html')
    result={'brand':brand['name'],'brand_slug':brand['slug'],'page':number,'source_url':url}
    try:
        data=initial_data(get(url,path))
        if data['page']!=number or data['brand']['slug']!=brand['slug']:raise ValueError('Response identity differs from requested page')
        if data['sortBy']!='title'or data['sortOrder']!='asc':raise ValueError('Stable title sort was not honoured')
        expected=min(data['pageSize'],max(0,data['total']-(number-1)*data['pageSize']))
        if len(data['manuals'])!=expected:raise ValueError('Incomplete listing page')
        result.update(status='collected',total=data['total'],page_size=data['pageSize'],manuals=data['manuals'])
    except Exception as error:result.update(status='failed',error=str(error))
    time.sleep(delay);return result

def reconcile(pages,brands,extras=()):
    records={};conflicts=[];summary=[]
    for page in [*pages,*extras]:
        for item in page.get('manuals',[]):
            # Referenced modelNumber values can be Flight string references and
            # include incidental parts; they are deliberately not applicability.
            value={k:item.get(k)for k in ['id','title','slug','s3Url','year','types','fileSize']}
            value.update(brand=page['brand'],brand_slug=page['brand_slug'],source_url=BASE+'/manuals/'+page['brand_slug']+'/'+item['slug'])
            previous=records.get(item['id'])
            if previous and previous!=value:conflicts.append({'id':item['id'],'first':previous,'later':value})
            else:records[item['id']]=value
    for brand in brands:
        selected=[p for p in pages if p['brand_slug']==brand['slug']];totals=sorted({p['total']for p in selected if p['status']=='collected'})
        count=sum(r['brand_slug']==brand['slug']for r in records.values())
        summary.append({'brand':brand['name'],'brand_slug':brand['slug'],'brand_index_count':brand['manualCount'],'page_totals':totals,'collected_unique':count,'failed_pages':[p['page']for p in selected if p['status']=='failed'],'complete':len(totals)==1 and count==totals[0]and all(p['status']=='collected'for p in selected)})
    return {'source_url':BASE+'/brands','scope':'All public brand listing pages; these include fire, security and other technical documents. Classification is a separate review.','records':sorted(records.values(),key=lambda r:(r['brand'],r['title'],r['id'])),'by_brand':summary,'conflicts':conflicts,'page_count':len(pages),'supplemental_pages':len(extras),'failed_pages':[p for p in pages if p['status']=='failed']}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--brands',type=Path,help='Previously saved brand inventory; omit to collect the public brand index');parser.add_argument('--output',type=Path,required=True);parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True);cache=args.output/'brand-pages';cache.mkdir(exist_ok=True)
    if args.brands:brands=json.loads(args.brands.read_text())['brands']
    else:
        brands=initial_brands(get(BASE+'/brands',args.output/'brands.html'))
        (args.output/'brands-parsed.json').write_text(json.dumps({'brands':brands},indent=2)+'\n')
    tasks=[(b,n)for b in brands for n in range(1,math.ceil(b['manualCount']/24)+1)]
    print(f'Collecting {len(tasks)} public pages for {len(brands)} brands',flush=True);pages=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(max(args.workers,1),6))as executor:
        pending=[executor.submit(collect_page,b,n,cache)for b,n in tasks]
        for future in concurrent.futures.as_completed(pending):
            value=future.result();pages.append(value)
            (args.output/'collection-progress.json').write_text(json.dumps({'pages_done':len(pages),'pages_expected':len(tasks),'failed':sum(p['status']=='failed'for p in pages),'last_brand':value['brand']}))
            if len(pages)%20==0 or value['status']=='failed':print(f"{len(pages)}/{len(tasks)} pages; {sum(p['status']=='failed'for p in pages)} failures; {value['brand']}",flush=True)
    # The site's title sort has no stable ID tie-breaker. A title spanning two
    # pages can repeat one UUID and omit a sibling. Re-query each boundary title,
    # then reconcile UUID totals instead of mistaking page counts for completeness.
    report=reconcile(pages,brands);extras=[];repair=args.output/'supplemental-pages';repair.mkdir(exist_ok=True)
    incomplete={b['brand_slug']for b in report['by_brand']if not b['complete']}
    seen={};queries={}
    for page in pages:
        if page['brand_slug']not in incomplete:continue
        for item in page.get('manuals',[]):
            if item['id']in seen:queries[(page['brand_slug'],item['title'])]=page['brand']
            seen[item['id']]=True
    for (brand_slug,title),brand_name in sorted(queries.items()):
        number=1
        while True:
            url=BASE+'/manuals/'+brand_slug+'?'+urlencode({'page':number,'sortBy':'title','sortOrder':'asc','q':title})
            key=hashlib.sha256(url.encode()).hexdigest();data=initial_data(get(url,repair/(key+'.html')))
            if data['brand']['slug']!=brand_slug or data.get('q')!=title:raise ValueError('Supplemental search identity mismatch')
            extras.append({'brand':brand_name,'brand_slug':brand_slug,'manuals':data['manuals'],'source_url':url})
            if number*data['pageSize']>=data['total']:break
            number+=1
        print('Reconciled boundary title: '+brand_name+' / '+title,flush=True)
    report=reconcile(pages,brands,extras);(args.output/'inventory.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'records':len(report['records']),'complete_brands':sum(b['complete']for b in report['by_brand']),'brands':len(brands),'failed_pages':len(report['failed_pages']),'conflicts':len(report['conflicts'])}),flush=True)
    return 0 if not report['failed_pages']and all(b['complete']for b in report['by_brand'])and not report['conflicts']else 2

if __name__=='__main__':raise SystemExit(main())
