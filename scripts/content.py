"""Standalone author notes, independent of daily report production."""
import argparse
from datetime import date, datetime
import html
import json
from pathlib import Path
import re
import shutil
from zoneinfo import ZoneInfo
from urllib.parse import urlparse

try:
    from scripts.reading import render_reading, render_toc
except ModuleNotFoundError:
    from reading import render_reading, render_toc

CATEGORIES={'rsi':'RSI研究','technology':'科技与AI','finance':'金融与投资','notes':'专题笔记'}

def is_paper(a):
    return a.get('content_type', 'research') == 'paper'

def validate_metadata(a):
    if a.get('content_type','research') not in ('paper','research'): raise ValueError('Unknown content_type')
    tags=a.get('tags',[])
    if not isinstance(tags,list) or len(tags)>20 or any(not isinstance(t,str) or not t.strip() or len(t)>60 for t in tags): raise ValueError('Invalid tags')
    paper=a.get('paper',{})
    if not isinstance(paper,dict): raise ValueError('paper must be an object')
    for key in ('arxiv_id','title','abstract','published','url','pdf_url','code_url'):
        if key in paper and not isinstance(paper[key],str): raise ValueError('Invalid paper.'+key)
    if 'arxiv_id' in paper and not re.fullmatch(r'(?:\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Z]{2})?/\d{7})(?:v[1-9]\d*)?',paper['arxiv_id']): raise ValueError('Invalid arXiv ID')
    if 'published' in paper: date.fromisoformat(paper['published'])
    if 'authors' in paper and (not isinstance(paper['authors'],list) or any(not isinstance(s,str) or not s.strip() for s in paper['authors'])): raise ValueError('Invalid paper authors')
    for key in ('url','pdf_url','code_url'):
        if key in paper:
            url=urlparse(paper[key])
            if url.scheme not in ('http','https') or not url.netloc or any(c.isspace() for c in paper[key]): raise ValueError('Invalid paper URL')

def paper_metadata(a):
    if not is_paper(a): return ''
    p=a.get('paper',{});escape=html.escape;arxiv=p.get('arxiv_id')
    links=[('原文 ↗',p.get('url') or (f'https://arxiv.org/abs/{arxiv}' if arxiv else None)),
           ('PDF ↗',p.get('pdf_url') or (f'https://arxiv.org/pdf/{arxiv}' if arxiv else None)),
           ('代码 ↗',p.get('code_url'))]
    fields=''
    for label,value in [('论文',p.get('title')),('作者',' · '.join(p.get('authors',[]))),('发表日期',p.get('published')),('arXiv',arxiv)]:
        if value: fields+=f'<div><dt>{label}</dt><dd>{escape(value)}</dd></div>'
    abstract=f'<details><summary>原文摘要</summary><p>{escape(p["abstract"])}</p></details>' if p.get('abstract') else ''
    resources=''.join(f'<a href="{escape(url,quote=True)}" rel="noreferrer">{label}</a>' for label,url in links if url)
    missing='<p class="muted">原论文元数据尚未提供。</p>' if not fields else ''
    return '<section class="paper-metadata" aria-label="原论文信息"><span class="eyebrow">SOURCE PAPER</span><dl>'+fields+'</dl>'+missing+abstract+'<div class="resource-links">'+resources+'</div></section>'

