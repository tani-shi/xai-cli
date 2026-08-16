# スレッドに関する生成回答

```bash
xai thread https://x.com/HANDLE/status/ID [--summary] \
  [--format text|markdown|json] [--raw] [--no-stream]
```

X Searchのスレッド取得機能を使い、指定投稿の会話について引用付きの解説を生成します。`--summary`は要点中心の回答を依頼します。

URLは`https`のXまたはTwitter status URLである必要があります。
