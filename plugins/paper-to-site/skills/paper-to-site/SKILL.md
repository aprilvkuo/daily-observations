---
name: paper-to-site
description: Use when the user wants a Chinese paper reading from an arXiv link or PDF, wants to turn an existing paper discussion into an article, or wants that reading submitted to 每日观察 / aprilvkuo/daily-observations. General paper questions without an article goal do not need this skill.
---

# 论文解读与发布

将论文或当前讨论整理成有来源、可阅读的每日观察文章。仓库 `aprilvkuo/daily-observations`，网站 `https://brief.egguo.com`。用户要求发布或入站时，默认直接发布；只有明确要求审阅时才创建 PR。

## 先判断用户要什么

- “解读”且未要求入站：完成有来源的解读草稿，不上线。
- “整理刚才讨论”：保留用户的问题、判断与关注点，核验讨论中引用的证据，不把他人或模型的观点归给用户。
- “发布 / 入站 / 发布到每日观察 / 直接上线”：完成必要检查后直接发布，不要求额外的 PR 或再次确认。此前用户已要求发布且稿件已完成时，继续完成发布。
- “提交审阅 / 创建 PR / 先别上线”：按用户明确要求提供审阅 PR 或保留草稿。用户后续改为直接发布时，以最新指令为准。

按当前聊天实际能力执行。Chat 不保证有本地终端；已安装此技能也不代表已有 GitHub/Make 授权。先检查可用工具。直接发布优先复用 Make 场景8162821；修订、资源文件或其他入口限制可用有权限的 GitHub 连接提交文章到默认分支。缺少发布能力时保留稿件和文件，说明具体缺少的权限或工具，不把 PR 审阅当作默认前置条件。

## 阅读与写作

读 [writing.md](references/writing.md)。核对论文版本、原文、实验与局限；没有读到全文就说明范围，不生成伪装成全文解读的完成稿。元数据、代码和结论均需可追溯，未核验字段省略。

用中文写清问题、方法、实验与判断，按用户关注点取舍。公式、代码、Mermaid、图片服务于解释。网页里的证据引用使用可点击的普通 Markdown 来源链接与章节/图表编号；不要把聊天专有引用标记当成网页来源。

## 组织文章并提交

读 [article-schema.md](references/article-schema.md) 和 [publishing.md](references/publishing.md)。JSON 的 `markdown` 与同名 `.md` 必须完全一致；用 JSON 序列化工具保存换行和反斜杠。论文类型为 `content_type: paper`，arXiv 元数据放在 `paper` 对象内。

先读取当前仓库的 validator 和已有文章，按不含版本号的 arXiv ID、原文 URL 与标题查重。修订保留已有 slug、date 和 generated_at；正文注明修订日和版本变化，显式调整解读日期时同步调整时间戳。不得凭空发明一个与 date 不同日的 generated_at。

有终端时复用仓库验证器、测试和构建；无终端时优先使用 Make 的 validation_only 检查，再发布并等待生产 Actions。明确要求 PR 时才依赖 PR CI。没有运行的本地检查如实标明；验证失败时修复稿件后重试。

仅修改本次文章和需要的图片资源；保持日报、08:00 任务、Make 配置、Top10、RSS 生成逻辑和生产工作流不变。

## 返回可核对的结果

简述文章主题、阅读来源及版本。发布后提供文章 URL 和对应 Actions 结果；明确要求审阅时提供 PR 链接。区分“草稿已准备”“发布请求已接受”“Actions 已通过”“文章已上线”，没有证据的步骤保持待完成。不能把 Make accepted 或文件已生成等同于上线。

常用请求：

> 解读这篇论文，重点分析对 RSI 的价值，发布到每日观察。

> 把我们刚才讨论的论文整理成解读，保留争议和局限，先给我草稿。
