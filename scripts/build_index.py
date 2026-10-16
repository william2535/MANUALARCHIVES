#!/usr/bin/env python3
"""Rebuild repository navigation and a self-contained offline catalogue browser."""
import collections,html,json,re,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CATEGORIES={'fire':('01-fire','Fire'),'security':('02-security','Security / intruder'),'access-control':('03-access-control','Access control / door entry'),'cctv':('04-cctv','CCTV')}
def slug(value):
    value=unicodedata.normalize('NFKD',value).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+','-',value).strip('-')[:100]or 'unspecified'
def md(value):return str(value or 'Not recorded').replace('|','\\|').replace('\n',' ').replace('[','\\[').replace(']','\\]')
def main():
    catalogue=json.loads((ROOT/'data/catalogue.json').read_text());records=catalogue['records'];generated=[]
    previous=json.loads((ROOT/'data/generated-files.json').read_text())if(ROOT/'data/generated-files.json').exists()else []
    def write(path,text):
        target=ROOT/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text.rstrip()+'\n');generated.append(path)
    folders=collections.defaultdict(list);brands=collections.defaultdict(lambda:collections.defaultdict(set));counts=collections.Counter(r['category']for r in records)
    for row in records:
        row['folders']=[f"{CATEGORIES[row['category']][0]}/{slug(row['brand'])}/{slug(m)}"for m in row['models']]
        for model,folder in zip(row['models'],row['folders']):
            folders[folder].append(row);brands[row['category']][row['brand']].add((model,folder))
    (ROOT/'data/catalogue.json').write_text(json.dumps(catalogue,ensure_ascii=False,indent=2)+'\n')
    for folder,items in folders.items():
        first=items[0];model=next(m for m,f in zip(first['models'],first['folders'])if f==folder)
        lines=[f'# {md(first["brand"])} — {md(model)}','', '[Brand index](../README.md) · [Category index](../../README.md) · [Archive](../../../README.md)','', 'Manufacturer titles and model associations are navigation aids. Confirm the installed model, protocol, firmware, market and issue against the original document.','', '| Document | Type | Number | Revision hint | Availability | Source |','|---|---|---|---|---|---|']
        for r in sorted(items,key=lambda x:(x['title'],x['id'])):
            url=r.get('download_url')or r['document_url'];lines.append(f'| [{md(r["title"])}]({url}) | {r["document_type"]} | {md(r["document_number"])} | {md(r["revision_hint"])} | {r["availability"]} | [Manufacturer]({r["source_url"]}) |')
        lines+=['','Revision hints come from filenames unless stated otherwise. A source listing is not a downloaded file.','', 'Record IDs: '+', '.join('`'+r['id']+'`'for r in items), '', 'PDFs are not mirrored in this public repository. See [offline downloads](../../../README.md#offline-downloads).']
        write(folder+'/README.md','\n'.join(lines))
    for category,(directory,label)in CATEGORIES.items():
        lines=[f'# {label}','','[Archive](../README.md)', '',f'{counts[category]} document records. Door entry belongs under access control.','', '| Brand | Document records | Model / family folders |','|---|---:|---:|']
        for brand,models in sorted(brands[category].items()):
            n=sum(r['category']==category and r['brand']==brand for r in records)
            lines.append(f'| [{md(brand)}]({slug(brand)}/README.md) | {n} | {len(models)} |')
            content=[f'# {md(brand)} — {label}','','[Category index](../README.md) · [Archive](../../README.md)','',f'{n} document records, grouped into {len(models)} model or product-family folders. Shared manuals may appear under several models; these are not additional documents.','', '| Model / family | Documents |','|---|---:|']
            for model,folder in sorted(models):content.append(f'| [{md(model)}]({folder.rsplit("/",1)[1]}/README.md) | {len(folders[folder])} |')
            write(f'{directory}/{slug(brand)}/README.md','\n'.join(content))
        write(directory+'/README.md','\n'.join(lines))
    availability=collections.Counter(r['availability']for r in records);brand_counts=collections.Counter(r['brand']for r in records);type_counts=collections.Counter(r['document_type']for r in records);direct=sum(bool(r.get('download_url'))for r in records)
    readme=['# FESS Manual Archives','','Manufacturer-source manuals and technical references, organised for the FESS onsite guide. This is a growing source catalogue, not a complete collection of every manufacturer or model.','',f'**{len(records):,} unique document records · {len(brand_counts)} brands · {direct:,} direct PDF links · 0 PDF files mirrored**','',f'Source collection date: {catalogue["generated_on"]}. A check date does not mean a document is the latest revision.','', '## Browse by system','','| Category | Documents |','|---|---:|']
    for key,(directory,label)in CATEGORIES.items():readme.append(f'| [{label}]({directory}/README.md) | {counts[key]:,} |')
    readme+=['','Each category contains **brand → model / product family → document** navigation. Documents are classified as installation, user guide, programming, quick start, application note, diagram, datasheet or reference. Shared documents are linked under all explicitly associated models without inflating the unique count.','','## Search and app data','','- Download or clone this repository, then open **`index.html`** in your browser. Its catalogue and search work offline; opening manufacturer documents requires a connection until you download them.','- [`data/catalogue.json`](data/catalogue.json) is the structured source for app integration. It contains stable IDs, categories, models, document types, source URLs, direct PDF URLs where found, and availability records.','- [Coverage and gaps](COVERAGE.md) separates confirmed PDF retrieval metadata, published PDF links, online manuals and unresolved sources.','','## Offline downloads','','Requires Python 3.10 or later; no extra packages. Download only material you are entitled to use under the publisher’s terms.','','Preview a selection:','','```bash','python3 scripts/download.py --category fire --brand "C-TEC" --list','```','','Download that brand’s available PDFs locally:','','```bash','python3 scripts/download.py --category fire --brand "C-TEC"','python3 scripts/download.py --category security --brand Texecom','python3 scripts/download.py --category access-control --brand Paxton','python3 scripts/download.py --category cctv --brand Axis --model P3245','```','','Use `--limit 5` for a small first batch. `--all` selects the whole catalogue and can download many GB. `--refresh` checks the selected sources again; changed contents get a separate file, retaining old versions.','','Files go into `downloads/category/brand/model/`. The gitignored `downloads/download-manifest.json` records source URLs, download time, exact byte counts, SHA-256 checksums, results and retained version history. Interrupted or non-PDF responses are removed. Source-only entries, login pages and blocked requests are reported for manual attention. The tool can resolve Axis’s explicit PDF export from its model manual page.','','A successful download checks the file header, trailer and integrity; it does not certify technical applicability. Open each required PDF and check it before going on site.','','## What is stored here','','The repository stores original indexing work and manufacturer links. It does **not** republish copyrighted manufacturer PDFs. Publicly accessible downloads do not themselves establish permission to redistribute. See [document rights](RIGHTS.md).','','This archive includes older editions and multiple languages. Unknown language, market or revision information stays explicitly unverified. Engineering manuals, application notes and datasheets are not interchangeable. No passwords, default-code lists, customer records or paid standards have been extracted into the catalogue.','','## Maintain the archive','','```bash','python3 scripts/build_index.py','python3 scripts/validate.py','python3 -m unittest discover -s tests -v','```','','See [contribution guidance](CONTRIBUTING.md).']
    write('README.md','\n'.join(readme))
    coverage=['# Coverage and outstanding work','',f'Collection date: {catalogue["generated_on"]}. Counts are unique document records, not downloaded files or a claim of completeness.','','## Brands','','| Brand | Records | Direct PDF links |','|---|---:|---:|']
    for brand,n in sorted(brand_counts.items()):coverage.append(f'| {brand} | {n} | {sum(r["brand"]==brand and bool(r.get("download_url"))for r in records)} |')
    coverage+=['','## Availability','','| Status | Records | Meaning |','|---|---:|---|']
    meanings={'pdf-indexed':'Retrieval service identified a PDF and its page count; this is not a local copy.','pdf-link-listed':'A direct PDF link was found on a manufacturer source; full file not downloaded by this collection.','online-manual':'Manufacturer publishes a web manual; use its PDF export or print option where available.','document-viewer':'Manufacturer links to a document viewer; download manually through that viewer.','source-listing':'Document title listed by manufacturer; a usable direct download is still unresolved.','retrieval-failed':'Source was identified but retrieval failed or exceeded the retrieval service’s limits.'}
    for status,n in sorted(availability.items()):coverage.append(f'| {status} | {n} | {meanings[status]} |')
    coverage+=['','## Document types','','| Type | Records |','|---|---:|']+[f'| {k} | {v} |'for k,v in sorted(type_counts.items())]
    coverage+=['','## Known gaps','','- Source indexes are a starting set, not an exhaustive crawl of all products or historical revisions. The largest collections here are the published Axis, Kentec, C-TEC, Texecom, Paxton and Videx indexes.','- Ajax records cover the models visible on the retrieved device listing. Additional product pages remain to be collected.','- Advanced, Apollo, CDVI, Dahua, Eaton/Scantronic, Hikvision and Pyronix have partial coverage. Shared firmware manuals must be matched to the exact product; generic family folders do not imply every model is supported.','- More manufacturer work remains, including Gent, Honeywell/Notifier/Morley-IAS, Cooper fire systems, Orisec, Risco, Bosch, TDSi, Salto, Comelit, CAME/BPT, Fike, Protec, Ziton and Haes. No empty folders are counted as collected manuals.','- Some Kentec index links did not resolve through the retrieval service. The manufacturer listing and exact listed title are retained for those records.','- No claim is made that a PDF has redistribution permission, is the newest issue, or is correct for a particular installation.','- The public archive contains no original PDF binaries. Device downloads and their integrity records are created by the local downloader.','','## Sources','']
    for brand in sorted(brand_counts):
        sources=sorted({r['source_url']for r in records if r['brand']==brand})
        coverage.append(f'- **{brand}**: '+', '.join(f'[source {i+1}]({u})'for i,u in enumerate(sources)))
    write('COVERAGE.md','\n'.join(coverage))
    # Embed only catalogue metadata; the browser does not fetch any third-party content until clicked.
    browser_records=[{k:r[k]for k in ['id','category','brand','models','title','document_type','document_number','revision_hint','availability','source_url','document_url','download_url','folders']}for r in records]
    template=(ROOT/'scripts/index-template.html').read_text()
    write('index.html',template.replace('__CATALOGUE_DATA__',json.dumps(browser_records,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')).replace('__COUNT__',f'{len(records):,}').replace('__DATE__',catalogue['generated_on']))
    write('data/generated-files.json',json.dumps(sorted(generated),indent=2))
    for old in set(previous)-set(generated):
        target=(ROOT/old).resolve()
        if target.is_relative_to(ROOT)and target.name=='README.md'and old.split('/')[0]in [v[0]for v in CATEGORIES.values()]:target.unlink(missing_ok=True)
    print(f'Built {len(generated)} files for {len(records)} records, {len(folders)} model/family folders, {len(brand_counts)} brands.')
if __name__=='__main__':main()
