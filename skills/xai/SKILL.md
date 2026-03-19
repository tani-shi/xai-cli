---
name: xai
description: >
  Use the `xai` CLI to search X (Twitter) posts, browse user timelines, retrieve threads,
  discover trending topics, and perform web searches via the xAI API.
  Use when the user wants to search for posts on X/Twitter, see what someone tweeted,
  read a thread, check what's trending, or do a web search.
  Trigger on: "xai", "X", "Twitter", "tweet", "posts on X", "trending",
  "search X", "search Twitter", "what's trending", "check someone's timeline",
  "read this thread", "web search via xai", "find tweets about",
  or any request to search, browse, or retrieve content from X/Twitter.
  Do NOT trigger when the user mentions "X" in a non-Twitter context (e.g., "variable X").
---

# xai-cli — X (Twitter) & Web Search CLI

Use the `xai` command to search and browse X (Twitter) content and the web via the xAI API.

## Repository

<https://github.com/tani-shi/xai-cli>

## Installation

```bash
uv tool install .
```

## Prerequisites

- `XAI_API_KEY` environment variable must be set
- Run `xai config init` to set up configuration

## Output formats

- Default: human-readable text
- `--format json` — JSON output (use for parsing structured data)
- `--format markdown` — Markdown formatted output (search command only)

## Common flags

- `--format FORMAT` — output format (`text`, `json`; `markdown` supported by search)
- `--no-stream` — disable streaming output
- `--from DATE` — filter results after this date (search, user commands)
- `--to DATE` — filter results before this date (search, user commands)

## Command reference files

Load the relevant reference file based on which command the user needs:

- **Search** (search X posts by query): See [references/search.md](references/search.md)
- **User** (browse user timelines): See [references/user.md](references/user.md)
- **Thread** (retrieve and display threads): See [references/thread.md](references/thread.md)
- **Trending** (discover trending topics): See [references/trending.md](references/trending.md)
- **Web** (web search): See [references/web.md](references/web.md)
- **Config** (configuration and model management): See [references/config.md](references/config.md)

## Common patterns

### Multi-step workflows

When performing complex tasks (e.g., "find posts by a user about a topic"), chain commands:
1. Search or browse user timeline to find relevant posts
2. Retrieve a thread for full context if needed

### Checking available models

```bash
xai models
```

### Quick search

```bash
xai search "query" --from 2026-03-06
```
