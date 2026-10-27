/* Pinned optional renderers. Original text remains readable if a CDN fails. */
(() => {
  const loadScript=(src)=>new Promise((resolve,reject)=>{const script=document.createElement('script');script.src=src;script.onload=resolve;script.onerror=reject;document.head.append(script);});
  const note=(el,text)=>{const p=document.createElement('p');p.className='render-note';p.textContent=text;el.after(p);};
  const math=Array.from(document.querySelectorAll('.math'));
  if(math.length) {
    const css=document.createElement('link');css.rel='stylesheet';css.href='https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/katex.min.css';document.head.append(css);
    loadScript('https://cdn.jsdelivr.net/npm/katex@0.19.1/dist/katex.min.js').then(()=>{
      for(const el of math) window.katex.render(el.textContent,el,{displayMode:el.classList.contains('block'),throwOnError:false,trust:false,strict:'warn',maxExpand:1000});
    }).catch(()=>note(math[0],'公式显示组件暂时无法加载，已保留 TeX 原文。'));
  }
  const charts=Array.from(document.querySelectorAll('pre.mermaid'));
  if(charts.length) import('https://cdn.jsdelivr.net/npm/mermaid@11.17.2/dist/mermaid.esm.min.mjs').then(async ({default:mermaid})=>{
    mermaid.initialize({startOnLoad:false,securityLevel:'strict',theme:'base',themeVariables:{primaryColor:'#edf1eb',primaryTextColor:'#223c35',lineColor:'#a57137',fontFamily:'system-ui'},flowchart:{htmlLabels:false},suppressErrorRendering:true,maxTextSize:50000});
    for(const [i,el] of charts.entries()) {
      const original=el.textContent;
      try {
        const {svg}=await mermaid.render('reading-diagram-'+i,original);
        const wrapper=document.createElement('div');wrapper.className='mermaid-rendered';wrapper.innerHTML=svg;
        el.replaceWith(wrapper);
        const source=document.createElement('details');source.className='diagram-source';
        const title=document.createElement('summary');title.textContent='查看图表源码';source.append(title,el);wrapper.after(source);
      } catch (_) { el.textContent=original;note(el,'图表暂时无法渲染，已保留 Mermaid 源码。'); }
    }
  }).catch(()=>note(charts[0],'图表显示组件暂时无法加载，已保留 Mermaid 源码。'));
})();
