// Embedded by build_index.py: all search data stays available offline.
const standardsData=JSON.parse($('standards-data').textContent);
let standardsLimit=25;
const standardsRows=standardsData.records.map(r=>({record:r,search:normal([r.edition,r.title,r.category,r.change_summary||'',...r.supersedes,...r.earlier_records.map(e=>e.edition)].join(' '))}));
$('standards-checked').textContent=`${standardsData.records.length} checked references · ${Object.keys(standardsData.categories).length} groups · checked ${standardsData.checked_on}`;
$('standards-category').innerHTML='<option value="">All subjects</option>'+Object.entries(standardsData.categories).map(([key,label])=>`<option value="${h(key)}">${h(label)}</option>`).join('');
$('standards-gaps').innerHTML=standardsData.coverage.remaining_checks.map(t=>`<li>${h(t)}</li>`).join('');
function standardUpdateMatch(r){
  const value=$('standards-update').value;
  return !value || (value==='recent'&&Math.max(...[...r.edition.matchAll(/:(\d{4})/g)].map(m=>Number(m[1])))>=2024)
    || (value==='amended'&&r.amendments_in_designation.length>0)
    || (value==='summary'&&r.change_summary)
    || (value==='review'&&r.under_review)
    || (value==='withdrawn'&&r.status==='withdrawn');
}
function standardDetails(r){
  const items=[...r.notes.map(n=>`<li>${h(n)}</li>`),...r.earlier_records.map(e=>`<li>Earlier record: <a href="${h(e.source_url)}" target="_blank" rel="noopener noreferrer">${h(e.edition)}</a> — ${h(e.publisher_status)}. ${h(e.note)}</li>`)];
  if(r.supersedes.length)items.unshift(`<li>Publisher-confirmed predecessor(s): ${h(r.supersedes.join(', '))}.</li>`);
  if(r.transition)items.unshift(`<li><strong>Transition end: ${h(r.transition.ends_on)}</strong>: ${h(r.transition.previous_edition)}. ${h(r.transition.note)} <a href="${h(r.transition.source_url)}" target="_blank" rel="noopener noreferrer">Official transition source</a></li>`);
  if(r.source_urls.length>1)items.push(`<li>More official information: ${r.source_urls.slice(1).map((url,i)=>`<a href="${h(url)}" target="_blank" rel="noopener noreferrer">source ${i+1}</a>`).join(' · ')}</li>`);
  return items.length?`<details><summary>Revision history and source notes</summary><ul>${items.join('')}</ul></details>`:'';
}
function renderStandards(){
  const terms=$('standards-search').value.trim().split(/\s+/).map(normal).filter(Boolean);
  const list=standardsRows.filter(x=>terms.every(t=>x.search.includes(t))&&(!$('standards-category').value||x.record.category===$('standards-category').value)&&standardUpdateMatch(x.record)).map(x=>x.record).sort((a,b)=>(b.publisher_record_date||'').localeCompare(a.publisher_record_date||'')||a.edition.localeCompare(b.edition));
  $('standards-count').textContent=`${list.length} references · showing ${Math.min(standardsLimit,list.length)}`;
  $('standards-more').hidden=list.length<=standardsLimit;
  $('standards-results').innerHTML=list.length?list.slice(0,standardsLimit).map(r=>`<article class="standard-card"><div><div class="eyebrow">${h(standardsData.categories[r.category])}</div><h3>${h(r.edition)}</h3><p class="standard-title">${h(r.title)}</p><div class="meta"><span class="badge ${r.status==='withdrawn'?'withdrawn':''}">${h(r.publisher_status)}</span>BSI record date: ${h(r.publisher_record_date||'Not established')} · checked ${h(r.source_checked)}<br>Amendment labels: ${h(r.amendments_in_designation.join(', ')||'None in designation')}</div><p class="standard-note">${h(r.change_summary||'Edition and status checked. A detailed revision summary is not available in this register; consult the publisher history and original text.')}</p>${standardDetails(r)}</div><div class="actions"><a class="primary" href="${h(r.source_url)}" target="_blank" rel="noopener noreferrer">Open official record ↗</a><span class="meta">Publisher access / licence</span></div></article>`).join(''):'<p class="empty">No matching references. Try a standard number or clear the filters.</p>';
}
for(const id of ['standards-search','standards-category','standards-update'])$(id).addEventListener(id==='standards-search'?'input':'change',()=>{standardsLimit=25;renderStandards();});
$('standards-clear').addEventListener('click',()=>{for(const id of ['standards-search','standards-category','standards-update'])$(id).value='';standardsLimit=25;renderStandards();});
$('standards-more').addEventListener('click',()=>{standardsLimit+=25;renderStandards();});
function showArchiveSection(){
  const standards=location.hash==='#standards';
  $('manual-panel').hidden=standards;$('standards-panel').hidden=!standards;
  $('nav-manuals').setAttribute('aria-current',standards?'false':'page');
  $('nav-standards').setAttribute('aria-current',standards?'page':'false');
}
window.addEventListener('hashchange',showArchiveSection);
renderStandards();showArchiveSection();
