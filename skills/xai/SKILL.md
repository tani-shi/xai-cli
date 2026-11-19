---
name: xai
description: >
  Research X (Twitter) posts or the web through xAI's Grok with the `xai` CLI, which returns an
  answer and its sources. Use it for what people say on X, a user's posts, a thread, trends, or
  web research through xAI. Not for other meanings of X.
---

# xai

```bash
xai search "QUERY" [--from YYYY-MM-DD] [--to YYYY-MM-DD] [--from-user HANDLE]... [--exclude HANDLE]... [--images] [--video] [--json]
xai web "QUERY" [--domain DOMAIN]... [--exclude-domain DOMAIN]... [--images] [--json]
```

- Write the task in QUERY. For a user's posts, a thread, or trends, use `search` with a question about it, plus `--from-user` or a post URL in QUERY.
- Dates are UTC and inclusive. Narrow dates and handles to reduce cost; X Search bills per post fetched.
- The answer is Grok's summary. `Sources:` (or `sources` in `--json`) lists what the search used, not which sentence cites what. Check important facts in the sources.
- xAI does not always apply `--from-user`, `--exclude`, or date filters. When they matter, open the sources and check authors and dates.
- Exit status `1` prints the xAI or key error on stderr; `2` means invalid arguments.
