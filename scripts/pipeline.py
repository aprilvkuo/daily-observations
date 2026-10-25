"""Deterministic archive, comparison and RSS builder. Never performs analysis."""
import argparse
from datetime import date, datetime, timezone
from email.utils import format_datetime
import html
import json
import os
from pathlib import Path
import re
import shutil
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
TOPICS = {'overview':'今日总览','finance':'金融与市场','technology':'科技与产业','ai-rsi':'AI与RSI','actions':'风险与行动'}

def markdown_lines(body):
    fence=None
    for line in body.splitlines(keepends=True):
        if fence:
            closing=re.fullmatch(r' {0,3}'+re.escape(fence[0])+'{'+str(len(fence))+r',}[ \t]*\r?\n?',line)
            if closing:
                fence=None;yield line,True,'close'
            else: yield line,True,None
        else:
            opening=re.match(r'^ {0,3}(`{3,}|~{3,})([^\r\n]*)',line)
            if opening:
                fence=opening[1];yield line,True,'open'
            else: yield line,False,None

def sections(body):
    """Extract exact canonical sections; do not classify or rewrite prose."""
    found=[]; current=None; lines=[]
    for line,fenced,marker in markdown_lines(body):
        match=None if fenced else re.fullmatch(r'## ([^\r\n]+)\r?\n?',line)
        slug=next((key for key,title in TOPICS.items() if match and match[1]==title),None)
        if slug:
            if current: found.append({'id':current,'title':TOPICS[current],'markdown':''.join(lines)})
            current=slug;lines=[]
        elif current: lines.append(line)
    if current: found.append({'id':current,'title':TOPICS[current],'markdown':''.join(lines)})
    return found

def validate(r):
    if not isinstance(r, dict): raise ValueError('Report must be an object')
    if r.get('schema_version') != 1: raise ValueError('schema_version must be 1')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(r.get('date',''))): raise ValueError('Invalid report date')
    date.fromisoformat(r['date'])
    if r.get('report_type') != 'full_daily': raise ValueError('Only full_daily reports are accepted')
    if r.get('timezone') != 'Asia/Shanghai': raise ValueError('timezone must be Asia/Shanghai')
    try: stamp = datetime.fromisoformat(r['generated_at'])
    except (KeyError, TypeError, ValueError) as exc: raise ValueError('Invalid generated_at') from exc
    if stamp.utcoffset() is None or stamp.utcoffset().total_seconds()!=28800 or stamp.date().isoformat()!=r['date']:
        raise ValueError('generated_at must match the report date at +08:00')
    for field in ('title','markdown'):
        if not isinstance(r.get(field),str) or not r[field].strip(): raise ValueError(f'Missing {field}')
    if len(r['markdown'].encode()) > 750_000: raise ValueError('Report too large')
    if not isinstance(r.get('source'),dict) or not r['source'].get('producer'): raise ValueError('Missing source.producer')
    if not isinstance(r.get('top10'),list) or len(r['top10'])>10: raise ValueError('top10 must contain at most 10 entries')
    seen=set(); ranks=set()
    for item in r['top10']:
        if not isinstance(item,dict): raise ValueError('Invalid Top10 entry')
        if item.get('market') not in ('CN','HK','US'): raise ValueError('market must be CN/HK/US')
        if not isinstance(item.get('symbol'),str) or not re.fullmatch(r'[A-Za-z0-9.^-]{1,24}',item['symbol']): raise ValueError('Invalid symbol')
        if not isinstance(item.get('name'),str) or not item['name'].strip(): raise ValueError('Missing stock name')
        rank=item.get('rank')
        if type(rank) is not int or not 1<=rank<=10 or rank in ranks: raise ValueError('Invalid or duplicate rank')
        key=(item['market'],item['symbol'].upper())
        if key in seen: raise ValueError('Duplicate market and symbol')
        ranks.add(rank);seen.add(key)
    return r

