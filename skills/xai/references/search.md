# Search

## Search X posts

```bash
xai search "<query>" [--from DATE] [--to DATE] [--from-user USER]... \
  [--exclude USER]... [--images] [--format FORMAT] [--no-stream]
```

Searches X posts matching the given query.

- `--from DATE` — only posts after this date (YYYY-MM-DD)
- `--to DATE` — only posts before this date (YYYY-MM-DD)
- `--from-user USER` — filter by post authors (repeat for multiple users)
- `--exclude USER` — exclude posts from these users (repeat for multiple users)
- `--images` — enable image understanding
- `--format FORMAT` — output format (`text`, `json`, `markdown`)
- `--no-stream` — disable streaming output

## Examples

```bash
# Search for recent posts about a topic
xai search "Claude AI" --from 2026-03-06

# Search posts from specific users
xai search "announcement" --from-user elonmusk --from-user xaboratories

# Search with image understanding
xai search "infographic" --images --format json

# Search within a date range
xai search "product launch" --from 2026-01-01 --to 2026-02-01
```
