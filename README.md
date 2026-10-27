# 每日观察：金融 / 科技 / AI

目标是将两个既有08:00任务合并为一个“每日观察日报”（任务合并尚未执行）。这里负责发布，不运行任何模型、不新增分析定时器，也不发送飞书/邮件消息。分析完成后，完整日报进入 Make → GitHub → GitHub Pages → RSS。

- 临时地址：https://aprilvkuo.github.io/daily-observations/
- 目标域名：https://invest.egguo.com/ （DNS/HTTPS 验证通过后启用）
- 统一完整订阅：站点下 `feed.xml`，每期只有一个条目，含所有栏目
- 历史：`reports/YYYY/MM/YYYY-MM-DD.{md,json}`，同时生成网页版
- Top10：两期任意比较，按 market + symbol 匹配；未知数据不填充、不推测

## 发布输入

Make on-demand 场景接收 `dispatch_json`（完整 GitHub dispatch JSON 文本，不加代码围栏）；其中 client_payload.report 的结构如下。以下为结构说明，勿把示例当真实报告发布：

```json
{
  "schema_version": 1,
  "date": "2026-10-25",
  "timezone": "Asia/Shanghai",
  "generated_at": "2026-10-25T08:30:00+08:00",
  "report_type": "full_daily",
  "title": "每日观察日报｜2026-10-25",
  "markdown": "完整原始报告正文，不能是摘要、链接或截断片段",
  "top10": [],
  "source": {"producer": "existing-chatgpt-0800-monitor"}
}
```

`top10` 单条：`{"market":"US","symbol":"EXAMPLE","name":"公司名","rank":1}`。market 仅 CN/HK/US，rank 1–10 且唯一。仅提取原日报明确给出的总Top10；若原报告没有结构化榜单，传空数组，不另作分析。可以保留额外估值、货币、数据截至时间等原始字段。`full_daily` 是发送者对完整性的声明；脚本无法判断观点是否充分或数据是否真实。

GitHub 接收 `POST /repos/aprilvkuo/daily-observations/dispatches`：

```json
{"event_type":"publish-report","client_payload":{"report":{ "完整报告对象": "按上述结构" }}}
```

验证链路时设置 `client_payload.validation_only=true`，仍验证 report 结构，但不写入历史、不生成伪日报。HTTP 204 仅表示收到触发请求，必须检查 Actions 的归档和部署结果。

## 数据保全与重复处理

同日相同 JSON 重发不会重复写入或增加 RSS 条目；同日不同 JSON 拒绝，需人工审查更正，通过 Git 保留修订记录。RSS guid 按日期固定。所有输入文本转义，JS 使用 textContent；网页不执行正文 HTML。Markdown 原样保存，网页支持标题、表格、加粗和 http(s) 链接。报告中的 Markdown 图片保留为原始文本/链接，不自动加载远程图片。

报告按日期倒序。缺失日期不补造。排名变化使用实际上一归档日期，非假设昨日。RSS 包含完整转义正文；没有报告时 feed 为空且网页明确显示等待状态。

## 本地验证

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python3 -m unittest discover -s tests -v
node tests/test_compare.cjs
node tests/test_library.cjs
python3 scripts/pipeline.py build
python3 -m http.server 8080 --directory dist
```

## Pages 与域名

仓库 Settings → Pages 设置 GitHub Actions。部署工作流没有 schedule；push、手动触发或发布 dispatch 才运行。设置仓库变量 `SITE_URL=https://invest.egguo.com` 并在 Pages 配置自定义域名后，RSS 将使用自定义域名链接。

DNS 提供商 Cloudflare：为 `invest` 添加 CNAME → `aprilvkuo.github.io`，初次签发证书建议 DNS only。只改 invest 记录，不改根域名和其他子域。必须核验 DNS 与 GitHub HTTPS 证书后才宣称域名已上线。

## 接入现有 ChatGPT 08:00 任务

先确认正确任务的名称、时区、内容及最近输出。保留既有分析主体、08:00 时刻和运行环境。仅在报告完成后追加：把相同完整正文与原报告Top10包装为上述 JSON，调用 Make 场景 8162821「Publish Three-Market Daily Report to GitHub Pages」一次，输入 dispatch_json 为包含 event_type 与 client_payload.report 的完整JSON文本。不要调用飞书发送场景，不要新建分析任务，不要重复发送摘要。上游若没有 Make 插件执行能力，应明确记录未接通，不能仅靠写入提示词声称完成。


