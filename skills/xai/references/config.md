# 設定

```bash
xai config init
xai config set api_key
xai config set default_model grok-4.6
xai config set stream false
xai config set format markdown
xai config get default_model
xai config list
xai config path
xai models
xai models --format json
```

APIキーは`config init`または`config set api_key`の非表示プロンプトで入力します。`config get api_key`と`config list`は設定の有無だけを表示します。

設定キーは`api_key`、`default_model`（`model`も可）、`stream`、`format`、`enable_image_understanding`、`enable_video_understanding`です。`format`は`text`、`markdown`、`json`のいずれかです。

優先順位はコマンドオプション、`XAI_API_KEY` / `XAI_DEFAULT_MODEL`、設定ファイル、組み込み既定値の順です。設定場所はOSごとに異なるため、`xai config path`で確認します。
