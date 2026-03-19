# Web

## Web search

```bash
xai web "<query>" [--domain DOMAIN]... [--exclude-domain DOMAIN]... \
  [--format FORMAT] [--no-stream]
```

Performs a web search via the xAI API.

- `--domain DOMAIN` — restrict results to specific domains (repeat for multiple)
- `--exclude-domain DOMAIN` — exclude results from specific domains (repeat for multiple)
- `--format FORMAT` — output format (`text`, `json`)
- `--no-stream` — disable streaming output

## Examples

```bash
# Basic web search
xai web "xAI Grok latest updates"

# Search within specific domains
xai web "AI safety research" --domain arxiv.org --domain openai.com

# Search excluding certain domains
xai web "machine learning tutorial" --exclude-domain medium.com --format json
```
