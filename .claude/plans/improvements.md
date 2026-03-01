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

### Phase 1: 重複排除
- [ ] `scripts/scrapers/tokyo_art_beat.py` に `seen_urls` 追加
- [ ] `scripts/scrapers/bijutsu_techo.py` に `seen_urls` 追加
- [ ] `scripts/main.py` にグローバル重複排除を追加（source_url ベース）

### Phase 2: フィルタリング改善
- [ ] `scripts/filters.py` の短いキーワードを改善
  - 「音」→「サウンド」「音響」に変更、または
  - 単語境界マッチングに変更

### Phase 3: データ品質改善
- [ ] Tokyo Art Beat の会場抽出パターン追加
- [ ] 画像URL取得の改善

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
