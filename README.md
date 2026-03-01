# perceptual

展覧会情報自動収集システム

## セットアップ

```bash
uv sync --dev
```

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
