import tempfile
import unittest
from pathlib import Path
from test_pipeline import pipeline, report

class AdaptationTests(unittest.TestCase):
    def test_daily_content_reaches_every_public_dimension(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);r=report()
            r['markdown']='# 日报\n'+ '\n'.join('## '+title+'\n'+slug+'实际正文' for slug,title in pipeline.TOPICS.items())
            pipeline.ingest(root,r);pipeline.build(root,'https://example.org')
            out=root/'dist'
            for page,slug in [('research.html','ai-rsi'),('notes.html','actions'),('topics/overview.html','overview')]:
                self.assertIn(slug+'实际正文',(out/page).read_text())
            home=(out/'index.html').read_text()
            for slug in pipeline.TOPICS:
                self.assertIn('topics/'+slug+'.html',home)
            self.assertNotIn('等待首篇独立文章',home)
            self.assertNotIn('尚无独立文章',(out/'research.html').read_text())

    def test_common_chat_heading_variations_keep_topics_separate(self):
        body='## 一、今日总览\n总览正文\n## **金融与市场**\n金融正文\n## 科技与AI\n科技正文\n## AI 与 RSI\n研究正文\n## 风险与行动\n行动正文\n## 附录\n不属于行动'
        parts=pipeline.sections(body)
        self.assertEqual([p['id'] for p in parts],list(pipeline.TOPICS))
        self.assertNotIn('不属于行动',parts[-1]['markdown'])
        self.assertIn('id="ai-rsi"',pipeline.markdown(body))

if __name__=='__main__':unittest.main()
