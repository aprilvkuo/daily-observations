(async () => {
  const current=document.querySelector('#current'),previous=document.querySelector('#previous'),market=document.querySelector('#market'),status=document.querySelector('#status'),container=document.querySelector('#comparison');
  const add=(tag,text,parent)=>{const el=document.createElement(tag);el.textContent=text;parent.append(el);return el;};
  try {
    const response=await fetch('data/index.json');if(!response.ok)throw Error('HTTP '+response.status);
    const {reports}=await response.json();
    if(!reports.length){status.textContent='尚无完整日报，收到真实报告后显示比较。';return;}
    for(const r of reports){for(const select of [current,previous]){const option=add('option',r.date,select);option.value=r.date;}}
    previous.value=reports[1]?.date||reports[0].date;
    const render=()=>{
      const a=reports.find(r=>r.date===current.value),b=reports.find(r=>r.date===previous.value),old=new Map(b.top10.map(x=>[x.market+':'+x.symbol.toUpperCase(),x]));
      container.replaceChildren();
      const rows=a.top10.filter(x=>market.value==='all'||x.market===market.value);
      const table=add('table','',container),head=add('tr','',add('thead','',table));
      ['市场 / 代码','公司','当前排名','比较排名','变化'].forEach(t=>add('th',t,head));
      const tbody=add('tbody','',table);
      for(const item of rows){const before=old.get(item.market+':'+item.symbol.toUpperCase()),delta=before?before.rank-item.rank:null,row=add('tr','',tbody);[item.market+' / '+item.symbol,item.name,item.rank,before?.rank??'—',delta===null?(b.top10.length?'新进':'无基准'):delta>0?'↑ '+delta:delta<0?'↓ '+(-delta):'持平'].forEach(t=>add('td',String(t),row));}
      const keys=new Set(a.top10.map(x=>x.market+':'+x.symbol.toUpperCase()));
      const exited=b.top10.filter(x=>!keys.has(x.market+':'+x.symbol.toUpperCase())&&(market.value==='all'||market.value===x.market));
      for(const x of exited){const row=add('tr','',tbody);[x.market+' / '+x.symbol,x.name,'—',x.rank,'退出'].forEach(t=>add('td',String(t),row));}
      status.textContent=`${a.date} 对比 ${b.date} · ${rows.length} 个当前标的 · ${exited.length} 个退出${!a.top10.length?' · 本期未提供结构化Top10':''}${!b.top10.length?' · 比较期未提供结构化Top10':''}`;
    };
    [current,previous,market].forEach(el=>el.addEventListener('change',render));render();
  }catch(error){status.textContent='历史档案暂时无法读取，请稍后刷新。';}
})();
