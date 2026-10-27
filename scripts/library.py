"""Editorial home and independent paper/research collections."""
import html
import json

try:
    from scripts.content import CATEGORIES, article_cards, is_paper
except ModuleNotFoundError:
    from content import CATEGORIES, article_cards, is_paper


def paper_cards(articles):
    cards=[]
    for a in articles:
        p=a.get('paper',{});tags=a.get('tags',[])
        search=' '.join([a['title'],a.get('summary',''),CATEGORIES[a['category']],
                         p.get('title',''),p.get('arxiv_id',''),*p.get('authors',[]),*tags])
        badges=''.join('<span class="tag">'+html.escape(t)+'</span>' for t in tags)
        source=('arXiv:'+p['arxiv_id']) if p.get('arxiv_id') else '论文解读'
        cards.append(f'<li class="paper-card" data-search="{html.escape(search.casefold(),quote=True)}" data-tags="{html.escape(json.dumps(tags,ensure_ascii=False),quote=True)}" data-date="{a["date"]}"><div class="paper-card-meta"><time datetime="{a["date"]}">{a["date"]}</time><span>{html.escape(source)}</span></div><h2><a href="articles/{a["slug"]}.html">{html.escape(a["title"])}</a></h2><p>{html.escape(a.get("summary", ""))}</p><div class="tags">{badges}</div><a class="text-link" href="articles/{a["slug"]}.html">阅读全文 <span aria-hidden="true">↗</span></a></li>')
    return ''.join(cards)


