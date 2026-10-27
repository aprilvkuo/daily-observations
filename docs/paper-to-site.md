# 在 Chat 中解读和发布论文

`plugins/paper-to-site` 是便携的技能插件源码，显示名为「论文解读与发布」。安装私有插件后，新开一个 Chat，输入 `@` 选择该插件或技能，附论文链接/PDF即可。无需为了阅读论文切换到本地开发窗口。

例如：

> 解读这篇论文：〈链接〉。重点分析它对 RSI 的价值，提交到每日观察供审阅。

也可以先在 Chat 里讨论，再说：

> 把刚才的讨论整理成论文解读，保留分歧和局限，先给我草稿。

仅要求解读/草稿不会创建 PR。要求“发布到每日观察”或“提交审阅”时，默认生成 `articles/<slug>.json` 与 `.md`，创建 PR；合并后由现有 Actions 发布。明确要求“直接上线”才走原Make场景8162821，日报08:00流程独立保持。

插件提供流程和资料，不附带新的 GitHub/Make 服务或权限。当前 Chat 需有可写GitHub连接才能提交PR；Make仅在直接上线时需要。没有相关能力时会返回文章与文件，说明尚未提交，不假报成功。无终端时本地测试标为未运行，查看PR的CI和构建预览产物。

ChatGPT官方说明：[技能编写与调用](https://learn.chatgpt.com/docs/build-skills)、[插件在Chat和Work中的使用](https://learn.chatgpt.com/docs/plugins)。独立技能适用于桌面端等支持的运行环境；打包插件用于跨Chat/Work复用，安装后以实际技能目录及账号权限为准。

技能的入口是 [SKILL.md](../plugins/paper-to-site/skills/paper-to-site/SKILL.md)，其中按需加载写作、文章字段和发布流程。已有格式规范见 [研究知识库与论文发布](research-library.md)。包内不包含密钥、本机绝对路径或示例论文档案。