def ingest(root, report):
    validate(report)
    folder=root/'reports'/report['date'][:4]/report['date'][5:7]
    path=folder/(report['date']+'.json')
    if path.exists():
        if json.loads(path.read_text())==report: return False
        raise ValueError('Conflicting same-date report: archive is immutable; review correction in Git')
    folder.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    path.with_suffix('.md').write_text(report['markdown'])
    return True

def inline(text,fragment_base=''):
    escaped=html.escape(text)
    def link(m):
        url=html.unescape(m[2])
        if re.fullmatch(r'#[A-Za-z0-9_-]+',url): url=fragment_base+url
        elif urlparse(url).scheme not in ('https','http'): return m[1]
        return '<a href="'+html.escape(url,quote=True)+'" rel="noreferrer">'+m[1]+'</a>'
    escaped=re.sub(r'\[([^\]]+)\]\(([^\s)]+)\)',link,escaped)
    return re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',escaped)

def markdown(body,fragment_base=''):
    result=[];table=False;code=False
    for raw,in_code,marker in markdown_lines(body):
        line=raw.rstrip('\r\n')
        if marker:
            if table: result.append('</tbody></table></div>');table=False
            result.append('</code></pre>' if marker=='close' else '<pre><code>');code=marker=='open';continue
        if in_code: result.append(html.escape(line)+'\n');continue
        if line.strip().startswith('|') and line.strip().endswith('|'):
            cells=line.strip().strip('|').split('|')
            if all(re.fullmatch(r'\s*:?-+:?\s*',c) for c in cells): continue
            if not table: result.append('<div class="table-scroll"><table><tbody>');table=True
            result.append('<tr>'+''.join('<td>'+inline(c.strip(),fragment_base)+'</td>' for c in cells)+'</tr>');continue
        if table: result.append('</tbody></table></div>');table=False
        heading=re.match(r'^(#{1,6})\s+(.+)$',line)
        if heading:
            anchor=next((key for key,title in TOPICS.items() if len(heading[1])==2 and heading[2]==title),None)
            attr=f' id="{anchor}"' if anchor else ''
            n=min(len(heading[1])+1,6);result.append(f'<h{n}{attr}>{inline(heading[2],fragment_base)}</h{n}>')
        elif line.strip(): result.append('<p>'+inline(line,fragment_base)+'</p>')
    if code: result.append('</code></pre>')
    if table: result.append('</tbody></table></div>')
    return '\n'.join(result)

