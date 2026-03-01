# 展覧会情報自動収集システム設計

## 概要

以下の作家名に代表されるような芸術作の展覧会イベントなどを自動取得して GitHub Pages で Web サイトおよび ICS として公開する。

- テオ・ヤンセン
- ジャン・ティンゲリー
- 藤本由紀夫
- 野村仁
- 鈴木昭男
- カワクボリョウタ

## 対象ジャンル（フィルタリングキーワード）

挙げられた作家から推定されるジャンル：
- キネティックアート（テオ・ヤンセン、ジャン・ティンゲリー）
- サウンドアート（藤本由紀夫、鈴木昭男）
- メディアアート / インスタレーション（野村仁、カワクボリョウタ）
- インタラクティブアート、テクノロジーアート

## 技術構成

| コンポーネント | 技術 |
|---------------|------|
| スクレイピング | Python + requests + BeautifulSoup4 |
| ICS生成 | ics ライブラリ |
| 定期実行 | GitHub Actions (cron) |
| ホスティング | GitHub Pages |
| フロントエンド | 静的HTML + Vanilla JS |

## ディレクトリ構造

```
/
├── .github/
│   └── workflows/
│       └── update-exhibitions.yml    # 毎日実行
├── scripts/
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base.py                   # 基底クラス
│   │   ├── tokyo_art_beat.py
│   │   ├── bijutsu_techo.py
│   │   ├── icc.py
│   │   ├── design_sight.py           # 21_21
│   │   ├── mori_art_museum.py
│   │   └── mot.py                    # 東京都現代美術館
│   ├── filters.py                    # ジャンルフィルタリング
│   ├── generator.py                  # JSON/ICS生成
│   ├── main.py
│   └── requirements.txt
├── docs/                             # GitHub Pages公開ディレクトリ
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── data/
│       ├── exhibitions.json
│       └── exhibitions.ics
└── README.md
```

## データスキーマ

### exhibitions.json
```json
{
  "lastUpdated": "2026-03-01T12:00:00Z",
  "exhibitions": [
    {
      "id": "sha256-hash-of-title-venue",
      "title": "展覧会タイトル",
      "description": "概要テキスト",
      "venue": "会場名",
      "address": "住所",
      "startDate": "2026-03-01",
      "endDate": "2026-05-31",
      "imageUrl": "https://example.com/image.jpg",
      "sourceUrl": "https://example.com/exhibition",
      "source": "tokyo_art_beat",
      "tags": ["キネティックアート", "メディアアート"],
      "ogp": {
        "title": "OGPタイトル",
        "description": "OGP説明",
        "image": "OGP画像URL"
      }
    }
  ]
}
```

### exhibitions.ics (Google Calendar用)
```
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Art Exhibitions//EN
BEGIN:VEVENT
DTSTART:20260301
DTEND:20260531
SUMMARY:展覧会タイトル
DESCRIPTION:概要\n会場: 会場名
LOCATION:住所
URL:https://example.com/exhibition
END:VEVENT
END:VCALENDAR
```

## スクレイピング対象サイト

| サイト | URL | 備考 |
|-------|-----|------|
| Tokyo Art Beat | tokyoartbeat.com | 展覧会検索ページをスクレイピング |
| 美術手帖 | bijutsutecho.com | イベントページ |
| ICC | icc.or.jp | メディアアート専門 |
| 21_21 DESIGN SIGHT | 2121designsight.jp | デザイン/アート |
| 森美術館 | mori.art.museum | 現代アート |
| 東京都現代美術館 | mot-art-museum.jp | 現代アート |

## フィルタリングロジック

```python
FILTER_KEYWORDS = [
    # ジャンル
    "キネティック", "kinetic", "サウンドアート", "sound art",
    "メディアアート", "media art", "インスタレーション", "installation",
    "インタラクティブ", "interactive", "テクノロジー", "technology",

    # 関連作家名
    "テオ・ヤンセン", "Theo Jansen", "ジャン・ティンゲリー", "Tinguely",
    "藤本由紀夫", "野村仁", "鈴木昭男", "カワクボリョウタ", "rhizomatiks",

    # 関連キーワード
    "機械", "動く", "音", "光", "影", "空間"
]
```

## GitHub Actions ワークフロー

```yaml
name: Update Exhibitions

on:
  schedule:
    - cron: '0 9 * * *'  # 毎日18:00 JST
  workflow_dispatch:      # 手動実行可能

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r scripts/requirements.txt
      - run: python scripts/main.py
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

## フロントエンド仕様

### index.html
- レスポンシブデザイン
- 展覧会カード表示（画像、タイトル、会期、会場）
- タグフィルター機能
- 日付ソート
- Google Calendar購読リンク

### 主要機能
1. **カード表示**: 各展覧会を画像付きカードで表示
2. **フィルター**: ジャンルタグでフィルタリング
3. **ソート**: 開始日/終了日でソート
4. **カレンダー連携**: ICSファイルのダウンロード/購読URL

## 実装手順

### Phase 1: 基盤構築
1. [ ] プロジェクト構造の作成
2. [ ] requirements.txt (requests, beautifulsoup4, ics, lxml)
3. [ ] 基底スクレイパークラス (base.py)
4. [ ] フィルタリングモジュール (filters.py)

### Phase 2: スクレイパー実装
5. [ ] Tokyo Art Beat スクレイパー
6. [ ] 美術手帖スクレイパー
7. [ ] ICC スクレイパー
8. [ ] 21_21 DESIGN SIGHT スクレイパー
9. [ ] 森美術館スクレイパー
10. [ ] 東京都現代美術館スクレイパー

### Phase 3: 出力生成
11. [ ] JSON生成 (generator.py)
12. [ ] ICS生成 (generator.py)
13. [ ] メインスクリプト (main.py)

### Phase 4: フロントエンド
14. [ ] index.html
15. [ ] style.css
16. [ ] app.js

### Phase 5: CI/CD
17. [ ] GitHub Actions ワークフロー
18. [ ] GitHub Pages設定

## 検証方法

1. **ローカルテスト**:
   ```bash
   cd scripts
   pip install -r requirements.txt
   python main.py
   # docs/data/exhibitions.json と exhibitions.ics を確認
   ```

2. **フロントエンド確認**:
   ```bash
   cd docs
   python -m http.server 8000
   # http://localhost:8000 で表示確認
   ```

3. **GitHub Actions**:
   - Push後、Actionsタブでワークフロー実行を確認
   - GitHub Pagesの公開URLでサイト確認

## 注意事項

- スクレイピングは各サイトの利用規約を確認
- 過度なリクエストを避けるため1日1回の更新に制限
- 画像は直接リンク（キャッシュはしない）
- robots.txtを尊重
