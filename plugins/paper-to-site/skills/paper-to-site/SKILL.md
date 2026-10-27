---
name: paper-to-site
description: Use when the user wants a Chinese paper reading from an arXiv link or PDF, wants to turn an existing paper discussion into an article, or wants that reading submitted to 每日观察 / aprilvkuo/daily-observations. General paper questions without an article goal do not need this skill.
---

# 论文解读与发布

将论文或当前讨论整理成有来源、可阅读、可审阅的每日观察文章。仓库 `aprilvkuo/daily-observations`，网站 `https://brief.egguo.com`。默认交付 PR；合并后的 Actions 才发布。

## 先判断用户要什么

- “解读”且未要求入站：完成有来源的解读草稿，不创建 PR。
- “整理刚才讨论”：保留用户的问题、判断与关注点，核验讨论中引用的证据，不把他人或模型的观点归给用户。
- “提交审阅 / 发布到每日观察”：准备文章并创建 PR，不再重复询问是否创建 PR。
- “直接发布 / 跳过 PR”：只有用户明确选择直接上线，才走 Make 入口。已有授权继续有效。

按当前聊天实际能力执行。Chat 不保证有本地终端；已安装此技能也不代表已有 GitHub/Make 授权。先检查可用工具。默认 PR 路径只需可写 GitHub 连接，Make 仅用于直接上线；缺少工具时保留能完成的稿件和发布文件，准确指出待完成的步骤。

## 阅读与写作

读 [writing.md](references/writing.md)。核对论文版本、原文、实验与局限；没有读到全文就说明范围，不生成伪装成全文解读的完成稿。元数据、代码和结论均需可追溯，未核验字段省略。

用中文写清问题、方法、实验与判断，按用户关注点取舍。公式、代码、Mermaid、图片服务于解释。网页里的证据引用使用可点击的普通 Markdown 来源链接与章节/图表编号；不要把聊天专有引用标记当成网页来源。

## 组织文章并提交

读 [article-schema.md](references/article-schema.md) 和 [publishing.md](references/publishing.md)。JSON 的 `markdown` 与同名 `.md` 必须完全一致；用 JSON 序列化工具保存换行和反斜杠。论文类型为 `content_type: paper`，arXiv 元数据放在 `paper` 对象内。

先读取当前仓库的 validator 和已有文章，按不含版本号的 arXiv ID、原文 URL 与标题查重。修订保留已有 slug、date 和 generated_at；正文注明修订日和版本变化，显式调整解读日期时同步调整时间戳。不得凭空发明一个与 date 不同日的 generated_at。

有终端时复用仓库验证器、测试和构建；无终端时通过 GitHub 工具创建匹配的文章文件并依赖 PR CI，明确本地构建未运行。验证结果阻止发布时，修复稿件或交付待修订稿。

仅修改本次文章和需要的图片资源；保持日报、08:00 任务、Make 配置、Top10、RSS 生成逻辑和生产工作流不变。

## 返回可核对的结果

简述文章主题、阅读来源及版本，提供稿件/文件或 PR 链接，并报告检查的实际状态。区分“草稿已准备”“PR 已提交”“CI 已通过”“已上线”；缺少任何一步的证据就保持该步待完成。直接发布返回 Actions 运行结果，成功后再检查文章 URL。

常用请求：

> 解读这篇论文，重点分析对 RSI 的价值，提交到每日观察供审阅。

> 把我们刚才讨论的论文整理成解读，保留争议和局限，先给我草稿。