def validate_article(a):
    if not isinstance(a,dict) or a.get('schema_version')!=1:raise ValueError('Invalid article schema')
    if not isinstance(a.get('slug'),str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',a['slug']) or len(a['slug'])>100:raise ValueError('Use a lowercase slug with hyphens')
    if a.get('category') not in CATEGORIES:raise ValueError('Unknown article category')
    if not isinstance(a.get('date'),str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',a['date']):raise ValueError('Invalid article date')
    date.fromisoformat(a['date'])
    try:stamp=datetime.fromisoformat(a['generated_at'])
    except (KeyError,ValueError,TypeError) as exc:raise ValueError('Missing generated_at') from exc
    if stamp.utcoffset() is None or stamp.utcoffset().total_seconds()!=28800 or stamp.date().isoformat()!=a['date']:raise ValueError('generated_at must match date at +08:00')
    for field in ('title','markdown'):
        if not isinstance(a.get(field),str) or not a[field].strip():raise ValueError('Missing '+field)
    if not isinstance(a.get('summary',''),str):raise ValueError('summary must be text')
    if len(a['markdown'].encode())>750_000:raise ValueError('Article too large')
    if not isinstance(a.get('source'),dict) or not a['source'].get('producer'):raise ValueError('Missing source.producer')
    validate_metadata(a)
    return a

def ingest_article(root,a,replace=False):
    validate_article(a);folder=root/'articles';path=folder/(a['slug']+'.json')
    if path.exists():
        if json.loads(path.read_text())==a:return False
        if not replace:raise ValueError('Article exists: use explicit --replace for a reviewed revision')
    folder.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n');path.with_suffix('.md').write_text(a['markdown'])
    return True

def load_articles(root):
    result=[]
    for path in (root/'articles').glob('*.json'):
        a=validate_article(json.loads(path.read_text()))
        if path.stem!=a['slug']:raise ValueError('Article filename must match slug')
        if not path.with_suffix('.md').exists() or path.with_suffix('.md').read_text()!=a['markdown']:raise ValueError('Article Markdown and JSON differ; use the content helper')
        result.append(a)
    return sorted(result,key=lambda a:(a['generated_at'],a['slug']),reverse=True)

def article_cards(articles,relative=''):
    return ''.join(f'<a class="report-card" href="{relative}articles/{a["slug"]}.html"><span class="date">{a["date"]}</span><span><strong>{html.escape(a["title"])}</strong><small>{CATEGORIES[a["category"]]} · {html.escape(a.get("summary",""))}</small></span><span class="arrow">↗</span></a>' for a in articles)

def build_articles(root,out,base,shell,markdown):
    articles=load_articles(root);(out/'articles').mkdir(exist_ok=True)
    for a in articles:
        slug=a['slug'];category=CATEGORIES[a['category']]
        rendered,outline=render_reading(a['markdown'])
        kind='论文解读' if is_paper(a) else '专题研究';collection='papers' if is_paper(a) else 'studies'
        date_label='解读日期' if is_paper(a) else '发布于'
        tags=''.join('<span class="tag">'+html.escape(t)+'</span>' for t in a.get('tags',[]))
        summary='<p class="article-summary">'+html.escape(a['summary'])+'</p>' if a.get('summary') else ''
        body=f'<main class="article reading"><a class="eyebrow" href="../{collection}.html">← {kind}</a><h1>{html.escape(a["title"])}</h1><div class="meta">{date_label} {a["date"]} · {category} · {kind}</div>{summary}<div class="tags">{tags}</div>{paper_metadata(a)}<div class="downloads"><a href="{slug}.md">Markdown ↓</a><a href="{slug}.json">JSON ↓</a></div><div class="reading-layout">{render_toc(outline)}<article>{rendered}</article></div><a class="back-top" href="#main-content">返回顶部 ↑</a></main><script src="../assets/reading.js" defer></script>'
        (out/'articles'/(slug+'.html')).write_text(shell(a['title'],body,base,'../'))
        for ext in ('md','json'):shutil.copy(root/'articles'/(slug+'.'+ext),out/'articles'/(slug+'.'+ext))
    (out/'data/articles.json').write_text(json.dumps([{k:v for k,v in a.items() if k!='markdown'} for a in articles],ensure_ascii=False,indent=2)+'\n')
    return articles

def main():
    parser=argparse.ArgumentParser(description='Add a standalone article from a Markdown file')
    parser.add_argument('--markdown',required=True,type=Path);parser.add_argument('--title',required=True);parser.add_argument('--slug',required=True);parser.add_argument('--category',required=True,choices=CATEGORIES);parser.add_argument('--summary',default='');parser.add_argument('--date');parser.add_argument('--replace',action='store_true');parser.add_argument('--metadata-json',type=Path,help='JSON with optional content_type, tags, paper');args=parser.parse_args()
    now=datetime.now(ZoneInfo('Asia/Shanghai'));day=args.date or now.date().isoformat()
    a={'schema_version':1,'slug':args.slug,'category':args.category,'date':day,'generated_at':day+'T'+now.strftime('%H:%M:%S')+'+08:00','title':args.title,'summary':args.summary,'markdown':args.markdown.read_text(),'source':{'producer':'author'}}
    if args.metadata_json:
        metadata=json.loads(args.metadata_json.read_text())
        if not isinstance(metadata,dict) or set(metadata)-{'content_type','tags','paper'}: raise ValueError('metadata-json accepts only content_type, tags, paper')
        a.update(metadata)
    print('Article changed:',ingest_article(Path(__file__).resolve().parents[1],a,replace=args.replace))

if __name__=='__main__':main()
