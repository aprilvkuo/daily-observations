# 提交与发布

## 仓库与能力检查

目标为 `aprilvkuo/daily-observations`，网站 `https://brief.egguo.com`。先读取实时默认分支、`scripts/content.py`、`docs/research-library.md` 和现有文章；不要假定聊天运行在某个本机目录、已装 gh 或拥有推送权限。

默认创建 PR，不调用会直接修改 main 的 dispatch，也不自动合并。按用户已授权范围直接完成建分支和 PR，无需再次询问。只读 GitHub 连接可用于查重；缺写权限时返回完整 JSON、Markdown 及预期路径，说明尚未提交。不要通过 Make 直接上线来绕过 PR 权限问题。

## 路径一：Chat 中使用 GitHub 连接

适用于可用工具能读取仓库并创建 tree、commit、branch、PR 的聊天：

1. 从最新默认分支读取 head SHA 和 tree SHA，完成查重与 schema 检查。
2. 将文章序列化为 UTF-8 JSON及一致的Markdown，提交两份文件。若有图片，使用该连接实际支持的文件写入方式；不要以文本工具伪装二进制图片。
3. 基于读取的 tree 新建 tree，创建以该 head 为parent的commit，再建立唯一 `publish/<slug>` 分支；已有分支则读取状态，避免覆盖他人工作。不得把提交指向main。
4. 创建面向默认分支的 PR，描述论文及版本、文章关注点、资源、修订变化和实际验证。可用时将 PR 附加到当前任务。
5. 查看 PR 的 CI。成功后提供结果；若尚未结束，写“CI待完成”。失败时读日志并修复文章，未知网络状态先查远端是否成功，不盲目重复创建。

Chat 没有终端时不能声称跑过本地测试或看过本地预览。PR的 `preview.yml` 负责 Python/Node测试、构建和 `research-library-preview` 下载产物，不会部署。CI通过不等于文章已上线；只有合并并完成生产Actions后才会发布。

## 路径二：有终端与已验证的本地 checkout

读取仓库 AGENTS.md 等适用规则，检查未提交改动，基于最新默认分支建立独立发布分支，不覆盖用户的修改。复用仓库环境安装 `requirements.txt`，不要假定系统Python已经有依赖。

以完整文章 JSON 写入文章：

```python
import json
from pathlib import Path
from scripts.content import ingest_article

article = json.loads(Path('/absolute/path/article.json').read_text())
# 在已检查的仓库根运行；修订时仅在用户要求修订现有文章后传replace=True。
ingest_article(Path.cwd(), article)
```

`ingest_article` 同时调用真实验证器并保存匹配的JSON/Markdown。新文覆盖已有slug会失败；修订才使用 `replace=True`。也可复用 `scripts/content.py --help` 的 Markdown+元数据入口。

完成后在仓库环境运行：

```sh
python -m unittest discover -s tests -v
node tests/test_compare.cjs
node tests/test_library.cjs
python scripts/pipeline.py build --base-url https://brief.egguo.com
git diff --check
```

检查 `dist/papers.html` 和 `dist/articles/<slug>.html`；有浏览器时检查列表归类、元数据与来源链接、公式/代码/Mermaid/图片/目录和手机宽度。核对diff只有文章及必要资源，然后提交分支、创建PR。凭实际连接能力选择git或GitHub工具，失败后不假报推送成功。

## 仅在明确授权直接上线时：Make

复用现有场景 `8162821`，不要新建或修改场景/连接/08:00任务。调用前读取当前接口和模块，确认仍是转发到目标仓库的dispatch。

输入名 `dispatch_json`，值是对以下对象的标准JSON序列化文本：

- `event_type`: `publish-article`
- `client_payload.article`: 符合article-schema.md的完整文章对象

先在 `client_payload` 追加 `validation_only: true` 运行一次，查看对应 GitHub Actions 成功并确认未写档案，再使用同一篇文章去掉该标志发送一次。Make accepted仅表示GitHub接受事件，不表示归档或部署成功。读取匹配的运行与文章URL验证完成；超时或结果未知时先查运行和目标文章，不能盲目重发。

既有同slug文章的修订走PR：当前dispatch没有经过确认的覆盖入口，不能编造 `replace` 参数。若正文超过GitHub dispatch当前限制，使用PR，不截短用户文章或分段伪造多篇。

直接发布必须有当前聊天可用的Make工具和授权连接。缺少工具时保留PR或文件交付；不要将生成了dispatch JSON描述为已发布。
