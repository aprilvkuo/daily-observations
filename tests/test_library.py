import json
from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit

from test_pipeline import pipeline, report
from test_articles import article, content


def paper(**changes):
    a = dict(article(), slug='attention-notes', content_type='paper',
             tags=['Transformer', 'AI'], title='Attention 论文解读',
             markdown='## 核心思路\n正文 $x^2$\n\n## 核心思路\n\n```python\nprint(1)\n```\n\n```mermaid\ngraph LR\nA-->B\n```\n\n![示意图](https://example.org/image.png)\n\n$$\na^2+b^2=c^2\n$$\n\n<script>bad()</script>',
             paper={'arxiv_id':'1706.03762', 'title':'Attention Is All You Need',
                    'authors':['Ashish Vaswani', 'Noam Shazeer'], 'published':'2017-06-12',
                    'abstract':'A paper about attention.',
                    'code_url':'https://github.com/example/research'})
    return dict(a, **changes)


class LibraryTests(unittest.TestCase):
    def test_toc_reserves_shell_anchor_and_ignores_fenced_headings(self):
        from reading import render_reading,render_toc
        rendered,outline=render_reading('## main-content\n## main-content\n```text\n## fake\n```')
        anchors=[anchor for _,anchor,_ in outline]
        self.assertEqual(len(anchors),2)
        self.assertEqual(len(set(anchors)),2)
        self.assertNotIn('main-content',anchors)
        self.assertNotIn('fake',render_toc(outline))

    def test_generated_local_links_and_directory_anchors_resolve(self):
        class Links(HTMLParser):
            def __init__(self):
                super().__init__();self.links=[];self.ids=set()
            def handle_starttag(self,tag,attrs):
                attrs=dict(attrs)
                if 'id' in attrs: self.ids.add(attrs['id'])
                for name in ('href','src'):
                    if name in attrs: self.links.append(attrs[name])
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);content.ingest_article(root,paper());pipeline.ingest(root,report())
            pipeline.build(root,'https://example.org/site');out=root/'dist'
            for page in out.rglob('*.html'):
                parser=Links();parser.feed(page.read_text())
                for link in parser.links:
                    url=urlsplit(link)
                    if url.scheme or url.netloc: continue
                    target=(page.parent/unquote(url.path)).resolve() if url.path else page
                    self.assertTrue(target.exists(),f'{page.name}: {link}')
                    if target.suffix=='.html' and url.fragment:
                        dest=Links();dest.feed(target.read_text())
                        self.assertIn(unquote(url.fragment),dest.ids,f'{page.name}: {link}')

    def test_gpt_latex_delimiters_render_without_touching_code(self):
        from reading import render_reading
        rendered,_=render_reading(r'Inline \(x^2\)'+'\n\n'+r'\['+'\n'+r'\frac{a}{b}'+'\n'+r'\]'+'\n\n```text\n'+r'\(literal\)'+'\n```')
        self.assertIn('<span class="math inline">x^2</span>',rendered)
        self.assertIn('<div class="math block">',rendered)
        self.assertIn(r'\(literal\)',rendered)

    def test_optional_metadata_is_validated_and_old_article_remains_valid(self):
        self.assertEqual(content.validate_article(article()), article())
        self.assertEqual(content.validate_article(paper()), paper())
        for changes in [dict(content_type='oops'), dict(tags='AI'), dict(tags=[3]),
                        dict(paper={'arxiv_id':'../escape'}),
                        dict(paper={'authors':'unknown'}),
                        dict(paper={'published':'2026-02-30'}),
                        dict(paper={'code_url':'javascript:alert(1)'}),
                        dict(paper={'pdf_url':'//evil.example/file'}),
                        dict(paper={'abstract':[]})]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                content.validate_article(paper(**changes))

    def test_paper_detail_has_metadata_unique_toc_safe_rich_reading_and_raw_downloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);a=paper();content.ingest_article(root,a)
            pipeline.build(root,'https://example.org/site')
            out=root/'dist';page=(out/'articles/attention-notes.html').read_text()
            for text in ['1706.03762','Attention Is All You Need','Ashish Vaswani','2017-06-12',
                         'https://arxiv.org/abs/1706.03762','https://arxiv.org/pdf/1706.03762',
                         'https://github.com/example/research','文章目录',
                         'href="#核心思路"','href="#核心思路-2"','class="mermaid"',
                         'class="highlight"','class="math', '<img ', 'loading="lazy"']:
                self.assertIn(text,page)
            self.assertNotIn('<script>bad()',page)
            self.assertEqual((out/'articles/attention-notes.md').read_text(),a['markdown'])
            self.assertEqual(json.loads((out/'articles/attention-notes.json').read_text()),a)
            entries=ET.parse(out/'feed.xml').findall('./channel/item')
            self.assertEqual(len(entries),1)
            self.assertEqual(entries[0].findtext('guid'),'https://example.org/site/articles/attention-notes.html')

    def test_collections_are_separate_and_old_routes_and_feed_survive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);content.ingest_article(root,paper());content.ingest_article(root,article())
            pipeline.ingest(root,report());pipeline.build(root,'https://example.org/site')
            out=root/'dist'
            for route in ['daily.html','compare.html','research.html','notes.html',
                          *['topics/'+key+'.html' for key in pipeline.TOPICS]]:
                self.assertTrue((out/route).exists(),route)
            papers=(out/'papers.html').read_text();studies=(out/'studies.html').read_text()
            self.assertIn('Attention 论文解读',papers)
            self.assertNotIn('rsi-research-notes.html',papers)
            self.assertIn('rsi-research-notes.html',studies)
            self.assertNotIn('attention-notes.html',studies)
            for name in ['paper-search','paper-tag','paper-sort','paper-results','paper-status']:
                self.assertIn('id="'+name+'"',papers)
            self.assertEqual(len(ET.parse(out/'feed.xml').findall('./channel/item')),3)
            self.assertEqual(json.loads((out/'data/index.json').read_text())['reports'][0]['date'],report()['date'])

    def test_empty_collection_has_no_fabricated_papers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);pipeline.build(root,'https://example.org')
            page=(root/'dist/papers.html').read_text()
            self.assertIn('尚无论文解读',page)
            self.assertEqual(json.loads((root/'dist/data/articles.json').read_text()),[])

    def test_image_urls_cannot_execute_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            content.ingest_article(root,paper(markdown='![bad](javascript:alert)\n<img src=x onerror=alert(1)>'))
            pipeline.build(root,'https://example.org')
            page=(root/'dist/articles/attention-notes.html').read_text()
            self.assertNotIn('src="javascript:',page)
            self.assertNotIn('<img src=x',page)


if __name__=='__main__': unittest.main()
