# 每日观察文章契约

以当前仓库 `scripts/content.py` 的 `validate_article` 为准。发布一篇论文需要 `articles/<slug>.json` 和同名 `.md`；JSON 的 `markdown` 是完整正文字符串，必须与 `.md` 逐字一致（包括末尾换行）。这是已有 schema_version 1 格式，不能改成作者/链接都在顶层的通用博客 JSON。

## 外层字段

| 字段 | 值或约束 |
| --- | --- |
| schema_version | 数字 `1` |
| slug | 小写英文和数字，以单个连字符分隔，最长100字符，文件名相同 |
| category | `rsi` / `technology` / `finance` / `notes`，按内容选 |
| date | `YYYY-MM-DD`，新文章为 Asia/Shanghai 的解读日期 |
| generated_at | ISO 8601，时区 `+08:00`，其日期必须与 date 相同 |
| title | 非空中文解读标题 |
| summary | 简短纯文本摘要，字符串 |
| markdown | 完整非空正文，UTF-8不超过750000字节 |
| source | 对象，必须含非空 `producer`；可用 `paper-to-site` |
| content_type | `paper` |
| tags | 字符串数组，最多20项，每项非空且最多60字符 |
| paper | 下表中的已核验论文元数据 |

`authors`、`arxiv_id`、`pdf_url` 等在 `paper` 内，不在外层。JSON使用标准序列化器，不能手工拼接正文转义。

## paper 字段（均可省略，不能用 null 假装已知）

| 字段 | 格式 |
| --- | --- |
| arxiv_id | 如 `1706.03762v7`，旧式 `cs/9901001` 也支持；只填实际读过的版本 |
| title | 原论文标题 |
| authors | 作者名称字符串数组 |
| published | `YYYY-MM-DD`，论文首次发表日；版本修订日写在正文 |
| abstract | 原文摘要字符串，可省略 |
| url | 官方原文完整HTTP(S)链接，锁定版本时与ID一致 |
| pdf_url | 官方PDF完整HTTP(S)链接 |
| code_url | 核验过的官方代码完整HTTP(S)链接，无则省略 |

只有 arxiv_id 时，站点会推导 arXiv原文/PDF链接，不会联网补作者/日期。没有 arXiv编号的论文使用已核验的 url/pdf_url/title 等。

## 新文与修订

创建前检索 `articles/*.json` 的 paper.arxiv_id（去除尾部v数字比较）、URL和标题。已存在同一论文时沿用 slug，并读取原 JSON/Markdown。

修订默认保留原 `date` 和 `generated_at`；更新 paper.arxiv_id、版本URL和正文，在正文注明实际修订日期及变化。不要保留旧date同时把generated_at改成今天，这会被验证器拒绝。需要按今天重新进入解读列表时，先按用户明确意图同步更新date和generated_at，并在发布结果或审阅PR中说明排序/RSS日期会变化。

用完整文章 JSON 提交时先调用仓库验证器；用 `scripts/content.py --metadata-json` 时，该元数据文件只包含 `content_type`、`tags`、`paper`，不包含整篇文章外层字段。
