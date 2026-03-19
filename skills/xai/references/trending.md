# Trending

## Discover trending topics

```bash
xai trending [topic] [--category CATEGORY] [--format FORMAT] [--no-stream]
```

Shows currently trending topics on X.

- `topic` — optional topic for detailed trending posts (positional argument)
- `--category CATEGORY` — topic category filter (tech, politics, sports, entertainment)
- `--format FORMAT` — output format (`text`, `json`)
- `--no-stream` — disable streaming output

## Examples

```bash
# Get global trending topics
xai trending

# Get trending posts about a specific topic
xai trending "AI"

# Get trending in a specific category as JSON
xai trending --category technology --format json
```
