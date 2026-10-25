# Daily report adaptation plan

Goal: make the published daily report the source for all five reading dimensions.
Architecture: keep immutable Markdown/JSON and one RSS item per report. Build research from AI/RSI, notes compatibility route from actions, and show standalone articles only when present. Normalize known heading aliases without rewriting source text.

- [x] Add regression tests for daily-only research/actions pages, five homepage links, tolerant headings and no empty article block.
- [x] Implement shared topic rendering and explicit heading aliases, keeping fenced examples excluded.
- [x] Show single-date Top10 as a snapshot without invented historical change.
- [x] Run tests and build against today's real report; inspect generated pages and links.
- [ ] Commit, deploy, and verify live pages and RSS preserve original content.
