# Config

## Initialize configuration

```bash
xai config init
```

Sets up the configuration file with default settings. Prompts for API key if `XAI_API_KEY` is not set.

## Set configuration values

```bash
xai config set <key> <value>
```

Available keys: `api_key`, `default_model` (or `model`), `stream`, `format`, `enable_image_understanding`, `enable_video_understanding`.

## Get a configuration value

```bash
xai config get <key>
```

## List configuration

```bash
xai config list
```

Shows current configuration values.

## List available models

```bash
xai models
```

Lists all available xAI models.

## Environment variables

- `XAI_API_KEY` — xAI API key (required)
- `XAI_DEFAULT_MODEL` — override default model

## Config file location

Configuration is stored in `~/.config/xai/config.toml` (via platformdirs).
