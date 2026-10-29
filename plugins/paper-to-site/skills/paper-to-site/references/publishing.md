# 直接发布与可选审阅

## 选择路径

目标为 `aprilvkuo/daily-observations`，网站 `https://brief.egguo.com`。用户说“发布”“入站”即授权本次文章直接上线；稿件已完成就继续发布，不追加 PR 审阅或再次确认。仅要求解读/草稿时完成稿件即可。只有用户明确要求“提交审阅”“创建 PR”才走审阅路径。

先读取实时默认分支、`scripts/content.py`、已有文章并核对当前接口。新文章优先使用 Make 场景8162821；修订、图片资源或 dispatch 容量等限制时，使用有权限的 GitHub 连接直接提交文章。任一路径都先检查内容，再等待生产 Actions 并核对文章 URL。Make 与 GitHub 是替代入口，不要求同时具备两种写权限。

没有可用的发布连接或实际权限被拒绝时，返回稿件和配对文件，准确说明阻断原因及尚未上线；不要把缺少本地终端误认为无法通过 Make 发布，也不要静默改成等待 PR。本文的直接发布授权只覆盖本次文章和必要图片，网站程序/工作流的修改按独立开发任务处理。

## 首选：Make 发布新文章

复用现有场景 `8162821`，不修改场景、连接或08:00任务。调用前读取接口和模块，确认仍是转发到目标仓库的dispatch。

输入名 `dispatch_json`，值是以下对象的标准JSON序列化文本：

- `event_type`: `publish-article`
- `client_payload.article`: 符合article-schema.md的完整文章对象

1. 先在 `client_payload` 追加 `validation_only: true` 发送一次。查看对应 GitHub Actions 成功并确认没有写入档案。
2. 验证通过后，使用同一篇文章去掉该标志发送一次正式发布，无需再次要求用户确认。复用相同文章内容和时间戳。
3. Make accepted只表示GitHub接受事件。查看匹配的生产运行，确认归档、构建和部署成功。
4. 检查 `https://brief.egguo.com/articles/<slug>.html` 的可访问性与标题/正文，并核对论文列表；成功后返回文章和Actions链接。

超时或结果未知时，先查 Make 执行记录、对应Actions、目标文章 JSON 和网页，判断验证/发布到了哪一步；不能盲目重发。验证失败时修复文章再验证。已归档但部署失败时先处理或报告部署错误，不重复归档。

当前 dispatch 不支持已核验的文章覆盖参数。相同slug且内容相同可视为已有档案并核对部署；内容不同的修订转到下面的GitHub直接提交路径，不能编造 `replace` 参数或改slug重复发布。文章超过dispatch当前限制时也用GitHub路径，不截短正文。

## 直接提交文章到 GitHub

适用于有默认分支写权限的 GitHub 工具或已验证的本地 checkout，尤其是修订、超长文章和本地图片：

1. 读取实时默认分支 head SHA 和 tree SHA，查重并读取现有文件。新文与修订遵循article-schema.md，JSON.markdown与同名.md逐字一致，修订保持原slug/date/generated_at。
2. 有终端时复用下方真实验证器和构建；有Make时也可先用validation_only验证完整文章对象。两者均不可执行时按实时schema检查字段、日期、正文配对和资源路径，如实注明本地检查未运行。
3. 基于读取的tree创建仅修改 `articles/<slug>.json`、同名.md和必要 `web/` 顶层图片的新tree，以该head为parent创建commit。核对diff包含完整文章且没有混入站点程序或其他人的改动。
4. 将实时默认分支更新到该commit；使用 `expected_sha` 匹配读取的head、`force: false`。本地git则普通push，禁止强推。分支若已前进，先读取新head和目标文件；仅当本篇文章未被他人修改时重建提交，否则保留冲突差异并说明情况。权限/保护规则拒绝写入时报告实际原因，不尝试绕过。
5. 等待该commit对应的生产Actions完成，再检查文章URL和论文列表。CI尚未结束就报告“发布处理中”；失败就修复本次文章或说明具体错误，不声称已上线。

本地有终端时先检查仓库规则和未提交改动，用临时分支或隔离checkout准备内容，不覆盖用户工作；必要的代码校验通过后才将该文章提交推送至目标默认分支。可用现有文章入口：

```python
import json
from pathlib import Path
from scripts.content import ingest_article

article = json.loads(Path('/absolute/path/article.json').read_text())
# 已检查的仓库根。只有修订本篇已存在文章时传replace=True。
ingest_article(Path.cwd(), article)
```

复用仓库依赖环境，运行：

```sh
python -m unittest discover -s tests -v
node tests/test_compare.cjs
node tests/test_library.cjs
python scripts/pipeline.py build --base-url https://brief.egguo.com
git diff --check
```

有预览能力时检查论文列表、元数据与来源链接、公式/代码/Mermaid/图片/目录和手机宽度。没有的能力如实标明，不用虚构的“CI已通过”替代真实结果。

## 只有明确要求审阅时：PR

从实时默认分支head/tree准备同样的文章文件，创建tree和commit、唯一的 `publish/<slug>` 分支，再创建面向默认分支的PR。已有分支先读取状态，不覆盖他人工作。可用时将PR附加到当前任务。

查看PR的 `preview.yml` 检查与 `research-library-preview` 产物，报告实际状态。此路径只提交审阅；合并后的生产Actions才发布。用户后续明确改为直接发布时，继续使用上述发布入口，不再把PR作为必经步骤，也不夹带其他PR改动自动合并。
