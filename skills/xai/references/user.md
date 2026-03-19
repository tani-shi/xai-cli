# User

## Browse user timeline

```bash
xai user @<username> [query] [--from DATE] [--to DATE] [--format FORMAT] [--no-stream]
```

Retrieves posts from the specified user's timeline.

- `query` — optional topic filter (positional argument)
- `--from DATE` — only posts after this date (YYYY-MM-DD)
- `--to DATE` — only posts before this date (YYYY-MM-DD)
- `--format FORMAT` — output format (`text`, `json`)
- `--no-stream` — disable streaming output

## Examples

```bash
# Get recent posts from a user
xai user @elonmusk

# Get posts from a user about a specific topic
xai user @elonmusk "AI announcements"

# Get posts from a date range
xai user @xaboratories --from 2026-02-28

# Get user timeline as JSON
xai user @anthropic --format json --from 2026-03-01
```
