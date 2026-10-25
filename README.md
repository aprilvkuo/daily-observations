# 三市场长期价值监控

每日08:00（Asia/Shanghai）启动的既有分析任务是唯一内容生产者。这里负责发布，不运行任何模型、不新增分析定时器，也不发送飞书/邮件消息。分析完成后，完整日报进入 Make → GitHub → GitHub Pages → RSS。

- 临时地址：https://aprilvkuo.github.io/investment-report/
- 目标域名：https://invest.egguo.com/ （DNS/HTTPS 验证通过后启用）
- 完整订阅：站点下 `feed.xml`
- 历史：`reports/YYYY/MM/YYYY-MM-DD.{md,json}`，同时生成网页版
- Top10：两期任意比较，按 market + symbol 匹配；未知数据不填充、不推测

## 发布输入

Make on-demand 场景接收 `report_json`（完整 JSON 文本，不加代码围栏）。以下为结构说明，勿把示例当真实报告发布：

```json
{
  "schema_version": 1,
  "date": "2026-10-25",
  "timezone": "Asia/Shanghai",
  "generated_at": "2026-10-25T08:30:00+08:00",
  "report_type": "full_daily",
  "title": "三市场长期价值监控｜2026-10-25",
  "markdown": "完整原始报告正文，不能是摘要、链接或截断片段",
  "top10": [],
  "source": {"producer": "existing-chatgpt-0800-monitor"}
}
```

`top10` 单条：`{"market":"US","symbol":"EXAMPLE","name":"公司名","rank":1}`。market 仅 CN/HK/US，rank 1–10 且唯一。仅提取原日报明确给出的总Top10；若原报告没有结构化榜单，传空数组，不另作分析。可以保留额外估值、货币、数据截至时间等原始字段。`full_daily` 是发送者对完整性的声明；脚本无法判断观点是否充分或数据是否真实。

GitHub 接收 `POST /repos/aprilvkuo/investment-report/dispatches`：

```json
{"event_type":"publish-report","client_payload":{"report":{ "完整报告对象": "按上述结构" }}}
```

验证链路时设置 `client_payload.validation_only=true`，仍验证 report 结构，但不写入历史、不生成伪日报。HTTP 204 仅表示收到触发请求，必须检查 Actions 的归档和部署结果。

## 数据保全与重复处理

同日相同 JSON 重发不会重复写入或增加 RSS 条目；同日不同 JSON 拒绝，需人工审查更正，通过 Git 保留修订记录。RSS guid 按日期固定。所有输入文本转义，JS 使用 textContent；网页不执行正文 HTML。Markdown 原样保存，网页支持标题、表格、加粗和 http(s) 链接。报告中的 Markdown 图片保留为原始文本/链接，不自动加载远程图片。

报告按日期倒序。缺失日期不补造。排名变化使用实际上一归档日期，非假设昨日。RSS 包含完整转义正文；没有报告时 feed 为空且网页明确显示等待状态。

## 本地验证

```sh
python3 -m unittest discover -s tests -v
python3 scripts/pipeline.py build
python3 -m http.server 8080 --directory dist
```

## Pages 与域名

仓库 Settings → Pages 设置 GitHub Actions。部署工作流没有 schedule；push、手动触发或发布 dispatch 才运行。设置仓库变量 `SITE_URL=https://invest.egguo.com` 并在 Pages 配置自定义域名后，RSS 将使用自定义域名链接。

DNS 提供商 Cloudflare：为 `invest` 添加 CNAME → `aprilvkuo.github.io`，初次签发证书建议 DNS only。只改 invest 记录，不改根域名和其他子域。必须核验 DNS 与 GitHub HTTPS 证书后才宣称域名已上线。

## 接入现有 ChatGPT 08:00 任务

先确认正确任务的名称、时区、内容及最近输出。保留既有分析主体、08:00 时刻和运行环境。仅在报告完成后追加：把相同完整正文与原报告Top10包装为上述 JSON，调用 Make 发布场景一次。不要调用飞书发送场景，不要新建分析任务，不要重复发送摘要。上游若没有 Make 插件执行能力，应明确记录未接通，不能仅靠写入提示词声称完成。