## 统一栏目约定

一份完整Markdown为唯一原文。请使用下面五个精确的二级标题，站点将直接抽取其原文段落建立栏目视图，不再次分析或改写：

```markdown
# 每日观察日报｜YYYY-MM-DD
## 今日总览
## 金融与市场
## 科技与产业
## AI与RSI
## 风险与行动
```

- 今日总览：当天最重要的3–5项变化和跨领域影响；关联正文以链接指向，不重复叙述整条新闻。
- 金融与市场：保留原三市场监控深度，A/H/美股长期价值、正常化盈利、估值、安全边际、Top10及变动；休市注明数据交易日。
- 科技与产业：保留重点简报中的关键新闻、进展、商业化意义和原始来源。
- AI与RSI：模型、Agent、自进化论文与实验启发，明确作者报告与独立验证边界。
- 风险与行动：跨栏目风险与待验证事项；无重要变化时明确说明，不填充虚构内容。

同一事件只在主要栏目完整说明，其他栏目引用其锚点。金融Top10仍存顶层top10数组，按market+symbol做历史比较；没有榜单则留空。不把栏目拆成独立日报或多个RSS条目。旧版无栏目标题的完整日报仍保留原文和订阅，栏目页不臆测归类。

栏目网址：`topics/finance.html`、`topics/technology.html`、`topics/ai-rsi.html`。完整报告内也有栏目导航。仓库、域名与发布场景复用，不新建站点或分析任务。

## 发布独立文章

RSI研究、科技与AI、金融与投资、专题笔记可以随时单独发布，不必包含金融Top10，也不依赖当天日报。

先在仓库之外准备完整Markdown正文，然后运行（替换成真实文件、标题和slug）：

```sh
python3 scripts/content.py --markdown /absolute/path/research.md --title '你的研究标题' --slug your-research-title --category rsi --summary '一句话介绍'
python3 -m unittest discover -s tests -v
python3 scripts/pipeline.py build
git add articles/
git commit -m 'Publish research note'
git push
```

分类可选 `rsi`、`technology`、`finance`、`notes`。工具自动生成 `articles/slug.md` 和 `articles/slug.json`，避免手工维护两份正文。修改已有文章需显式添加 `--replace`，审阅差异后提交，Git保留历史。原稿无日期时使用当前北京时间，也可指定 `--date YYYY-MM-DD`。

文章更新沿用同一RSS guid；是否提示修订取决于订阅器。网站更新由合并到 main 后的 push 自动触发，不需要手动上传生成的HTML。统一feed.xml同时包含日报和独立文章。日常开发请创建分支并提交 PR，检查工作流只构建预览，不部署。

也支持通过现有Make发布入口发送：

```json
{"event_type":"publish-article","client_payload":{"article":{"schema_version":1,"slug":"your-research-title","category":"rsi","date":"2026-10-25","generated_at":"2026-10-25T12:00:00+08:00","title":"你的研究标题","summary":"一句话介绍","markdown":"完整文章正文","source":{"producer":"author"}}}}
```

Make场景8162821接收上述完整JSON文本作为dispatch_json。仅验证时设置client_payload.validation_only=true，不写入公开档案。按需文章发布不创建任何定时分析任务。

## 站点结构与域名

- 每日简报：`daily.html`
- RSI研究：`research.html`，并链接日报中的AI/RSI动态
- 科技与AI：`topics/technology.html`
- 金融与投资：`topics/finance.html`，保留Top10历史入口
- 专题笔记：`notes.html`
- 独立文章：`articles/slug.html`

站名“每日观察”覆盖多种主题。新目标域名为 `brief.egguo.com`，取代尚未配置的invest.egguo.com；以实际DNS、Pages域名配置与HTTPS核验结果为准。仓库仍复用daily-observations，不会影响已有blog或stock_agent。

## 研究知识库改版

论文列表、可选 arXiv 元数据、Markdown 阅读格式与 PR 预览流程见 [研究知识库发布说明](docs/research-library.md)。旧文章默认归入专题研究；论文继续使用 articles/slug.html 原址。
