# Maker Faire 対応

## 課題

Maker Faire Tokyo、 NT 東京、「博物ふぇすてぃばる」など、国内のメイカー・ものづくりイベントを追加する。

## 実装プラン

### 対象サイト

| サイト | URL | 状態 |
|------|-----|------|
| Maker Faire / Make Japan | `https://makezine.jp/event/` | 稼働中（WordPress） |
| NT (ニコ技) | `https://wiki.nicotech.jp/nico_tech/` | 稼働中（PukiWiki） |
| 博物ふぇすてぃばる | `https://www.hakubutufes.info/` | 稼働中（Jimdo、Cloudflare保護→Playwright必須） |

### タスク

- [x] `scripts/filters.py` にメイカー系キーワード追加（`"メイカー"`, `"maker"`, `"ものづくり"`, `"Maker Faire"`）
- [x] `scripts/scrapers/maker_faire.py` を作成（`BaseScraper` 継承、`https://makezine.jp/event/` をスクレイプ）
- [x] `scripts/scrapers/nt.py` を作成（`BaseScraper` 継承、`https://wiki.nicotech.jp/nico_tech/` をスクレイプ）
- [x] `scripts/scrapers/hakubutsu_fes.py` を作成（`PlaywrightBaseScraper` 継承、`https://www.hakubutufes.info/` をスクレイプ）
- [x] `scripts/scrapers/__init__.py` と `scripts/main.py` にスクレイパー登録
- [x] `tests/scrapers/test_maker_faire.py` を作成
- [x] `tests/scrapers/test_nt.py` を作成
- [x] `uv run pytest` 通過確認
- [x] `uv run python -m scripts.main` で動作確認
- [x] commit & push
