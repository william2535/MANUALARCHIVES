#!/usr/bin/env python3
"""Rebuild repository navigation and a self-contained offline catalogue browser."""
import collections,html,json,re,unicodedata
from pathlib import Path
from app_data import build_manifest, build_gap_audit, download_info
from standards_data import standards_errors, render_standards_markdown
ROOT=Path(__file__).resolve().parents[1]
CATEGORIES={'fire':('01-fire','Fire'),'security':('02-security','Security / intruder'),'access-control':('03-access-control','Access control / door entry'),'cctv':('04-cctv','CCTV'),'warden-call':('06-warden-call','Warden call / telecare / nurse call')}
def slug(value):
    value=unicodedata.normalize('NFKD',value).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+','-',value).strip('-')[:100]or 'unspecified'
def md(value):return str(value or 'Not recorded').replace('|','\\|').replace('\n',' ').replace('[','\\[').replace(']','\\]')
def main():
    catalogue=json.loads((ROOT/'data/catalogue.json').read_text());records=catalogue['records'];generated=[]
    standards=json.loads((ROOT/'data/standards.json').read_text())
    problems=standards_errors(standards)
    if problems:raise ValueError('\n'.join(problems))
    previous=json.loads((ROOT/'data/generated-files.json').read_text())if(ROOT/'data/generated-files.json').exists()else []
    def write(path,text):
        target=ROOT/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text.rstrip()+'\n');generated.append(path)
    folders=collections.defaultdict(list);brands=collections.defaultdict(lambda:collections.defaultdict(set));counts=collections.Counter(r['category']for r in records)
    for row in records:
        row['folders']=[f"{CATEGORIES[row['category']][0]}/{slug(row['brand'])}/{slug(m)}"for m in row['models']]
        for model,folder in zip(row['models'],row['folders']):
            folders[folder].append(row);brands[row['category']][row['brand']].add((model,folder))
    (ROOT/'data/catalogue.json').write_text(json.dumps(catalogue,ensure_ascii=False,indent=2)+'\n')
    manifest=build_manifest(catalogue);gap_audit=build_gap_audit(catalogue)
    write('data/app-manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))
    write('data/gap-audit.json',json.dumps(gap_audit,ensure_ascii=False,indent=2))
    for folder,items in folders.items():
        first=items[0];model=next(m for m,f in zip(first['models'],first['folders'])if f==folder)
        lines=[f'# {md(first["brand"])} — {md(model)}','', '[Brand index](../README.md) · [Category index](../../README.md) · [Archive](../../../README.md)','', 'Source titles and model associations are navigation aids. Some legacy model names are taken from supplier filenames. Confirm the installed model, protocol, firmware, market and issue against the original document.','', '| Document | Type | Number | Revision hint | Availability | Source |','|---|---|---|---|---|---|']
        for r in sorted(items,key=lambda x:(x['title'],x['id'])):
            title=r['title']+(' (duplicate listing)'if r.get('duplicate_of')else'')
            url=r.get('download_url')or r['document_url'];lines.append(f'| [{md(title)}]({url}) | {r["document_type"]} | {md(r["document_number"])} | {md(r["revision_hint"])} | {r["availability"]} | [{md(r.get("source_kind", "manufacturer").title())}]({r["source_url"]}) |')
        lines+=['','Revision hints come from filenames unless stated otherwise. A source listing is not a downloaded file.','', 'Record IDs: '+', '.join('`'+r['id']+'`'for r in items), '', 'PDFs are not mirrored in this public repository. See [offline downloads](../../../README.md#offline-downloads).']
        write(folder+'/README.md','\n'.join(lines))
    for category,(directory,label)in CATEGORIES.items():
        scope=('Grouped living warden call, at-home telecare and related nurse-call documents. These are distinct system types; use the exact model and document. Standalone rescue-assistance systems remain under fire. See [social alarm standards](../05-british-standards/README.md#warden-call-and-social-alarms).'if category=='warden-call'else'Door entry belongs under access control.')
        lines=[f'# {label}','','[Archive](../README.md)', '',f'{counts[category]} document records. {scope}','', '| Brand | Document records | Model / family folders |','|---|---:|---:|']
        for brand,models in sorted(brands[category].items()):
            n=sum(r['category']==category and r['brand']==brand for r in records)
            lines.append(f'| [{md(brand)}]({slug(brand)}/README.md) | {n} | {len(models)} |')
            content=[f'# {md(brand)} — {label}','','[Category index](../README.md) · [Archive](../../README.md)','',f'{n} document records, grouped into {len(models)} model or product-family folders. Shared manuals may appear under several models; these are not additional documents.','', '| Model / family | Documents |','|---|---:|']
            for model,folder in sorted(models):content.append(f'| [{md(model)}]({folder.rsplit("/",1)[1]}/README.md) | {len(folders[folder])} |')
            write(f'{directory}/{slug(brand)}/README.md','\n'.join(content))
        write(directory+'/README.md','\n'.join(lines))
    availability=collections.Counter(r['availability']for r in records);brand_counts=collections.Counter(r['brand']for r in records);type_counts=collections.Counter(r['document_type']for r in records);direct=sum(bool(r.get('download_url'))for r in records)
    readme=['# FESS Manual Archives','','Fire, security, access control, CCTV, warden call, telecare and nurse-call manuals and technical references, organised for the FESS onsite guide. This is a growing source catalogue, not a complete collection of every manufacturer or model.','',f'**{len(records):,} document records · {len(brand_counts)} brands · {direct:,} direct PDF links · 0 PDF files mirrored**','',f'Source collection date: {catalogue["generated_on"]}. A check date does not mean a document is the latest revision.','', '## Browse by system','','| Category | Documents |','|---|---:|']
    for key,(directory,label)in CATEGORIES.items():readme.append(f'| [{label}]({directory}/README.md) | {counts[key]:,} |')
    readme+=['','Each category contains **brand → model / product family → document** navigation. Documents are classified as installation, user guide, programming, quick start, application note, diagram, datasheet or reference. Shared documents are linked under all explicitly associated models without counting each model association as a separate document.','','## Search and app data','','- Download or clone this repository, then open **`index.html`** in your browser. Its catalogue and search work offline; opening source documents requires a connection until you download them.','- [`data/catalogue.json`](data/catalogue.json) is the structured source for app integration. It contains stable IDs, categories, models, document types, source URLs, direct PDF URLs where found, and availability records.','- [Coverage and gaps](COVERAGE.md) separates confirmed PDF retrieval metadata, published PDF links, online manuals and unresolved sources.','','## Offline downloads','','Requires Python 3.10 or later; no extra packages. Download only material you are entitled to use under the publisher’s terms.','','Preview a selection:','','```bash','python3 scripts/download.py --category fire --brand "C-TEC" --list','```','','Download that brand’s available PDFs locally:','','```bash','python3 scripts/download.py --category fire --brand "C-TEC"','python3 scripts/download.py --category security --brand Texecom','python3 scripts/download.py --category access-control --brand Paxton','python3 scripts/download.py --category cctv --brand Axis --model P3245','python3 scripts/download.py --category warden-call --brand Tynetec','```','','Use `--limit 5` for a small first batch. `--all` selects the whole catalogue and can download many GB. `--refresh` checks the selected sources again; changed contents get a separate file, retaining old versions.','','Files go into `downloads/category/brand/model/`. The gitignored `downloads/download-manifest.json` records source URLs, download time, exact byte counts, SHA-256 checksums, results and retained version history. Interrupted or non-PDF responses are removed. Source-only entries, login pages and blocked requests are reported for manual attention. The tool can resolve Axis’s explicit PDF export from its model manual page.','','A successful download checks the file header, trailer and integrity; it does not certify technical applicability. Open each required PDF and check it before going on site.','','## What is stored here','','The repository stores original indexing work and links. Manufacturer sources are preferred; public installer, distributor and independent archive copies are labelled separately with `source_kind`. Some legacy titles and model associations come from abbreviated filenames and need document-level review. It does **not** republish copyrighted manufacturer PDFs. Publicly accessible downloads do not themselves establish permission to redistribute. See [document rights](RIGHTS.md).','','This archive includes older editions and multiple languages. Unknown language, market or revision information stays explicitly unverified. Engineering manuals, application notes and datasheets are not interchangeable. No passwords, default-code lists, customer records or paid standards have been extracted into the catalogue.','','## Maintain the archive','','```bash','python3 scripts/build_index.py','python3 scripts/validate.py','python3 -m unittest discover -s tests -v','node tests/test_browser.cjs','```','','See [contribution guidance](CONTRIBUTING.md).']
    app_lines=['','## Phone app foundation','','[`data/app-manifest.json`](data/app-manifest.json) is the versioned download feed for a phone app. It keeps stable record IDs, model associations, source provenance, verification dates, file sizes and SHA-256 checksums where known. A direct link alone is not a verified download.','',f'Current evidence: **{manifest["download_status_counts"].get("complete-file",0):,} complete-file checks**; other records retain their actual evidence level. The feed never claims a manual is saved on a device.','', 'See [app integration](APP_INTEGRATION.md) for the feed contract, download validation, local storage and version retention. The archive remains the catalogue; a phone app must download and retain the selected PDFs before offline use.','','[`data/gap-audit.json`](data/gap-audit.json) audits every record and model association, with review flags and counts by brand. It is regenerated with the catalogue.']
    readme[readme.index('## Offline downloads')-1:readme.index('## Offline downloads')-1]=app_lines
    readme=[line.replace('Source collection date:', 'Catalogue build date:') for line in readme]
    section=['','## British Standards updates and revisions','',f'**{len(standards["records"])} checked references across {len(standards["categories"])} groups**, covering fire, security, access control, CCTV, social alarms and supporting lighting/electrical references. The section includes current editions, amendment labels, public revision summaries, earlier records and confirmed transition dates. Checked {standards["checked_on"]}.','','[Browse the standards section](05-british-standards/README.md) · [Search standards offline](index.html#standards) · [App data](data/standards.json)','','The register identifies gaps explicitly; it is not a complete history of every BS amendment. Full licensed standard texts are obtained from the publisher. The archive stores metadata and original short summaries.']
    position=readme.index('## Search and app data')-1
    readme[position:position]=section
    write('README.md','\n'.join(readme))
    write('05-british-standards/README.md',render_standards_markdown(standards))
    coverage=['# Coverage and outstanding work','',f'Collection date: {catalogue["generated_on"]}. Counts are catalogue records, not downloaded files or a claim of completeness.','','## Brands','','| Brand | Records | Direct PDF links |','|---|---:|---:|']
    for brand,n in sorted(brand_counts.items()):coverage.append(f'| {brand} | {n} | {sum(r["brand"]==brand and bool(r.get("download_url"))for r in records)} |')
    coverage+=['','## Availability','','| Status | Records | Meaning |','|---|---:|---|']
    meanings={'pdf-indexed':'PDF retrieved and page count identified. Per-record evidence distinguishes retrieval-service indexing from complete-file local checks; no copy is mirrored here.','pdf-link-listed':'A PDF download was listed by the cited source; per-record header or checksum evidence is retained where checked.','online-manual':'Manufacturer publishes a web manual; use its PDF export or print option where available.','document-viewer':'Manufacturer links to a document viewer; download manually through that viewer.','source-listing':'Document title listed by manufacturer; a usable direct download is still unresolved.','retrieval-failed':'Source was identified but retrieval failed or exceeded the retrieval service’s limits.'}
    for status,n in sorted(availability.items()):coverage.append(f'| {status} | {n} | {meanings[status]} |')
    coverage+=['','## Document types','','| Type | Records |','|---|---:|']+[f'| {k} | {v} |'for k,v in sorted(type_counts.items())]
    audit=json.loads((ROOT/'data/coverage-audit.json').read_text())
    source_counts=collections.Counter(r.get('source_kind','manufacturer')for r in records)
    coverage+=['','## Source provenance','','| Source type | Records |','|---|---:|']+[f'| {k} | {v} |'for k,v in sorted(source_counts.items())]
    coverage+=['','Manufacturer sources are preferred. Installer, distributor and independent archive copies are explicitly labelled; filenames are navigation aids and may be abbreviated. A listed PDF URL is not evidence of technical applicability or a current issue.','','## This expansion','']+['- '+x for x in audit['completed']]
    coverage+=['','## Known gaps','']+['- '+x for x in audit['remaining']]
    unresolved=[r for r in records if not r.get('download_url')]
    coverage+=['','## Records without direct PDF links','','| Brand | Records |','|---|---:|']+[f'| {k} | {v} |'for k,v in sorted(collections.Counter(r['brand']for r in unresolved).items())]
    coverage+=['','The full queue is in [data/research-backlog.json](data/research-backlog.json). These counts include valid web manuals as well as unresolved listings; they are not all broken links.','','## Sources','']
    for brand in sorted(brand_counts):
        sources=sorted({r['source_url']for r in records if r['brand']==brand})
        coverage.append(f'- **{brand}**: '+', '.join(f'[source {i+1}]({u})'for i,u in enumerate(sources)))
    coverage+=['','## Record-level gap audit','','This audit covers every indexed record, with model/type coverage for every recorded model association. It does not establish completeness against products that have never been indexed. Valid web manuals and unresolved PDF links are counted separately.','','| Review flag | Records |','|---|---:|']+[f'| {k} | {v:,} |'for k,v in gap_audit['gap_counts'].items()]
    coverage+=['','See [machine-readable gap audit](data/gap-audit.json) for exact record IDs, per-brand counts and model coverage. Flags overlap; do not add them together as a count of missing manuals.','','## Download evidence','','| Evidence / status | Records |','|---|---:|']+[f'| {k} | {v:,} |'for k,v in manifest['download_status_counts'].items()]
    coverage+=['','Complete-file checks include a recorded SHA-256, size, PDF header and EOF marker. File-hash records have a checksum but lack that full validation trail. PDF-indexed means a retrieval service identified a PDF and page count; it is not a locally verified file. See [app integration](APP_INTEGRATION.md).']
    coverage=[line.replace('Collection date:', 'Catalogue build date:') for line in coverage]
    write('COVERAGE.md','\n'.join(coverage))
    # Embed only catalogue metadata; the browser does not fetch any third-party content until clicked.
    browser_records=[{k:r[k]for k in ['id','category','brand','models','title','document_type','document_number','revision_hint','availability','source_url','document_url','download_url','folders','source_kind','model_basis']}for r in records]
    for browser_row,row in zip(browser_records,records):
        browser_row['download']=download_info(row)
        if row.get('duplicate_of'):browser_row['duplicate_of']=row['duplicate_of']
    template=(ROOT/'scripts/index-template.html').read_text()
    template=template.replace('__STANDARDS_DATA__',json.dumps(standards,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')).replace('__STANDARDS_SCRIPT__',(ROOT/'scripts/standards-browser.js').read_text())
    write('index.html',template.replace('__CATALOGUE_DATA__',json.dumps(browser_records,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')).replace('__COUNT__',f'{len(records):,}').replace('__DATE__',catalogue['generated_on']))
    write('data/generated-files.json',json.dumps(sorted(generated),indent=2))
    for old in set(previous)-set(generated):
        target=(ROOT/old).resolve()
        if target.is_relative_to(ROOT)and target.name=='README.md'and old.split('/')[0]in [v[0]for v in CATEGORIES.values()]:target.unlink(missing_ok=True)
    print(f'Built {len(generated)} files for {len(records)} records, {len(folders)} model/family folders, {len(brand_counts)} brands.')
if __name__=='__main__':main()
