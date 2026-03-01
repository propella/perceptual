# perceptual

展覧会情報自動収集: https://propella.github.io/perceptual/

## セットアップ

```bash
uv sync --dev
```

## 実行

```bash
uv run python -m scripts.main
```

出力ファイル:
- `docs/data/exhibitions.json`
- `docs/data/exhibitions.ics`

## テスト

```bash
uv run pytest
```

カバレッジ付き:

```bash
uv run pytest --cov=scripts
```

## リンター

```bash
uv run ruff check scripts tests
```

## フロントエンド確認

```bash
uv run python -m http.server 8000 -d docs
# http://localhost:8000 で表示確認
```

## CI/CD

- PR 作成時: CI が自動でテスト実行
- main マージ: 自動デプロイ (GitHub Pages)
- 毎日 18:00 JST にスクレイピング自動実行
