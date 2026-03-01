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
