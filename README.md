# xai

CLI tool for searching and browsing X (Twitter) content via xAI API.

## Installation

```bash
uv tool install .
```

Or run directly:

```bash
uv run xai --help
```

## Setup

Set your xAI API key:

```bash
# Option 1: Environment variable
export XAI_API_KEY="xai-xxx"

# Option 2: Interactive setup
xai config init

# Option 3: Direct config
xai config set api_key "xai-xxx"
```

## Usage

### Search X posts

```bash
xai search "Rust programming"
xai search "OpenAI" --from 2025-12-01 --to 2026-01-31
xai search "AI news" --from-user @elonmusk --from-user @OpenAI
xai search "AI" --exclude @spam_bot
xai search "infographic" --images
xai search "Bitcoin" --format json
xai search "topic" --no-stream
```

### Search user posts

```bash
xai user @elonmusk
xai user @elonmusk --from 2026-01-01
xai user @elonmusk "about SpaceX"
```

### Get a thread

```bash
xai thread https://x.com/user/status/123456789
xai thread https://x.com/user/status/123456789 --summary
```

### Trending topics

```bash
xai trending
xai trending --category tech
xai trending "topic name"
```

### Web search

```bash
xai web "latest Python release"
xai web "AI research" --domain arxiv.org --domain openai.com
xai web "news" --exclude-domain reddit.com
```

### Configuration

```bash
xai config init                            # Interactive setup
xai config set default_model grok-4-1-fast # Change model
xai config get default_model               # Get a value
xai config list                            # Show all settings
```

### List models

```bash
xai models
xai models --format json
```

## Output formats

- **text** (default) -- Plain text with streaming
- **json** (`--format json`) -- Full API response as JSON, suitable for piping to `jq`
- **markdown** (`--format markdown`) -- Rich Markdown rendering

```bash
# Pipe JSON to jq
xai search "AI" --format json | jq '.output'

# Save to file
xai search "Rust" > results.txt
```

## Configuration file

Stored at `~/.config/xai/config.toml`:

```toml
[auth]
api_key = "xai-xxx"

[defaults]
model = "grok-4-1-fast-non-reasoning"
stream = true
format = "text"

[search]
enable_image_understanding = false
enable_video_understanding = false
```

### Priority (high to low)

1. Command-line flags
2. Environment variables (`XAI_API_KEY`, `XAI_DEFAULT_MODEL`)
3. Config file
4. Built-in defaults

## Claude Code Plugin

This repository is also a Claude Code plugin that provides the `xai` skill.

```bash
claude plugin marketplace add tani-shi/xai-cli
claude plugin install xai-cli@xai-cli
```

The skill enables Claude Code to use `xai` commands for searching X posts, browsing user timelines, retrieving threads, discovering trending topics, and performing web searches.

## Development

```bash
uv sync
uv run pytest
uv run ruff check src/ tests/
```

## License

MIT
