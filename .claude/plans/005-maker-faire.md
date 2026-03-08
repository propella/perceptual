# Maker Faire 対応

## 課題

Maker Faire Tokyo、 NT 東京、「博物ふぇすてぃばる」など、国内のメイカー・ものづくりイベントを追加する。

## 実装プラン

### 対象サイト

| サイト | URL | 状態 |
|------|-----|------|
| Maker Faire / Make Japan | `https://makezine.jp/event/` | 稼働中（WordPress） |
| NT (ニコ技) | `https://wiki.nicotech.jp/nico_tech/` | 稼働中（PukiWiki） |
| 博物ふぇすてぃばる | 不明 | アクセス不可 → バックログに移動 |

### タスク

- [ ] `scripts/filters.py` にメイカー系キーワード追加（`"メイカー"`, `"maker"`, `"ものづくり"`, `"Maker Faire"`）
- [ ] `scripts/scrapers/maker_faire.py` を作成（`BaseScraper` 継承、`https://makezine.jp/event/` をスクレイプ）
- [ ] `scripts/scrapers/nt.py` を作成（`BaseScraper` 継承、`https://wiki.nicotech.jp/nico_tech/` をスクレイプ）
- [ ] `scripts/scrapers/__init__.py` と `scripts/main.py` にスクレイパー登録
- [ ] `tests/scrapers/test_maker_faire.py` を作成
- [ ] `tests/scrapers/test_nt.py` を作成
- [ ] `uv run pytest` 通過確認
- [ ] `uv run python -m scripts.main` で動作確認
- [ ] 博物ふぇすてぃばるを `999-backlog.md` に追記
- [ ] commit & push
