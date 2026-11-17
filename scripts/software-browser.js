const softwareData=JSON.parse($('software-data').textContent);
const softwareAccess={public:'Public download page','account-required':'Account required','installer-account':'Installer access required','registration-required':'Registration required','not-verified':'Download access not verified'};
const softwareTypes={software:'Software',driver:'Driver','firmware-portal':'Firmware portal'};
let softwareLimit=30;
for(const [id,key,label] of [['software-brand','brand','All brands'],['software-category','category','All systems']]){
  $(id).innerHTML=`<option value="">${label}</option>`+[...new Set(softwareData.records.map(r=>r[key]))].sort().map(v=>`<option value="${h(v)}">${h(key==='category'?(labels[v]||v):v)}</option>`).join('');
}
$('software-checked').textContent=`Official links checked ${softwareData.checked_on}. Package contents and installation have not been tested.`;
$('software-gaps').innerHTML=(softwareData.gaps||[]).map(g=>`<li>${h(g)}</li>`).join('');
const softwareIndex=softwareData.records.map(record=>({record,search:normal([record.name,record.brand,...record.products,record.description,...record.platforms].join(' '))}));
function renderSoftware(){
  const terms=$('software-search').value.trim().split(/\s+/).map(normal).filter(Boolean);
  const list=softwareIndex.filter(({record:r,search})=>terms.every(t=>search.includes(t))&&
    (!$('software-brand').value||r.brand===$('software-brand').value)&&
    (!$('software-category').value||r.category===$('software-category').value)&&
    (!$('software-type').value||r.resource_type===$('software-type').value)&&
    (!$('software-access').value||r.access===$('software-access').value)).map(x=>x.record);
  $('software-count').textContent=`${list.length} resources · showing ${Math.min(softwareLimit,list.length)}`;
  $('software-more').hidden=list.length<=softwareLimit;
  $('software-results').innerHTML=list.length?list.slice(0,softwareLimit).map(r=>`<article><div><div class="eyebrow">${h(labels[r.category]||r.category)} / ${h(r.brand)}</div><h2>${h(r.name)}</h2><div class="models">${h(r.products.join(' · '))}</div><p class="resource-scope">${h(r.description)}</p><div class="meta"><span class="badge">${h(softwareTypes[r.resource_type])}</span><span class="badge">${h(softwareAccess[r.access])}</span><br>Platform: ${h(r.platforms.join(' · ')||'Not verified')} · Version: ${h(r.version||'Check official source')}<br>Source checked ${h(r.checked_on)}</div><details><summary>Source check and limitations</summary><p class="resource-scope">${h(r.verification.note)}</p><p class="meta">${h(r.verification.method)} · ${h(r.verification.status)}. Installer contents, signatures and equipment compatibility have not been tested.</p></details></div><div class="actions"><a class="primary" href="${h(r.source_url)}" target="_blank" rel="noopener noreferrer">${r.access==='public'?'Open official download page':r.access==='not-verified'?'Open official source':'Open vendor access page'} ↗</a>${r.download_url&&r.access==='public'?`<a href="${h(r.download_url)}" target="_blank" rel="noopener noreferrer">Publisher-listed package ↗</a>`:''}</div></article>`).join(''):'<p class="empty">No matching resources. Try another model, brand or access filter.</p>';
}
for(const id of ['software-search','software-brand','software-category','software-type','software-access'])$(id).addEventListener(id==='software-search'?'input':'change',()=>{softwareLimit=30;renderSoftware();});
$('software-clear').addEventListener('click',()=>{for(const id of ['software-search','software-brand','software-category','software-type','software-access'])$(id).value='';softwareLimit=30;renderSoftware();});
$('software-more').addEventListener('click',()=>{softwareLimit+=30;renderSoftware();});
renderSoftware();
