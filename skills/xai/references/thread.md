# Thread

## Retrieve a thread

```bash
xai thread <URL> [--summary] [--format FORMAT] [--no-stream]
```

Retrieves and displays a full thread from a post URL.

- `--summary` — show summary instead of full thread
- `--format FORMAT` — output format (`text`, `json`)
- `--no-stream` — disable streaming output

## Examples

```bash
# Retrieve a thread by URL
xai thread https://x.com/user/status/1234567890

# Retrieve and summarize a thread
xai thread https://x.com/user/status/1234567890 --summary

# Get thread as JSON
xai thread https://x.com/user/status/1234567890 --format json
```
