# 发布状态与继续接入

## 2026-10-27 仓库改名

当前公开仓库：https://github.com/aprilvkuo/daily-observations 。仓库 ID 1432771914 不变，旧仓库地址作为历史记录保留。网站仍为 https://brief.egguo.com/ ，SITE_URL 不变。Make 8162821 的 dispatch 地址及返回的 Actions 链接已同步至新名称。下面按日期记录的旧地址属于当时快照。

核查日期：2026-10-25（Asia/Shanghai）。

## 已验证

- 独立公开仓库：https://github.com/aprilvkuo/investment-report
- 网站：https://aprilvkuo.github.io/investment-report/ ，首页和feed.xml均HTTP 200。
- 首次Pages部署运行40155683163成功。
- Make发布场景8162821已启用，按需触发，无分析、无定时器、无飞书/邮件消息模块。
- 场景：https://eu1.make.com/2991244/scenarios/8162821
- GitHub OAuth连接已由用户授权；连接健康状态ok。
- Make执行09a73e0a087349e297ae3e7bdc9aec06成功；GitHub API返回204。
- 对应GitHub repository_dispatch运行40155890246成功，日志明确Validation only; no archive written，Reports built: 0。无测试日报公开发布。
- 修复后推送运行40156022614成功。
- 六项本地测试通过；独立审查提出的并发排队丢失和缺榜单误报退出均已修复。

## 原有Make场景

Send Daily Brief to Feishu（7689324）启用、按需运行，最近运行成功。它没有08:00定时器，2026-10-25输入为“每日重点简报”，不能当成三市场完整日报。未改动、未触发此消息场景。

## 待登录后完成

- 原ChatGPT每天08:00三市场任务的身份、完整指令、时区、插件执行能力和完整输出尚未核验。任务页面读取失败，应用内浏览器转登录页。没有创建替代分析任务。
- Cloudflare当前为登录页。用户已同意新增invest CNAME，但DNS尚未写入。
- Pages自定义域名和HTTPS证书尚未配置，保留可用临时网址。
- 尚无真实完整日报，历史及RSS为空。

## 域名操作

1. Cloudflare → egguo.com → DNS，仅新增CNAME invest → aprilvkuo.github.io，DNS only，TTL Auto。
2. 核验公共DNS后，将仓库Pages自定义域名设为invest.egguo.com，等待证书就绪并开启Enforce HTTPS。
3. 仓库变量SITE_URL设为https://invest.egguo.com，手动运行发布工作流。核验首页、feed.xml、Top10页及HTTPS。

## 追加到原任务的发布步骤

保留原分析范围、08:00（Asia/Shanghai）时间和单次分析流程。完成完整报告后，使用完全相同的Markdown正文与原报告明确给出的总Top10，包装为README中的report对象。不缩写、不截断，不补造未知榜单。原报告无结构化Top10则传空数组。

调用Make私人空间场景“Publish Three-Market Daily Report to GitHub Pages”（8162821）一次。输入dispatch_json为完整JSON文本：

```json
{"event_type":"publish-report","client_payload":{"report":{"说明":"替换为README定义的完整report对象"}}}
```

正式发布不包含validation_only。GitHub accepted仅代表受理；须核验Actions归档与部署完成，否则明确说明待验证。不要为发布另作分析，不额外调用飞书或邮件场景，不重复发送摘要。失败时保留原文、说明错误，不以摘要代替正文。若原任务不能调用Make插件，不声称自动接通。

## 限制

GitHub dispatch存在payload大小上限，超限失败并保留完整原文，不截断。公开档案仅接收可公开研究报告，不能含账户信息、持仓数量、密钥或私人Webhook地址。本仓库无模型API调用或新增分析定时任务；Make实际操作消耗以执行记录为准。


## 2026-10-25用户追加要求

用户要求将“每日重点简报”与“三市场长期价值监控”统一成一个整体，包含金融、科技等多个维度。网站现采用“每日观察”，每期一份原文、一个RSS条目，提供金融、科技、AI/RSI栏目视图，并保留三市场Top10历史比较。

界面已确认两个任务均为活跃、显示每天08:00。三市场任务ID为6a9b01e36c1881919486422af4f7bc54。原完整提示词和插件能力尚未核验，因此未改写或停用任何任务。Chrome被其他任务并行操作且页面控制超时，用户明确选择“先完成网站，任务稍后合并”。不要据本次网站部署声称两个任务已合并。

下一阶段：核验并备份两个任务提示词，合并全部内容要求；保留一个08:00任务，另一个暂停而非删除。复用Make场景8162821，每期只发布一次。以网页/RSS为主要阅读入口，避免另发重复摘要。域名DNS仍待可安全操作Chrome时完成；既有授权有效，不必重复请求同一DNS变更的确认。

## 个人综合站扩展

用户接受“每日观察 / brief.egguo.com”与每日简报、RSI研究、科技与AI、金融与投资、专题笔记结构。增加独立文章Markdown/JSON归档、分类页、统一RSS与publish-article事件。定时任务合并继续暂缓。旧invest域名从未实际配置，不需删除其DNS。

## 日报与网站栏目适配

正式站点：https://brief.egguo.com/ ，订阅：https://brief.egguo.com/feed.xml 。
日报中的五个二级标题依次是：今日总览、金融与市场、科技与产业、AI与RSI、风险与行动。
网站从同一份 Markdown 自动提取这五个维度；首页、导航、栏目页面名称一致。
`research.html` 兼容原入口，直接显示 AI与RSI 日报和已有 RSI 独立文章；
`notes.html` 兼容原入口，显示风险与行动及已有专题笔记。独立文章不是日报栏目展示的前置条件。
标题可含常见编号、加粗和空格，但生产任务仍建议保持标准标题；代码块中的标题不会分类。
仅有一期 Top10 时显示当期榜单；两期以上才有历史比较依据。
原始 JSON/Markdown 及 RSS 不复制、不拆分，历史内容修订仍需显式审阅提交。
