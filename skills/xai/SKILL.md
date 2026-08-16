---
name: xai
description: >
  xAIのX SearchとWeb Searchを使い、Xの投稿・ユーザー・スレッド・トレンドまたはWebについて
  引用付きの生成回答が必要なときに`xai` CLIを使う。X/Twitter検索、投稿の調査、ユーザーの発言、
  スレッドの解説、トレンド分析、xAI経由のWeb調査で使用する。変数XなどTwitter以外のXには使用しない。
---

# xai-cli

`xai`は、xAIのサーバー側検索ツールに情報を調査させ、引用付きの回答を生成するCLIです。投稿一覧、タイムライン、スレッド、トレンド、生のWeb検索結果を直接取得するAPIではありません。

## 前提

- `XAI_API_KEY`を環境変数に設定するか、`xai config init`で保存する
- 既定モデルは、X SearchとWeb Searchに対応する明示的な`grok-4.6`

APIキーはコマンド引数へ書かず、環境変数または非表示プロンプトを使います。

## 出力

- `--format text`: プレーンテキスト
- `--format markdown`: Markdown
- `--format json`: `schema_version`、`response_id`、`model`、`status`、`text`、`citations`を持つ安定スキーマ
- `--format json --raw`: 生のxAI Responses応答
- `--no-stream`: 完了後に出力。JSONは常に非ストリーム

結果はstdout、進捗・警告・診断はstderrです。回答本文の`[[N]](url)`とJSONの`citations`を引用として扱います。

## コマンド別リファレンス

- X検索: [references/search.md](references/search.md)
- ユーザーの投稿に関する調査: [references/user.md](references/user.md)
- スレッドに関する調査: [references/thread.md](references/thread.md)
- トレンド分析: [references/trending.md](references/trending.md)
- Web調査: [references/web.md](references/web.md)
- 設定とモデル: [references/config.md](references/config.md)

複合調査では、まず`search`または`user`で論点を探し、必要な投稿URLを`thread`で詳しく調べます。
