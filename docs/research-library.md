# 研究知识库与论文发布

## 页面与兼容性

主导航为每日简报（`daily.html`）、论文解读（`papers.html`）、专题研究（`studies.html`）。首页展示真实档案计数与最新简报；没有论文或专题时保留空态，不自动发布示例。

旧 `research.html`、`notes.html`、`topics/*.html` 保留各自的日报栏目内容。`reports/日期.html`、`articles/slug.html`、Markdown/JSON 下载与 RSS guid 均保持原址。`compare.html` 和 `data/index.json` 继续服务原有 Top10。

## 可选文章字段

旧 `schema_version: 1` 文章继续有效，缺省归入专题研究。论文通过 `content_type: "paper"` 明确分类；`category` 仍为原来的 rsi/technology/finance/notes。分类用于主题，content_type 用于阅读类型，两者独立。

在原 `publish-article` 的 `client_payload.article` 对象中追加如下字段，即可使用现有 Make 8162821 发布。以下仅为格式示例，不代表本站已有解读：

```json
{
  "content_type": "paper",
  "tags": ["Transformer", "AI"],
  "paper": {
    "arxiv_id": "1706.03762",
    "title": "Attention Is All You Need",
    "published": "2017-06-12"
  }
}
```

其他可选字段：`paper.authors`（作者字符串数组）、`paper.abstract`（原文摘要字符串）、`paper.url`、`paper.pdf_url`、`paper.code_url`（完整 http(s) URL）。只有提供了 arxiv_id，才按 arXiv 官方地址格式补出原文与 PDF 链接；其他元数据不联网获取或猜补。未知字段无需造值。解读日期使用文章 date，论文发表日期单独展示；列表按解读日期排序。标签最多 20 个，每个 1–60 字符。

本地发布先把上述可选字段保存为仓库外的 metadata.json，然后运行：

```sh
git switch -c publish/your-paper-slug
python scripts/content.py --markdown /absolute/path/paper.md --title '真实解读标题' --slug your-paper-slug --category rsi --summary '真实摘要' --metadata-json /absolute/path/metadata.json
python -m unittest discover -s tests -v
python scripts/pipeline.py build
git add articles/
git commit -m 'Add reviewed paper reading'
git push -u origin HEAD
gh pr create
```

metadata.json 仅允许 content_type、tags、paper；不能覆盖 slug、日期或原文。现有 `--replace` 显式修订规则与不可变日报规则不变。Make 的直接发布仍是已有生产入口；网站开发分支使用 PR 审阅。

## 阅读格式

独立文章支持 Markdown 标题、列表、引用、表格、链接、图片及围栏代码。目录取自标题，重复标题获得唯一锚点；代码块里的标题不会进入目录。代码由 Pygments 在构建时高亮，不依赖浏览器 CDN。

数学支持 `$...$`、`$$...$$`、`\(...\)`、`\[...\]`，其中后者的块公式可跨行。围栏语言 `mermaid` 生成图表。图片可使用完整 http(s) URL，或把资源置于 `web/` 后引用 `../assets/文件名`（相对于 articles 详情页）；web 顶层文件随构建复制。远程图片可用性取决于原站。

原始 HTML 作为文本显示。公式/图表渲染器固定为 KaTeX 0.19.1 和 Mermaid 11.17.2，按需从 jsDelivr 加载；安全选项禁止可信 HTML 执行。CDN 加载失败保留 TeX/Mermaid 原文并显示提示。长代码、公式、表格在内容区域内横向滚动；图片自适应宽度。手机版目录可折叠。原始 Markdown/JSON 与完整 RSS 正文不经富文本转换。

## 自动化与审阅

生产 `publish.yml` 保留 main push、publish-report / publish-article dispatch、手动触发及串行队列，只增加依赖安装和论文列表测试。08:00 上游任务和 Make 场景未改动。Make 在本次检查中为按需发布转发器，不是定时器。

`preview.yml` 仅由 PR 触发，以只读仓库权限运行 Python、Node 测试和站点构建。产物 `research-library-preview` 可从该 PR 的 Actions 运行下载，保留 14 天；解压后运行 `python3 -m http.server 8080` 预览。此工作流没有归档写入、Pages 部署或 Make 调用。

开发完成后审阅 PR，再合并至 main；本次开发不会自行合并或部署。

渲染实现参照 [Markdown-it 安全说明](https://markdown-it-py.readthedocs.io/en/latest/security.html)、[KaTeX API](https://katex.org/docs/api.html)、[Mermaid API](https://mermaid.js.org/config/usage.html)。
