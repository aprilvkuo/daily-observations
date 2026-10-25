import html
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

SPEC = importlib.util.spec_from_file_location('pipeline', Path(__file__).parents[1] / 'scripts/pipeline.py')
pipeline = importlib.util.module_from_spec(SPEC) if SPEC else None
if SPEC and SPEC.loader and SPEC.origin and Path(SPEC.origin).exists():
    SPEC.loader.exec_module(pipeline)

def report(date='2026-10-25'):
    return {'schema_version':1,'date':date,'title':'三市场完整日报','report_type':'full_daily',
            'timezone':'Asia/Shanghai','generated_at':date+'T08:30:00+08:00',
            'markdown':'# 完整日报\n<script>alert(1)</script>\n正文 & 历史',
            'top10':[{'market':'US','symbol':'TEST','name':'测试标的','rank':1}],
            'source':{'producer':'fixture'}}

class PipelineTests(unittest.TestCase):
    def test_pipeline_exists(self):
        self.assertTrue(hasattr(pipeline, 'ingest'), 'report pipeline not implemented')

    def test_archive_is_idempotent_and_conflicts_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.assertTrue(pipeline.ingest(root, report()))
            self.assertFalse(pipeline.ingest(root, report()))
            revised=report(); revised['markdown']+=' changed'
            with self.assertRaises(ValueError): pipeline.ingest(root, revised)
            self.assertEqual((root/'reports/2026/10/2026-10-25.md').read_text(),report()['markdown'])

    def test_validation_rejects_partial_dates_duplicates(self):
        for key,value in [('date','../../escape'),('date','2026-02-30'),('report_type','summary'),('markdown',''),('timezone','UTC')]:
            bad=report();bad[key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):pipeline.validate(bad)
        bad=report();bad['top10']*=2
        with self.assertRaises(ValueError):pipeline.validate(bad)

    def test_build_full_rss_safe_report_and_comparison(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            prior=report('2026-10-24');prior['top10'][0]['rank']=3
            pipeline.ingest(root,prior);pipeline.ingest(root,report())
            pipeline.build(root,'https://example.org/investment-report')
            out=root/'dist'
            feed=ET.parse(out/'feed.xml')
            self.assertEqual(len(feed.findall('./channel/item')),2)
            self.assertIn(report()['markdown'],html.unescape(feed.findtext('./channel/item/description')))
            self.assertIn('https://example.org/investment-report/reports/2026-10-25.html',feed.findtext('./channel/item/link'))
            page=(out/'reports/2026-10-25.html').read_text()
            self.assertNotIn('<script>alert',page)
            self.assertIn('&lt;script&gt;',page)
            data=json.loads((out/'data/index.json').read_text())
            self.assertEqual(data['reports'][0]['top10'][0]['rank_change'],2)
            self.assertEqual(data['reports'][0]['previous_date'],'2026-10-24')
            self.assertTrue((out/'reports/2026/10/2026-10-25.json').exists())

    def test_missing_top10_does_not_imply_entries_or_exits(self):
        for old_missing,new_missing in [(False,True),(True,False),(True,True)]:
            with self.subTest(old_missing=old_missing,new_missing=new_missing),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);old=report('2026-10-24');new=report()
                if old_missing: old['top10']=[]
                if new_missing: new['top10']=[]
                pipeline.ingest(root,old);pipeline.ingest(root,new);pipeline.build(root,'https://example.org')
                row=json.loads((root/'dist/data/index.json').read_text())['reports'][0]
                self.assertFalse(row['comparison_available'])
                self.assertEqual(row['exited'],[])
                for entry in row['top10']: self.assertEqual(entry['status'],'no_baseline')

    def test_unified_sections_share_one_canonical_report_and_rss_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);r=report()
            r['markdown']='# 每日观察日报\n\n## 今日总览\n今日概述\n\n## 金融与市场\n金融正文\n\n## 科技与产业\n科技正文\n\n## AI与RSI\n研究正文\n\n## 风险与行动\n行动正文'
            pipeline.ingest(root,r);pipeline.build(root,'https://example.org')
            self.assertEqual((root/'reports/2026/10/2026-10-25.md').read_text(),r['markdown'])
            self.assertEqual(len(ET.parse(root/'dist/feed.xml').findall('./channel/item')),1)
            for slug,text in [('finance','金融正文'),('technology','科技正文'),('ai-rsi','研究正文')]:
                page=(root/'dist/topics'/f'{slug}.html').read_text()
                self.assertIn(text,page)
                self.assertIn(f'../reports/2026-10-25.html#{slug}',page)
            self.assertIn('每日观察',(root/'dist/index.html').read_text())
            data=json.loads((root/'dist/data/index.json').read_text())
            self.assertEqual(len(data['reports'][0]['sections']),5)

    def test_code_fences_do_not_create_false_topics(self):
        cases=[('~~~markdown','~~~'),('   ```python','   ```'),('````markdown','````')]
        for start,end in cases:
            with self.subTest(start=start):
                body='## 金融与市场\n金融\n'+start+'\n```\n## AI与RSI\n示例\n```\n'+end+'\n仍属金融\n## 科技与产业\n技术'
                parts=pipeline.sections(body)
                self.assertEqual([p['id'] for p in parts],['finance','technology'])
                self.assertIn('仍属金融',parts[0]['markdown'])

    def test_section_links_resolve_from_canonical_and_topic_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);r=report();r['markdown']='## 金融与市场\n[查看AI栏目](#ai-rsi)\n## AI与RSI\n研究'
            pipeline.ingest(root,r);pipeline.build(root,'https://example.org')
            self.assertIn('href="#ai-rsi"',(root/'dist/reports/2026-10-25.html').read_text())
            self.assertIn('href="../reports/2026-10-25.html#ai-rsi"',(root/'dist/topics/finance.html').read_text())
            self.assertNotIn('href="javascript:',pipeline.markdown('[危险](javascript:alert)'))

    def test_empty_site_has_no_fake_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);pipeline.build(root,'https://example.org')
            self.assertEqual(json.loads((root/'dist/data/index.json').read_text())['reports'],[])
            self.assertEqual(ET.parse(root/'dist/feed.xml').findall('./channel/item'),[])

if __name__=='__main__': unittest.main()
