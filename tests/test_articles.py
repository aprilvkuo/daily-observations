import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import subprocess
import unittest
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
import pipeline
try:
    import content
except ImportError:
    content=None

def article():
    return {'schema_version':1,'slug':'rsi-research-notes','category':'rsi','date':'2026-10-25','generated_at':'2026-10-25T10:00:00+08:00','title':'RSI研究笔记','summary':'用于本地测试','markdown':'# 研究笔记\n测试正文 <script>bad()</script>','source':{'producer':'author'}}

class ArticleTests(unittest.TestCase):
    def test_documented_cli_parses_source_on_installed_python(self):
        for script in ('pipeline.py','content.py'):
            result=subprocess.run([sys.executable,str(Path(__file__).parents[1]/'scripts'/script),'--help'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)

    def test_content_support_exists(self):
        self.assertIsNotNone(content,'Standalone article support missing')

    def test_article_archive_idempotency_explicit_revision_and_path_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);a=article()
            self.assertTrue(content.ingest_article(root,a))
            self.assertFalse(content.ingest_article(root,a))
            changed=dict(a,markdown='修订正文')
            with self.assertRaises(ValueError):content.ingest_article(root,changed)
            self.assertTrue(content.ingest_article(root,changed,replace=True))
            self.assertEqual((root/'articles/rsi-research-notes.md').read_text(),'修订正文')
            for key,value in [('slug','../escape'),('category','unknown'),('date','2026-02-30')]:
                with self.subTest(key=key),self.assertRaises(ValueError):content.ingest_article(root,dict(a,**{key:value}))

    def test_article_build_category_pages_full_feed_and_no_daily_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);a=article();content.ingest_article(root,a)
            pipeline.build(root,'https://example.org/site')
            out=root/'dist'
            self.assertIn('RSI研究笔记',(out/'research.html').read_text())
            self.assertIn('articles/rsi-research-notes.html',(out/'research.html').read_text())
            self.assertIn('专题笔记',(out/'notes.html').read_text())
            self.assertTrue((out/'daily.html').exists())
            page=(out/'articles/rsi-research-notes.html').read_text()
            self.assertIn('&lt;script&gt;',page)
            self.assertNotIn('<script>bad()',page)
            self.assertEqual((out/'articles/rsi-research-notes.md').read_text(),a['markdown'])
            items=ET.parse(out/'feed.xml').findall('./channel/item')
            self.assertEqual(len(items),1)
            self.assertEqual(items[0].findtext('link'),'https://example.org/site/articles/rsi-research-notes.html')
            self.assertIn('测试正文',items[0].findtext('description'))
            self.assertEqual(json.loads((out/'data/index.json').read_text())['reports'],[])

if __name__=='__main__':unittest.main()
