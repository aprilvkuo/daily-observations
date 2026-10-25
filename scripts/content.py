"""Standalone author notes, independent of daily report production."""
import argparse
from datetime import date, datetime
import html
import json
from pathlib import Path
import re
import shutil
from zoneinfo import ZoneInfo

CATEGORIES={'rsi':'RSI研究','technology':'科技与AI','finance':'金融与投资','notes':'专题笔记'}

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
        body=f'<main class="article"><a class="eyebrow" href="../index.html">← 每日观察 / {category}</a><h1>{html.escape(a["title"])}</h1><div class="meta">{a["date"]} · {category} · 独立文章</div><div class="downloads"><a href="{slug}.md">Markdown ↓</a><a href="{slug}.json">JSON ↓</a></div><article>{markdown(a["markdown"])}</article></main>'
        (out/'articles'/(slug+'.html')).write_text(shell(a['title'],body,base,'../'))
        for ext in ('md','json'):shutil.copy(root/'articles'/(slug+'.'+ext),out/'articles'/(slug+'.'+ext))
    for category,path in [('rsi','research.html'),('notes','notes.html')]:
        title=CATEGORIES[category];cards=article_cards([a for a in articles if a['category']==category])
        extra='<p class="muted"><a href="topics/ai-rsi.html">查看每日日报中的 AI／RSI 动态 ↗</a></p>' if category=='rsi' else ''
        body=f'<main><section class="hero compact"><span class="eyebrow">RESEARCH / NOTES</span><h1>{title}</h1><p>独立于每日简报，积累值得持续回看的问题、证据与思考。</p>{extra}</section><section>{cards or "<div class=empty>尚无独立文章，发布后自动归档。</div>"}</section></main>'
        (out/path).write_text(shell(title,body,base))
    (out/'data/articles.json').write_text(json.dumps([{k:v for k,v in a.items() if k!='markdown'} for a in articles],ensure_ascii=False,indent=2)+'\n')
    return articles

def main():
    parser=argparse.ArgumentParser(description='Add a standalone article from a Markdown file')
    parser.add_argument('--markdown',required=True,type=Path);parser.add_argument('--title',required=True);parser.add_argument('--slug',required=True);parser.add_argument('--category',required=True,choices=CATEGORIES);parser.add_argument('--summary',default='');parser.add_argument('--date');parser.add_argument('--replace',action='store_true');args=parser.parse_args()
    now=datetime.now(ZoneInfo('Asia/Shanghai'));day=args.date or now.date().isoformat()
    a={'schema_version':1,'slug':args.slug,'category':args.category,'date':day,'generated_at':day+'T'+now.strftime('%H:%M:%S')+'+08:00','title':args.title,'summary':args.summary,'markdown':args.markdown.read_text(),'source':{'producer':'author'}}
    print('Article changed:',ingest_article(Path(__file__).resolve().parents[1],a,replace=args.replace))

if __name__=='__main__':main()
