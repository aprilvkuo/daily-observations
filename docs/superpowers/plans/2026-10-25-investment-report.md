# Investment Report Implementation Plan

**Goal:** Publish complete daily reports, Markdown/JSON archives, RSS and Top10 comparisons through an isolated public repository.
**Architecture:** Existing 08:00 analysis remains the only producer. Make dispatches its complete JSON to GitHub; Actions validates and commits immutable daily archives, builds a static site, then deploys Pages. No analysis cron.
**Tech Stack:** Python 3.11 standard library, GitHub Actions/Pages, HTML/CSS/JS, Make GitHub REST.

## Constraints
- Repository aprilvkuo/investment-report only; do not change blog or stock_agent.
- Asia/Shanghai report dates; 08:00 is production start, publication occurs after completion.
- No fabricated financial data or reconstructed reports. Empty state until real report supplied.
- Reject invalid dates, duplicate ticker identities, incomplete reports and conflicting same-date writes.
- Render untrusted Markdown as escaped text; RSS includes full body.

## Execution
- [ ] Write failing behavior tests for validation, idempotency, archive output, safe HTML, full RSS, ranking movements and empty state.
- [ ] Implement scripts/pipeline.py and web assets; run unittest discovery.
- [ ] Add ingestion/build/deploy workflow with serialized publishing, no scheduled analysis, least job permissions.
- [ ] Create public repository, push tested source, enable Pages; verify Actions and served index/feed.
- [ ] Inspect existing task and Make logs; prepare on-demand publisher and request missing GitHub authorization.
- [ ] Configure custom hostname only with DNS confirmation; verify DNS and HTTPS independently.
