# Research library implementation plan

**Goal:** 在现有 Python 站点添加独立论文知识库，并保护现有发布契约。

**Architecture:** scripts/content.py 负责兼容的文章 schema 与详情，scripts/reading.py 负责安全 Markdown，scripts/library.py 负责首页和列表，web 中为静态渐进增强资源。

**Constraints:** 所有旧路由、报告原文、RSS guid、publish-report/publish-article、Make 8162821、08:00 上游均保留。不提交伪文章。不合并或部署 PR。

1. [x] 新增 tests/test_library.py，使用临时目录验证 metadata、论文分类、详情、锚点、安全渲染和 RSS；运行并确认新功能测试失败。
2. [x] 新增固定 Python 依赖和 reading.py；实现安全 Markdown、目录、高亮和公式/图表容器。接入可选 paper 元数据验证及 CLI --metadata-json，旧文章默认 research。
3. [x] library.py 构建 papers.html/studies.html、详情链接、首页三类内容；web/library.js 提供搜索标签日期排序；重做 CSS 与共享导航。
4. [x] 新增 PR-only CI：安装依赖、Python/Node 测试、完整构建、预览 artifact；现有部署仅加依赖安装。更新 README 发布规范。
5. [x] 运行完整 Python/Node 回归及站点构建，浏览器验证真实空态与仅本地 fixture 的富文本详情、筛选、移动端。确认原报告、RSS、Top10 和所有旧路由保持兼容。
6. [ ] 审查差异，提交分支并创建 PR，核验远端提交及 CI，附预览截图与验证结果供审阅。
