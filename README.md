# xai-cli

`xai-cli` generates cited answers from X and the web through xAI's server-side X Search and Web Search tools.

The `search`, `user`, `thread`, `trending`, and `web` commands are agentic research commands. They ask Grok to search, inspect sources, and synthesize an answer. They do not expose a raw post, timeline, trend, or search-results API.

## Requirements

- Python 3.12 or later
- An [xAI API key](https://console.x.ai/)

## Installation

```bash
uv tool install .
```

For development:

```bash
uv sync
uv run xai --help
```

## Authentication and configuration

The recommended setup is an environment variable:

```bash
export XAI_API_KEY="xai-..."
```

You can instead store the key through a hidden interactive prompt:

```bash
xai config init
# or
xai config set api_key
```

`config get api_key` and `config list` report only whether a key is configured. They never print any part of the key. Avoid putting a key in shell arguments or scripts.

Runtime values are resolved in this order:

1. Command options
2. `XAI_API_KEY` and `XAI_DEFAULT_MODEL`
3. The configuration file
4. Built-in defaults

The default model is the explicit search-capable model `grok-4.6`. Set another model with:

```bash
xai config set default_model MODEL
```

The configuration path is platform-specific and provided by `platformdirs`. Print the exact path with:

```bash
xai config path
```

The file is written atomically. On POSIX systems, its mode is enforced as `0600`, including existing files created by 0.1 releases.

## Commands

### Generate an answer with X Search

```bash
xai search "What are developers saying about a new release?"
xai search "AI launches" --from 2026-01-01 --to 2026-02-01
xai search "product update" --from-user @xai --from-user @elonmusk
xai search "topic" --exclude @spam_account
xai search "visual announcement" --images
```

`--from-user` and `--exclude` are mutually exclusive. Each accepts up to 20 handles. Dates are inclusive and use `YYYY-MM-DD`.

### Generate an answer about a user's posts

```bash
xai user @xai
xai user @xai "What product changes were announced?"
xai user @xai --from 2026-01-01 --to 2026-02-01
```

### Generate an answer about a thread

```bash
xai thread https://x.com/xai/status/1234567890
xai thread https://x.com/xai/status/1234567890 --summary
```

The URL must identify an X or Twitter status.

### Analyze trends on X

```bash
xai trending
xai trending "spaceflight"
xai trending --category tech
```

Categories are `tech`, `politics`, `sports`, and `entertainment`. A topic and category cannot be combined.

### Generate an answer with Web Search

```bash
xai web "What changed in the latest Python release?"
xai web "API reference" --domain docs.python.org --domain peps.python.org
xai web "tutorial" --exclude-domain medium.com
```

`--domain` and `--exclude-domain` are mutually exclusive. Each accepts up to five bare hostnames without a scheme, port, or path.

### List API models

```bash
xai models
xai models --format json
```

## Output contracts

All answer commands support `--format text`, `--format markdown`, and `--format json`. Progress and diagnostics go to stderr; stdout contains only the result.

- `text` writes the generated answer as plain UTF-8 text.
- `markdown` preserves the generated Markdown and renders it on an interactive terminal.
- `json` writes a stable CLI schema with `schema_version`, `response_id`, `model`, `status`, `text`, and `citations`.

Inline citations from the Responses API remain in the answer as `[[N]](url)`. Structured citation URLs are retained in JSON output.

Use `--raw` with JSON only when the complete xAI response is required:

```bash
xai search "xAI updates" --format json | jq '.citations'
xai search "xAI updates" --format json --raw | jq '.output'
```

Text and Markdown stream by default when streaming is enabled in the configuration. `--no-stream` requests a complete response before writing it. JSON is always non-streaming so it remains valid JSON.

POST requests are retried at most twice only when xAI returns `Retry-After` with HTTP 429 or 503 and the requested delay is no more than two seconds. Ambiguous 500, 502, and 504 responses are not replayed.

## Configuration commands

```bash
xai config init
xai config set default_model grok-4.6
xai config set stream false
xai config set format markdown
xai config get default_model
xai config list
xai config path
```

Supported keys are `api_key`, `default_model` (alias `model`), `stream`, `format`, `enable_image_understanding`, and `enable_video_understanding`.

## Compatibility notes for 0.2

- Command names and the principal search options remain available.
- The default model changed from the retired `grok-4-1-fast-non-reasoning` slug to `grok-4.6`.
- JSON now uses a stable CLI schema. Pass `--raw` to request the previous full-response style.
- `xai config set api_key VALUE` is intentionally rejected because shell arguments are visible. Use the hidden prompt without `VALUE`.
- Thread URLs, categories, formats, dates, handles, domains, limits, and mutually exclusive filters are validated before a request is sent.
- API and streaming failures now use documented nonzero exit codes instead of returning partial or silently ignored data.

## Exit codes

| Code | Meaning |
| ---: | --- |
| 1 | General error |
| 2 | Invalid syntax, request, or option combination |
| 3 | Authentication or authorization error |
| 4 | xAI API or stream error |
| 5 | Rate limit exceeded |
| 6 | Network error or timeout |
| 7 | Configuration error |
| 8 | Incomplete response or interrupted protocol |

## Claude Code plugin

This repository also packages an `xai` skill:

```bash
claude plugin marketplace add tani-shi/xai-cli
claude plugin install xai-cli@xai-cli
```

## Development and verification

```bash
uv sync --locked
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest -m "not live"
uv build
```

Live API tests are separate from the normal suite and run only when explicitly enabled:

```bash
XAI_LIVE_TEST=1 XAI_API_KEY="xai-..." uv run pytest -m live tests/live
```

CI checks formatting, lint, types, unit tests on Python 3.12 and 3.13, wheel and source-distribution builds, and installed CLI smoke tests.

## License

[MIT](LICENSE)
