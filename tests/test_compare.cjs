const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
function element(){return {children:[],value:'',textContent:'',append(x){this.children.push(x);if(!this.value&&x.value)this.value=x.value;},replaceChildren(){this.children=[];},addEventListener(){}};}
(async()=>{
 const nodes=Object.fromEntries(['current','previous','market','status','comparison'].map(k=>['#'+k,element()]));
 nodes['#current'].value='2026-10-25';nodes['#market'].value='all';
 const context={document:{querySelector:k=>nodes[k],createElement:element},fetch:async()=>({ok:true,json:async()=>({reports:[{date:'2026-10-25',top10:[{market:'US',symbol:'TEST',name:'Example',rank:1}]}]})})};
 await vm.runInNewContext(fs.readFileSync('web/compare.js','utf8'),context);
 assert.match(nodes['#status'].textContent,/仅有一期/);
 assert.ok(nodes['#comparison'].children.length);
 assert.doesNotMatch(JSON.stringify(nodes['#comparison']),/持平|新进/);
 console.log('Single-report snapshot verified');
})();
