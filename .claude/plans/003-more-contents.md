# コンテンツの保全とより広い情報の取得

## 課題

* 更新するたびに古いイベント情報が削除される事がある。一旦収集したイベント情報は、会期が終了するまで削除しないで欲しい。
* 収集するサイトが少ないため情報に乏しい、東京に限らず日本全国のキネティックアート、サウンドアートを集めたい。


## 実装プラン

### 課題1: イベント保全（更新時に会期中イベントを消さない）

**原因**: `scripts/main.py` がスクレイピングのたびに `docs/data/exhibitions.json` / `.ics` を完全再生成するため、サイト側の一時的なデータ欠落やスクレイピング失敗により会期中のイベントが消える。

**実装方針**: スクレイピング後、出力前に既存 JSON を読み込んでマージする。

- **残す**: `end_date >= today` のイベント（会期中・未来）
- **削除**: `end_date < today` のイベント（会期終了済み）
- **更新**: 同一 `source_url` のイベントは新しいスクレイピング結果で上書き
- **追加**: 新規 `source_url` のイベントは追加

**変更ファイル**: `scripts/main.py`

追加する関数:
```python
def load_existing_exhibitions(json_path: Path) -> list[Exhibition]:
    """既存JSONからExhibitionリストを復元。ファイルがなければ空リストを返す。"""

def merge_exhibitions(existing: list[Exhibition], new: list[Exhibition], today: date) -> list[Exhibition]:
    """新旧イベントをマージ。source_url をキーに上書き/追加。会期終了済みは削除。"""
```

`main()` の修正: スクレイピング→マージ→フィルタ→出力 の順に変更。

**テスト追加**: `tests/test_main.py` に `merge_exhibitions()` のユニットテストを追加。
- 会期終了済みイベントが除外されること
- 同一URLのイベントが新しいデータで上書きされること
- 既存イベントで新規スクレイピングにないものが保持されること

---

### 課題2: 収集対象の拡充（日本全国）

**現状**: 東京の6施設のみ（TokyoArtBeat, 美術手帖, ICC, 21_21, 森美術館, MOT）。

**追加スクレイパー候補**:

| 優先度 | サイト | URL | 理由 |
|--------|--------|-----|------|
| 高 | **artscape** | artscape.jp/exhibition/ | 全国2,000施設、月2回更新 |
| 高 | **アートアジェンダ** | artagenda.jp | 全国321館の集約サイト |
| 中 | **金沢21世紀美術館** | kanazawa21.jp | インスタレーション・メディアアートの聖地 |
| 中 | **国立国際美術館** | nmao.go.jp | 大阪の国立美術館 |

**実装ステップ**:
1. `scripts/scrapers/artscape.py` 新規作成（BaseScraper継承）
2. `scripts/scrapers/artagenda.py` 新規作成
3. `scripts/scrapers/kanazawa21.py` 新規作成
4. `scripts/scrapers/nmao.py` 新規作成
5. `scripts/main.py` の `SCRAPERS` リストに追加
6. 各スクレイパーのユニットテストを追加（`responses` ライブラリでHTTPモック）

---

### 実装順序

- [x] `scripts/main.py` にマージロジックを追加 + テスト（課題1）
- [x] artscapeスクレイパー + テスト
- [x] アートアジェンダスクレイパー + テスト
- [x] 金沢21世紀美術館スクレイパー + テスト
- [x] 国立国際美術館スクレイパー + テスト

---

### 検証方法

```bash
uv run pytest --cov=scripts          # テスト実行
uv run python -m scripts.main        # ローカルスクレイピング実行
```

- 既存JSONにある会期中イベントが再スクレイプ後も残ることを確認
- 新規スクレイパーで取得件数が増加することを確認

