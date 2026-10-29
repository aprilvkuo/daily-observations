# Paper-to-site skill implementation plan

**Goal:** Let the user request a sourced paper reading or package an existing discussion in Chat, then submit it to daily-observations for review.

**Architecture:** A portable instruction-only skill bundled as a private plugin. It uses the existing article schema, GitHub branch/PR tools, and optional Make publication route. No new server, scheduler, or site renderer.

**Constraints:** Default to PR review. Only explicit direct-publication authorization permits Make dispatch. Keep the 08:00 report, Make configuration, main branch, routes, and RSS unchanged. Never claim unread evidence, unrun checks, or an unverified deployment.

## Tasks

- [x] Inspect the current article validator, ingestion, build, PR preview, and Chat skill documentation.
- [x] Run an isolated no-skill reference scenario. Baseline produced an incompatible flat article schema and a revision timestamp violating the same-day validator rule.
- [x] Write `plugins/paper-to-site/skills/paper-to-site/SKILL.md`, UI metadata, writing guidance, schema, and publication references. Keep the package usable without a local checkout.
- [x] Validate YAML/JSON, contained references, plugin layout, and article examples with the real site validator. Run the same independent scenarios with the skill; revise any concrete failures.
- [x] Run existing Python and Node tests and build; ensure no new articles or production workflow changes.
- [x] Package and inspect one private plugin archive, save it with Plugin Creator, and fetch back its files to confirm the skill was retained. Installation and connections remain separate evidence.

Release step: submit only the skill/package/docs through a GitHub PR, attach it to this chat, and check CI. Do not merge the PR automatically.

## Validation evidence

- Skill Creator format validation, manifest/UI YAML/SVG parsing, contained reference checks and archive integrity passed.
- Independent offline application covered full-text fixture, abstract-only/read-only access, v2 revision, and unknown Make result. The fixture's matching JSON/Markdown passed the actual validator and isolated archive/detail/list/RSS build; headings and Mermaid were retained. No fixture entered the real archive.
- Existing 23 Python tests, both Node suites and production-site build passed; archive remained at three reports and no articles.
- Private USER-scoped plugin version 0.1.0 was saved; its entrypoint, UI metadata and all three references were fetched back and matched the packaged source. This does not assert installation, new-Chat invocation or production article publication.

## Acceptance

In Chat, the user can select the installed skill/plugin and provide a URL, PDF, or existing discussion. The skill preserves verified source versions, produces matching Markdown/JSON, and returns a PR plus its actual check status. With missing tools it returns a publishable handoff and states that it has not submitted or published. Source files and a private plugin link are delivered; no test paper is published.
