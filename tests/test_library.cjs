const assert=require('node:assert/strict');
const {filterPapers}=require('../web/library.js');
const papers=[
  {slug:'older',date:'2026-10-25',search:'attention vaswani transformer 1706.03762',tags:['AI','Transformer']},
  {slug:'newer',date:'2026-10-27',search:'agent memory 论文',tags:['Agent']},
  {slug:'other',date:'2026-10-26',search:'attention test',tags:['AI']}
];
assert.deepEqual(filterPapers(papers,'','','desc').map(p=>p.slug),['newer','other','older']);
assert.deepEqual(filterPapers(papers,'','','asc').map(p=>p.slug),['older','other','newer']);
assert.deepEqual(filterPapers(papers,' ATTENTION  vaswani ','AI','desc').map(p=>p.slug),['older']);
assert.equal(filterPapers(papers,'1706.03762','','desc').length,1);
assert.equal(filterPapers(papers,'论文','Agent','desc').length,1);
assert.equal(filterPapers(papers,'missing','','desc').length,0);
assert.equal(filterPapers(papers,'attention','Agent','desc').length,0);
assert.equal(papers[0].slug,'older','Filtering must not mutate input order');
console.log('Paper search, tags, date ordering, empty results and input stability verified');
