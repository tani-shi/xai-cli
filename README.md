# xai-cli

A thin CLI over xAI's Responses API. Grok answers a question with the server-side X Search or Web Search tool, and the CLI prints the answer and the sources the search used.

## Install

```bash
uv tool install git+https://github.com/tani-shi/xai-cli
```

Claude Code plugin with the `xai` skill:

```bash
claude plugin marketplace add tani-shi/xai-cli
claude plugin install xai-cli@xai-cli
```

## Setup

Set `XAI_API_KEY`, or on macOS store the key in the Keychain:

```bash
security add-generic-password -a "$(id -un)" -s xai-api-key -U -w
```

The model defaults to `grok-4.7`; override it with `XAI_DEFAULT_MODEL`.

## Usage

```bash
xai search "QUERY" [--from YYYY-MM-DD] [--to YYYY-MM-DD] [--from-user HANDLE]... [--exclude HANDLE]... [--images] [--video] [--json]
xai web "QUERY" [--domain DOMAIN]... [--exclude-domain DOMAIN]... [--images] [--json]
```

- Dates are UTC and both ends are inclusive.
- Options map to the [X Search](https://docs.x.ai/developers/tools/x-search) and [Web Search](https://docs.x.ai/developers/tools/web-search) tool parameters; xAI validates them.
- Text output ends with a `Sources:` list. `--json` prints `response_id`, `model`, `text`, `sources`, and `usage`.
- `sources` are the results the search used, not citations of specific sentences.
- Exit status: `0` success, `1` API, network, or key error, `2` invalid arguments.

## Development

```bash
uv sync
uv run ruff format --check . && uv run ruff check . && uv run mypy && uv run pytest -m "not live"
XAI_LIVE_TEST=1 XAI_API_KEY=... uv run pytest -m live tests/live
```

## License

[MIT](LICENSE)
