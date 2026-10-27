# 研究知识库改版

按用户已明确授权的范围开发，通过 PR 审阅，不部署分支。

保留纸白、墨绿、古铜金。首页以最新简报为重点，三个明确入口分别通向每日简报、论文解读、专题研究。旧日报栏目放入首页次级链接，Top10、RSS 保持可达。

复用 Python 生成器及 articles JSON/Markdown 双档案；可选 content_type 为 paper/research，缺省 research。论文支持 tags、paper 元数据（arxiv_id、title、authors、published、abstract、url、pdf_url、code_url），不联网猜补数据。旧 category 与 publish-article 输入保持兼容。论文规范地址继续为 articles/slug.html，新增 papers.html、studies.html；所有旧路由与 RSS guid 保留。

独立文章采用安全 Markdown 渲染，原始 HTML 禁用；支持层级标题与唯一锚点目录、公式、服务端代码高亮、Mermaid、图片、表格和移动端排版。公式与图表使用固定版本浏览器依赖；加载失败仍保留公式或图表源码。数学和 Mermaid 内容不执行任意 HTML。

论文列表服务端输出全部条目，浏览器渐进增强搜索、标签筛选、日期升降序与空结果提示。无论文时显示真实空态，测试论文只放 tests 或本地预览，不进入公开档案。

现有报告输入、归档、数据、Top10 比较算法和完整 RSS 正文不改。Make 8162821 按需 dispatch 接口不改，08:00 上游任务不改。PR 工作流只测试、构建、上传预览产物；生产工作流仍仅 main/dispatch/手动部署。

验证：旧测试全通过；新增验证兼容性、元数据安全、唯一目录、渲染、空态、论文/专题隔离、原始档案与 RSS 一致；浏览器检查桌面/手机、筛选排序、旧链接与渲染失败回退。
