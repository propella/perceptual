# perceptual 改善プラン

## 発見された問題

### 1. 重複問題（Critical）
- 「安野光雅展」が3回重複出力（bijutsu_techo から）
- `tokyo_art_beat` と `bijutsu_techo` に重複排除ロジックがない
- グローバルな重複排除もない

### 2. フィルタリング精度（High）
- 短いキーワード（音、光、影）が誤検出リスク高い
- 部分一致のため「音」→「音声学」「音楽」にもマッチ

### 3. データ品質（Medium）
- 会場情報なし: 30%（主に tokyo_art_beat）
- 画像URLなし: 70%
- 説明なし: 100%

## 改善タスク

### Phase 1: 重複排除 ✅
- [x] `scripts/scrapers/tokyo_art_beat.py` に `seen_urls` 追加
- [x] `scripts/scrapers/bijutsu_techo.py` に `seen_urls` 追加
- [x] `scripts/main.py` にグローバル重複排除を追加（source_url ベース）

### Phase 2: フィルタリング改善 ✅
- [x] `scripts/filters.py` の短いキーワードを検討
  - 短いキーワード（音、光、影、空間）は維持（誤検出許容）

### Phase 3: データ品質改善 ✅
- [x] Tokyo Art Beat の会場抽出パターン追加
  - `<h3>` 後の最初の `<p>` から会場名を抽出
  - フォールバックとして `@` / `会場：` パターンも維持
- [x] 画像URL取得の改善
  - プロトコル相対URL (`//images.ctfassets.net/...`) を `https:` 付きに変換
  - `data-src` 属性（lazy-loading）にも対応
  - bijutsu_techo の HTML フォールバックにも同様の改善を適用

### Phase 4: 画像URL取得の強化 ✅
- [x] Tokyo Art Beat: `__NEXT_DATA__` JSON から画像 URL を抽出
  - `imageposter.fields.file.url` パスで Contentful CDN URL を取得
  - slug でイベントカードとマッチング
- [x] ICC: 個別展覧会ページから画像を取得
  - 一覧ページに画像がないため、各展覧会の詳細ページを fetch
  - `/uploads/assets/` パターンの img タグから抽出

## 修正対象ファイル

- `scripts/scrapers/tokyo_art_beat.py`
- `scripts/scrapers/bijutsu_techo.py`
- `scripts/main.py`
- `scripts/filters.py`
- `tests/` 配下の対応テスト

## 検証方法

```bash
uv run pytest
uv run python -m scripts.main
# 重複がないことを確認
jq '.exhibitions | group_by(.id) | map(select(length > 1))' docs/data/exhibitions.json
```

## 備考

- MOT（東京都現代美術館）はJavaScript動的読込みのため未対応
- DORA ベストプラクティスに従いテスト追加必須
