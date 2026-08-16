# Web Searchによる生成回答

```bash
xai web "<query>" [--domain DOMAIN]... [--exclude-domain DOMAIN]... \
  [--format text|markdown|json] [--raw] [--no-stream]
```

GrokがWeb検索とページ閲覧を行い、引用付きの回答を生成します。検索結果の生リストは返しません。

- `--domain`と`--exclude-domain`は同時指定不可、それぞれ最大5件
- ドメインはscheme、port、pathを含まないホスト名
- `--raw`は`--format json`との組み合わせだけで使用

```bash
xai web "Python release changes"
xai web "API reference" --domain docs.python.org --domain peps.python.org
xai web "tutorial" --exclude-domain medium.com --format json
```
