# Xトレンドの分析

```bash
xai trending [TOPIC] [--category tech|politics|sports|entertainment] \
  [--format text|markdown|json] [--raw] [--no-stream]
```

Grokが現在のXを検索し、重要なトレンドを引用付きで分析します。Xのトレンド一覧をそのまま返すコマンドではありません。

`TOPIC`と`--category`は同時に指定できません。

```bash
xai trending
xai trending "spaceflight"
xai trending --category tech --format json
```