def shell(title,body,base,relative=''):
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(title)} · 每日观察</title><link rel="stylesheet" href="{relative}assets/style.css"><link rel="alternate" type="application/rss+xml" title="每日观察完整日报" href="{base}/feed.xml"></head><body><header><a class="brand" href="{relative}index.html">◈ 每日观察 <small>DAILY / PERSPECTIVES</small></a><nav><a href="{relative}index.html">完整日报</a><a href="{relative}topics/finance.html">金融</a><a href="{relative}topics/technology.html">科技</a><a href="{relative}topics/ai-rsi.html">AI / RSI</a><a href="{relative}compare.html">Top10</a><a href="{relative}feed.xml">RSS ↗</a></nav></header>{body}<footer>金融 · 科技 · AI与研究 · 保留每一次判断<br>同一份完整日报，多个阅读维度。观点与数据以各期标注为准，研究记录仅供参考。</footer></body></html>'''

def build(root, base):
    base=base.rstrip('/')
    if urlparse(base).scheme not in ('http','https'): raise ValueError('Invalid base URL')
    out=root/'dist'
    if out.exists(): shutil.rmtree(out)
    (out/'data').mkdir(parents=True);(out/'reports').mkdir()
    web=root/'web'
    if not web.exists(): web=ROOT/'web'
    (out/'assets').mkdir()
    for asset in web.glob('*'):
        if asset.is_file(): shutil.copy(asset,out/'assets'/asset.name)
    reports=[]
    for path in sorted((root/'reports').glob('*/*/*.json'),reverse=True): reports.append(validate(json.loads(path.read_text())))
    index=[]
    for i,r in enumerate(reports):
        prior=reports[i+1] if i+1<len(reports) else None
        comparable=bool(prior and prior['top10'] and r['top10'])
        old={(x['market'],x['symbol'].upper()):x for x in prior['top10']} if comparable else {}
        ranked=[]
        for item in sorted(r['top10'],key=lambda x:x['rank']):
            prev=old.get((item['market'],item['symbol'].upper()))
            ranked.append(dict(item,previous_rank=prev['rank'] if prev else None,rank_change=prev['rank']-item['rank'] if prev else None,status='continued' if prev else ('new' if comparable else 'no_baseline')))
        exited=[x for k,x in old.items() if k not in {(y['market'],y['symbol'].upper()) for y in r['top10']}]
        parts=sections(r['markdown'])
        index.append(dict(sections=[{'id':p['id'],'title':p['title']} for p in parts],comparison_available=comparable,date=r['date'],title=r['title'],generated_at=r['generated_at'],top10=ranked,exited=exited,previous_date=prior['date'] if prior else None))
        dest=out/'reports'/r['date'][:4]/r['date'][5:7];dest.mkdir(parents=True,exist_ok=True)
        raw=root/'reports'/r['date'][:4]/r['date'][5:7]/(r['date']+'.json')
        shutil.copy(raw,dest/raw.name);shutil.copy(raw.with_suffix('.md'),dest/raw.with_suffix('.md').name)
        prefix=f"{r['date'][:4]}/{r['date'][5:7]}/{r['date']}"
        toc='<div class="topic-links">'+''.join(f'<a href="#{p["id"]}">{p["title"]}</a>' for p in parts)+'</div>' if parts else ''
        body=f'''<main class="article"><a class="eyebrow" href="../index.html">← 全部日报</a><h1>{html.escape(r['title'])}</h1><div class="meta">{r['date']} · 北京时间 {html.escape(r['generated_at'][11:16])} · 完整日报</div><div class="downloads"><a href="{prefix}.md">Markdown ↓</a><a href="{prefix}.json">JSON ↓</a></div>{toc}<article>{markdown(r['markdown'])}</article></main>'''
        (out/'reports'/(r['date']+'.html')).write_text(shell(r['title'],body,base,'../'))
    (out/'data/index.json').write_text(json.dumps({'timezone':'Asia/Shanghai','reports':index},ensure_ascii=False,indent=2)+'\n')
    cards=''.join(f'<a class="report-card" href="reports/{r["date"]}.html"><span class="date">{r["date"]}</span><span><strong>{html.escape(r["title"])}</strong><small>完整正文 · Markdown / JSON</small></span><span class="arrow">↗</span></a>' for r in reports)
    empty='<div class="empty"><h2>等待首份完整日报</h2><p>发布基础设施已准备。收到真实报告后，这里会显示完整正文、历史归档与排名变化。</p></div>'
    topic_cards=''.join(f'<a class="topic-card" href="topics/{key}.html"><span class="eyebrow">{key.upper()}</span><h2>{title}</h2><p>{desc}</p><span>进入栏目 ↗</span></a>' for key,title,desc in [('finance','金融与市场','A股、港股、美股 · 长期价值 · Top10变动'),('technology','科技与产业','关键技术、产业进展与商业化影响'),('ai-rsi','AI与RSI','模型与Agent · 自进化研究 · 实验启发')])
    body=f'''<main><section class="hero"><span class="eyebrow">FINANCE / TECHNOLOGY / AI</span><h1>看见变化，形成判断。</h1><p>把金融、科技与AI研究放在同一张图景中。每天一份完整日报，先读总览，再按关注的维度深入。</p><a class="button" href="feed.xml">订阅统一日报 RSS ↗</a></section><div class="stats"><div><strong>{len(reports):03}</strong><span>已归档完整日报</span></div><div><strong>08:00</strong><span>北京时间 · 分析启动时间</span></div><div><strong>1</strong><span>统一日报 / 统一订阅</span></div></div><section class="topic-grid">{topic_cards}</section><section><div class="section-head"><h2>完整日报档案</h2><span>多个维度 / 一份原文</span></div><p class="muted">{'最新报告：'+reports[0]['date'] if reports else '尚无报告；统一任务与发布接入待核验。'} · 完成分析后发布，缺失日期不补造。</p>{cards or empty}</section></main>'''
    (out/'index.html').write_text(shell('日报档案',body,base))
    compare='''<main><section class="hero compact"><span class="eyebrow">RANKING / HISTORY</span><h1>变化，比名次更重要。</h1><p>选择任意两期，比较同一市场与代码的排名。新进、退出与名次移动单独记录。</p></section><section><div class="controls"><label>当前日期<select id="current"></select></label><label>比较日期<select id="previous"></select></label><label>市场<select id="market"><option value="all">全部市场</option><option value="CN">A股</option><option value="HK">港股</option><option value="US">美股</option></select></label></div><p id="status" class="muted" aria-live="polite">正在读取档案…</p><div id="comparison" class="table-scroll"></div></section></main><script src="assets/compare.js" defer></script>'''
    (out/'compare.html').write_text(shell('Top10 历史比较',compare,base))
    (out/'topics').mkdir()
    for slug,title in TOPICS.items():
        entries=[]
        for r in reports:
            part=next((p for p in sections(r['markdown']) if p['id']==slug),None)
            if part:
                canonical=f'../reports/{r["date"]}.html'
                entries.append(f'<section><div class="section-head"><h2>{r["date"]}</h2><a href="{canonical}#{slug}">阅读本期完整日报 ↗</a></div><article>{markdown(part["markdown"],canonical)}</article></section>')
        content=''.join(entries) or '<div class="empty"><h2>等待本栏目内容</h2><p>这里展示统一日报中的原文栏目，不单独生成第二份报告。</p></div>'
        body=f'<main><section class="hero compact"><span class="eyebrow">DAILY / {slug.upper()}</span><h1>{title}</h1><p>从同一份完整日报进入这个维度，保留当时的事实、判断与来源。</p></section>{content}</main>'
        (out/'topics'/(slug+'.html')).write_text(shell(title,body,base,'../'))
    rss=ET.Element('rss',version='2.0');channel=ET.SubElement(rss,'channel')
    for tag,value in [('title','每日观察 · 金融 / 科技 / AI'),('link',base+'/'),('description','每天08:00启动统一日报，包含今日总览、金融与市场、科技与产业、AI与RSI、风险与行动。'),('language','zh-CN')]: ET.SubElement(channel,tag).text=value
    for r in reports:
        item=ET.SubElement(channel,'item');url=f"{base}/reports/{r['date']}.html"
        for tag,value in [('title',r['title']),('link',url),('guid',url),('pubDate',format_datetime(datetime.fromisoformat(r['generated_at']))),('description','<pre style="white-space:pre-wrap">'+html.escape(r['markdown'])+'</pre>')]: ET.SubElement(item,tag).text=value
    ET.indent(rss);ET.ElementTree(rss).write(out/'feed.xml',encoding='utf-8',xml_declaration=True)
    (out/'.nojekyll').touch()
    (out/'robots.txt').write_text('User-agent: *\nAllow: /\n')
    return len(reports)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['build','ingest-event']);parser.add_argument('--base-url',default=os.environ.get('SITE_URL','https://aprilvkuo.github.io/investment-report'));args=parser.parse_args()
    if args.action=='ingest-event':
        event=json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
        if event.get('client_payload',{}).get('validation_only') is True:
            validate(event['client_payload']['report']);print('Validation only; no archive written');return
        print('Archive changed:',ingest(ROOT,event.get('client_payload',{}).get('report')))
    else: print('Reports built:',build(ROOT,args.base_url))

if __name__=='__main__': main()
