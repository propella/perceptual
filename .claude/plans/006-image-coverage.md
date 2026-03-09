# 006: 画像カバレッジ改善

## 背景

現在の画像表示率は約44%（18件中8件）。スクレイパーごとに画像取得の欠落・バグがあり、Web サイトで「No Image」が多数表示されている。

---

## 開発プラン

### 優先度1: artagenda.py — セレクタのバグ修正

- [x] `_parse_item` で `h3` から親要素を遡り `a.exhImg` を見つける処理を修正
- 現在: `h3.parent`（`div.exhDtl`）の前の兄弟を探しているが、`a.exhImg` は `article.artEvent` の直下にある
- 修正: `article.artEvent` まで遡って `a[href=href]` 内の `img` を取得
- [x] `tests/scrapers/test_artagenda.py` の既存テスト `test_scrape_extracts_image_url` が通ることを確認

### 優先度2: artscape.py — lazy-load の base64 スキップ

- [x] `_parse_article` と `_parse_item` の画像抽出で `src="data:image/png;base64,..."` を無視し、`data-src` を使うよう修正
- [x] `tests/scrapers/test_artscape.py` に base64 + `data-src` のテストケースを追加

### 優先度3: icc.py — CSS background-image と OGP フォールバック

- [x] `_parse_item`: `<img>` が見つからない場合、`[style*='background-image']` から URL を抽出するコードを追加
- [x] `_fetch_detail_image`: `img[src*='/uploads/assets/']` の前に `og:image` メタタグ取得を試みるよう修正
- [x] `tests/scrapers/test_icc.py` に background-image と og:image テストを追加

### 優先度4: nt.py — 詳細ページから画像取得

- [x] `_fetch_detail_image(page_url, page_name)` メソッドを追加
- 詳細ページの `<img>` から `plugin=ref` かつ `page=PAGE_NAME` を含む URL を取得
- [x] `_parse_li` から詳細ページ取得を呼び出す
- [x] `tests/scrapers/test_nt.py` に詳細ページモックを使ったテストを追加

### 優先度5: hakubutsu_fes.py — OGP 画像取得を追加

- [x] `_parse_page` に `og:image` メタタグ取得と、ドメイン一致 `<img>` のフォールバックを追加
- [x] `tests/scrapers/test_hakubutsu_fes.py` を新規作成

---

## 変更対象ファイル

| ファイル | 変更内容 |
|---------|---------|
| `scripts/scrapers/artagenda.py` | `_parse_item`: article コンテナ経由で `a[href] img` を取得 |
| `scripts/scrapers/artscape.py` | `_parse_article`/`_parse_item`: `data:` URI をスキップし `data-src` を使用 |
| `scripts/scrapers/icc.py` | `_parse_item`: CSS background-image 抽出追加。`_fetch_detail_image`: OGP フォールバック追加 |
| `scripts/scrapers/nt.py` | `_fetch_detail_image` 追加、`_parse_li` から呼び出し |
| `scripts/scrapers/hakubutsu_fes.py` | `_parse_page` に OGP 画像取得追加 |
| `tests/scrapers/test_artagenda.py` | 既存テストが通ることを確認（変更不要の可能性あり） |
| `tests/scrapers/test_artscape.py` | base64 + `data-src` テストケース追加 |
| `tests/scrapers/test_icc.py` | HTML フィクスチャを実ページ構造に更新 |
| `tests/scrapers/test_nt.py` | 詳細ページ画像取得テスト追加 |
| `tests/scrapers/test_hakubutsu_fes.py` | 新規作成 |

---

## 検証手順

1. `uv run pytest tests/scrapers/ -v` — 全スクレイパーテスト通過を確認
2. `uv run ruff check scripts tests` — lint エラーなし
3. `uv run python -m scripts.main` — 画像カバレッジが 44% → 70%+ に改善することを確認
4. 出力 JSON (`docs/data/exhibitions.json`) の artagenda, artscape, ICC エントリに `imageUrl` が存在することを確認
