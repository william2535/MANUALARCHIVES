// Embedded by build_index.py: search metadata stays available offline; PDFs need downloading.
const standardsData=JSON.parse($('standards-data').textContent);
const freeResources=standardsData.free_resources||[];
let standardsLimit=25;
function resourcesFor(r){return freeResources.filter(f=>f.related_standard_ids.includes(r.id));}
const standardsRows=standardsData.records.map(r=>({record:r,search:normal([r.edition,r.title,r.category,r.change_summary||'',...r.supersedes,...r.earlier_records.map(e=>e.edition),...resourcesFor(r).map(f=>[f.title,f.publisher,f.scope_note].join(' '))].join(' '))}));
$('standards-checked').textContent=`${freeResources.length} free PDF guides, white papers and forms · links checked ${standardsData.free_resources_checked_on||'Not established'} · ${standardsData.records.length} reference records, status checked ${standardsData.checked_on}`;
$('standards-category').innerHTML='<option value="">All subjects</option>'+Object.entries(standardsData.categories).map(([key,label])=>`<option value="${h(key)}">${h(label)}</option>`).join('');
$('standards-access').value='free';
$('standards-gaps').innerHTML=standardsData.coverage.remaining_checks.map(t=>`<li>${h(t)}</li>`).join('');
$('standards-drafts').innerHTML=(standardsData.draft_watchlist||[]).map(d=>`<li><a href="${h(d.source_url)}" target="_blank" rel="noopener noreferrer">${h(d.reference)} — publisher reference, not a free download</a> — ${h(d.subject)} · BSI record ${h(d.publisher_record_date)}</li>`).join('');
function standardUpdateMatch(r){
  const value=$('standards-update').value;
  return !value || (value==='recent'&&Math.max(...[...r.edition.matchAll(/:(\d{4})/g)].map(m=>Number(m[1])))>=2024)
    || (value==='amended'&&r.amendments_in_designation.length>0)
    || (value==='summary'&&r.change_summary)
    || (value==='review'&&r.under_review)
    || (value==='withdrawn'&&r.status==='withdrawn');
}
function standardAccessMatch(r){
  const value=$('standards-access').value,available=resourcesFor(r).length>0;
  return value==='all'||(value==='free'&&available)||(value==='none'&&!available);
}
function standardDetails(r){
  const items=[`<li><a href="${h(r.source_url)}" target="_blank" rel="noopener noreferrer">Publisher record — reference only, may require payment</a></li>`,...r.notes.map(n=>`<li>${h(n)}</li>`),...r.earlier_records.map(e=>`<li>Earlier publisher record: <a href="${h(e.source_url)}" target="_blank" rel="noopener noreferrer">${h(e.edition)}</a> — ${h(e.publisher_status)}. ${h(e.note)}</li>`)];
  if(r.supersedes.length)items.push(`<li>Publisher-confirmed predecessor(s): ${h(r.supersedes.join(', '))}.</li>`);
  if(r.transition)items.push(`<li><strong>Transition end: ${h(r.transition.ends_on)}</strong>: ${h(r.transition.previous_edition)}. ${h(r.transition.note)} <a href="${h(r.transition.source_url)}" target="_blank" rel="noopener noreferrer">Official transition source</a></li>`);
  if(r.source_urls.length>1)items.push(`<li>More official information: ${r.source_urls.slice(1).map((url,i)=>`<a href="${h(url)}" target="_blank" rel="noopener noreferrer">source ${i+1}</a>`).join(' · ')}</li>`);
  return `<details class="standard-sources"><summary>Publisher metadata and revision history (access may require payment)</summary><p class="meta"><span class="badge ${r.status==='withdrawn'?'withdrawn':''}">${h(r.publisher_status)}</span>BSI record date: ${h(r.publisher_record_date||'Not established')} · status checked ${h(r.source_checked)}<br>Amendment labels: ${h(r.amendments_in_designation.join(', ')||'None in designation')}</p><p class="standard-note">${h(r.change_summary||'Edition and status metadata only; detailed revision changes have not been verified.')}</p><ul>${items.join('')}</ul></details>`;
}
function resourceCard(f){
  const kind=f.resource_type==='model-forms'?'model forms':f.resource_type==='white-paper'?'white paper':'guide';
  return `<div class="free-resource"><span class="badge">Free ${h(kind)} · not the full standard</span>${f.edition_relation==='earlier-edition'?'<span class="badge withdrawn">Earlier-edition guidance</span>':''}<h4>${h(f.title)}</h4><p class="meta">${h(f.publisher)} · ${h(f.document_issue)} · ${f.page_count} pages</p><p class="resource-scope">${h(f.scope_note)}</p><div class="actions"><a class="primary" href="${h(f.download_url)}" target="_blank" rel="noopener noreferrer">Download free ${h(kind)} PDF ↗</a><span class="meta">Free PDF link checked ${h(f.checked_on)}</span></div></div>`;
}
function renderStandards(){
  const terms=$('standards-search').value.trim().split(/\s+/).map(normal).filter(Boolean);
  const list=standardsRows.filter(x=>terms.every(t=>x.search.includes(t))&&(!$('standards-category').value||x.record.category===$('standards-category').value)&&standardUpdateMatch(x.record)&&standardAccessMatch(x.record)).map(x=>x.record).sort((a,b)=>(b.publisher_record_date||'').localeCompare(a.publisher_record_date||'')||a.edition.localeCompare(b.edition));
  $('standards-count').textContent=`${list.length} references · showing ${Math.min(standardsLimit,list.length)}`;
  $('standards-more').hidden=list.length<=standardsLimit;
  $('standards-results').innerHTML=list.length?list.slice(0,standardsLimit).map(r=>{
    const resources=resourcesFor(r);
    return `<article class="standard-card"><div class="eyebrow">${h(standardsData.categories[r.category])}</div><h3>${h(r.edition)}</h3><p class="standard-title">${h(r.title)}</p><p class="standard-note"><strong>Full standard: no verified free download.</strong></p>${resources.length?`<div class="free-resources">${resources.map(resourceCard).join('')}</div>`:'<p class="no-free-resource">No verified free guide PDF for this reference yet.</p>'}${standardDetails(r)}</article>`;
  }).join(''):`<p class="empty">No matching references${$('standards-access').value==='free'?' with verified free PDF guides':''}. Try another subject or choose “All reference records”.</p>`;
}
for(const id of ['standards-search','standards-category','standards-update','standards-access'])$(id).addEventListener(id==='standards-search'?'input':'change',()=>{standardsLimit=25;renderStandards();});
$('standards-clear').addEventListener('click',()=>{for(const id of ['standards-search','standards-category','standards-update'])$(id).value='';$('standards-access').value='free';standardsLimit=25;renderStandards();});
$('standards-more').addEventListener('click',()=>{standardsLimit+=25;renderStandards();});
function showArchiveSection(){
  const standards=location.hash==='#standards';
  $('manual-panel').hidden=standards;$('standards-panel').hidden=!standards;
  $('nav-manuals').setAttribute('aria-current',standards?'false':'page');
  $('nav-standards').setAttribute('aria-current',standards?'page':'false');
}
window.addEventListener('hashchange',showArchiveSection);
renderStandards();showArchiveSection();