def build_library(out, base, reports, articles, shell, topics):
    papers=[a for a in articles if is_paper(a)]
    studies=[a for a in articles if not is_paper(a)]
    # Both initial HTML and JS sort by the visible reading date, with slug as tie break.
    papers.sort(key=lambda a:(a['date'],a['slug']), reverse=True)
    tags=sorted({t for a in papers for t in a.get('tags',[])})
    options=''.join(f'<option value="{html.escape(t,quote=True)}">{html.escape(t)}</option>' for t in tags)
    controls=f'<form class="library-controls" role="search"><label class="search-field" for="paper-search">搜索论文<input id="paper-search" type="search" placeholder="标题、作者、arXiv ID 或关键词" autocomplete="off"></label><label for="paper-tag">标签<select id="paper-tag"><option value="">全部标签</option>{options}</select></label><label for="paper-sort">解读日期<select id="paper-sort"><option value="desc">最新在前</option><option value="asc">最早在前</option></select></label></form>'
    empty='<div class="empty"><span class="eyebrow">A SPACE FOR IDEAS</span><h2>尚无论文解读</h2><p>论文解读发布后，将在这里按日期归档。先从每日简报中的 AI 与 RSI 动态读起。</p><a class="text-link" href="topics/ai-rsi.html">阅读研究动态 ↗</a></div>'
    results='<p id="paper-status" class="muted" role="status" aria-live="polite">'+str(len(papers))+' 篇论文解读</p><ul id="paper-results" class="paper-grid">'+paper_cards(papers)+'</ul><div id="paper-no-results" class="empty" hidden><h2>没有找到匹配的论文</h2><p>试试其他关键词，或重置筛选条件。</p><button id="paper-reset" type="button">重置筛选</button></div>'
    body='<main><section class="hero compact collection-hero"><span class="eyebrow">PAPERS / IDEAS INTO UNDERSTANDING</span><h1>论文解读</h1><p>读懂一个方法的来处、证据与边界。把论文里的想法，放回实际问题中。</p></section>'+controls+results+(empty if not papers else '')+'<noscript><p class="muted">当前显示全部论文，按最新解读日期排序；启用 JavaScript 后可搜索和筛选。</p></noscript></main><script src="assets/library.js" defer></script>'
    (out/'papers.html').write_text(shell('论文解读',body,base))
    empty_studies='<div class="empty"><h2>专题研究正在积累</h2><p>长期问题，需要持续观察。独立文章发布后，会在这里归档。</p><a class="text-link" href="daily.html">先读每日简报 ↗</a></div>'
    body='<main><section class="hero compact"><span class="eyebrow">RESEARCH / THE LONG VIEW</span><h1>专题研究</h1><p>围绕金融、科技与 AI 展开持续思考，留下推理过程，也留下待验证的问题。</p></section><section>'+ (article_cards(studies) or empty_studies)+'</section></main>'
    (out/'studies.html').write_text(shell('专题研究',body,base))
    topic_links=''.join(f'<a href="topics/{slug}.html">{title} ↗</a>' for slug,title in topics.items())
    if reports:
        r=reports[0]
        latest=f'<a class="latest-report" href="reports/{r["date"]}.html"><div class="paper-card-meta"><span>最新一期</span><time datetime="{r["date"]}">{r["date"]}</time></div><h2>{html.escape(r["title"])}</h2><p>今日总览 · 金融与市场 · 科技与产业 · AI与RSI · 风险与行动</p><span class="text-link">阅读完整简报 ↗</span></a>'
    else:
        latest='<div class="latest-report"><span class="eyebrow">DAILY BRIEF</span><h2>等待首份完整日报</h2><p>收到真实报告后，这里会显示最新一期。</p></div>'
    collections=''.join(f'<a class="collection-link" href="{url}"><span class="eyebrow">{eyebrow}</span><h2>{title}<span aria-hidden="true">↗</span></h2><p>{desc}</p><small>{count} {unit}</small></a>' for url,eyebrow,title,desc,count,unit in [
        ('daily.html','01 / DAILY BRIEF','每日简报','捕捉金融、科技与 AI 的每日变化。',len(reports),'期完整简报'),
        ('papers.html','02 / PAPER NOTES','论文解读','拆解方法、实验与可以复用的启发。',len(papers),'篇论文解读'),
        ('studies.html','03 / RESEARCH','专题研究','围绕长期问题，积累独立判断。',len(studies),'篇专题研究')])
    recent=''.join(f'<a class="archive-date" href="reports/{r["date"]}.html">{r["date"]} <span>↗</span></a>' for r in reports[1:5])
    paper_preview=paper_cards(papers[:2])
    preview_empty='<div class="quiet-empty"><span class="empty-mark" aria-hidden="true">◇</span><h3>为值得深读的论文留一页</h3><p>论文解读发布后，这里会展示最新内容。</p><a class="text-link" href="papers.html">进入论文库 ↗</a></div>'
    studies_preview=article_cards(studies[:3]) or '<div class="quiet-empty"><h3>把观察，积累成研究</h3><p>专题文章将独立于每日简报归档。</p></div>'
    body=f'''<main id="home">
<section class="home-intro"><div><span class="eyebrow">DAILY OBSERVATIONS, LASTING IDEAS</span><h1>看见变化，<br>积累判断。</h1><p>用简报捕捉当下，用论文理解方法，<br class="desktop-break">用研究连接更长的时间。</p><div class="intro-actions"><a class="button" href="daily.html">阅读每日简报 <span aria-hidden="true">↗</span></a><a class="text-link" href="papers.html">探索论文库 →</a></div></div><aside class="editorial-note"><span class="eyebrow">FIELD NOTES / 每日观察</span><div class="orbit" aria-hidden="true"><i></i><b>观</b></div><p>金融 · 科技 · AI</p><small>记录事实，理解方法，保留判断。</small></aside></section>
<section class="collection-grid" aria-label="内容分类">{collections}</section>
<section><div class="section-head"><div><span class="eyebrow">THE DAILY EDITION</span><h2>从今天开始阅读</h2></div><a class="text-link" href="daily.html">全部简报 →</a></div>{latest}<div class="recent-dates">{recent}</div><div class="topic-links" aria-label="日报栏目">{topic_links}</div></section>
<section><div class="section-head"><div><span class="eyebrow">READ THE ORIGINAL. THINK FURTHER.</span><h2>最近的论文解读</h2></div><a class="text-link" href="papers.html">全部论文 →</a></div>{'<ul class="paper-grid">'+paper_preview+'</ul>' if papers else preview_empty}</section>
<section><div class="section-head"><div><span class="eyebrow">QUESTIONS WORTH KEEPING</span><h2>持续关注的议题</h2></div><a class="text-link" href="studies.html">全部研究 →</a></div>{studies_preview}</section>
<section class="subscribe-strip"><div><span class="eyebrow">KEEP IN PERSPECTIVE</span><h2>让阅读有迹可循。</h2><p>北京时间 08:00 启动日报分析，完成后归档。订阅包含完整简报与独立文章。</p></div><a class="button" href="feed.xml">订阅 RSS ↗</a></section></main>'''
    (out/'index.html').write_text(shell('首页',body,base))
