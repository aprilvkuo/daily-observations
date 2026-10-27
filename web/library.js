/* Progressive enhancement: every card is already present in the static HTML. */
(() => {
  function filterPapers(papers, query, tag, order) {
    const terms=query.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    return papers.filter(p=>terms.every(t=>p.search.includes(t)) && (!tag || p.tags.includes(tag)))
      .sort((a,b)=>(order==='asc'?1:-1)*(a.date.localeCompare(b.date)||a.slug.localeCompare(b.slug)));
  }
  if(typeof module!=='undefined') module.exports={filterPapers};
  if(typeof document==='undefined') return;
  const search=document.querySelector('#paper-search'),tag=document.querySelector('#paper-tag'),sort=document.querySelector('#paper-sort');
  const list=document.querySelector('#paper-results'),status=document.querySelector('#paper-status'),empty=document.querySelector('#paper-no-results');
  if(!search || !list) return;
  search.closest('form').addEventListener('submit',event=>event.preventDefault());
  const papers=Array.from(list.children).map(el=>({el,search:el.dataset.search,tags:JSON.parse(el.dataset.tags),date:el.dataset.date,slug:el.querySelector('a').getAttribute('href')}));
  const params=new URLSearchParams(location.search);
  search.value=params.get('q')||'';
  if(Array.from(tag.options).some(o=>o.value===params.get('tag'))) tag.value=params.get('tag');
  if(params.get('sort')==='asc') sort.value='asc';
  function render() {
    const visible=filterPapers(papers,search.value,tag.value,sort.value),selected=new Set(visible);
    for(const p of papers) p.el.hidden=!selected.has(p);
    for(const p of visible) list.append(p.el);
    status.textContent=`${visible.length} / ${papers.length} 篇论文解读`;
    empty.hidden=visible.length>0 || papers.length===0;
    const next=new URLSearchParams();
    if(search.value.trim()) next.set('q',search.value.trim());
    if(tag.value) next.set('tag',tag.value);
    if(sort.value==='asc') next.set('sort','asc');
    try { history.replaceState(null,'',location.pathname+(next.size?'?'+next.toString():'')); } catch (_) { /* file previews stay usable */ }
  }
  search.addEventListener('input',render);tag.addEventListener('change',render);sort.addEventListener('change',render);
  document.querySelector('#paper-reset').addEventListener('click',()=>{search.value='';tag.value='';sort.value='desc';render();search.focus();});
  render();
})();
