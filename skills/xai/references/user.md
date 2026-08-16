# ユーザーの投稿に関する生成回答

```bash
xai user @HANDLE [QUESTION] [--from YYYY-MM-DD] [--to YYYY-MM-DD] \
  [--format text|markdown|json] [--raw] [--no-stream]
```

指定ユーザーだけを対象にX Searchを実行し、最近の投稿の要約または質問への引用付き回答を生成します。タイムラインの生データは返しません。

```bash
xai user @xai
xai user @xai "Which API changes were announced?" --from 2026-01-01
```
