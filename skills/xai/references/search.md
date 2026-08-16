# X Searchによる生成回答

```bash
xai search "<query>" [--from YYYY-MM-DD] [--to YYYY-MM-DD] \
  [--from-user HANDLE]... [--exclude HANDLE]... [--images] \
  [--format text|markdown|json] [--raw] [--no-stream]
```

GrokがX Searchを実行し、検索した投稿を根拠に引用付き回答を生成します。

- 日付は両端を含み、`--from`は`--to`以前
- `--from-user`と`--exclude`は同時指定不可、それぞれ最大20件
- ハンドルは`@`付き・なしのどちらも可
- `--images`は投稿画像の理解を有効化
- `--raw`は`--format json`との組み合わせだけで使用

```bash
xai search "xAI API updates" --from 2026-01-01
xai search "release" --from-user @xai --from-user @elonmusk --format json
```
