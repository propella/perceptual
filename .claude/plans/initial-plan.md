# 展覧会情報自動収集システム設計

## 対象ジャンル（フィルタリングキーワード）

挙げられた作家から推定されるジャンル：
- キネティックアート（テオ・ヤンセン、ジャン・ティンゲリー）
- サウンドアート（藤本由紀夫、鈴木昭男）
- メディアアート / インスタレーション（野村仁、カワクボリョウタ）
- インタラクティブアート、テクノロジーアート

## 開発方針 (DORA ベストプラクティス)

[DORA](https://dora.dev/) の推奨するプラクティスに従い、以下を重視する：

### 5つのメトリクス
| メトリクス | 目標 | 実現方法 |
|-----------|------|----------|
| デプロイ頻度 | 高 | main マージで自動デプロイ |
| 変更リードタイム | 短 | 小さな PR、自動テスト |
| 変更失敗率 | 低 | テスト自動化、CI 必須化 |
| 復旧時間 | 短 | ロールバック可能な設計 |
| 再作業率 | 低 | コードレビュー、テストカバレッジ |

### 採用するプラクティス
- **トランクベース開発**: 短命ブランチ、小さな PR
- **継続的インテグレーション**: PR ごとにテスト自動実行
- **継続的デリバリー**: main マージで GitHub Pages に自動デプロイ
- **テスト自動化**: pytest によるユニットテスト
- **監視/可観測性**: スクレイピング成功率のログ出力

## 技術構成

| コンポーネント | 技術 |
|---------------|------|
| パッケージ管理 | uv |
| スクレイピング | Python + requests + BeautifulSoup4 |
| ICS生成 | ics ライブラリ |
| テスト | pytest + responses (モック) |
| CI/CD | GitHub Actions |
| ホスティング | GitHub Pages |
| フロントエンド | 静的HTML + Vanilla JS |

## ディレクトリ構造

```
/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # PR時にテスト実行
│       └── deploy.yml                # main マージで自動デプロイ
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
│   └── main.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py                   # pytest fixtures
│   ├── test_filters.py
│   ├── test_generator.py
│   └── scrapers/
│       ├── __init__.py
│       └── test_base.py
├── docs/                             # GitHub Pages公開ディレクトリ
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── data/
│       ├── exhibitions.json
│       └── exhibitions.ics
├── pyproject.toml                    # プロジェクト設定・依存管理
├── uv.lock                           # ロックファイル
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

### ci.yml (PR時のテスト)
```yaml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --dev
      - run: uv run pytest --cov=scripts --cov-report=term-missing
      - run: uv run ruff check scripts tests
```

### deploy.yml (自動デプロイ)
```yaml
name: Deploy

on:
  schedule:
    - cron: '0 9 * * *'  # 毎日18:00 JST
  workflow_dispatch:      # 手動実行可能
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync
      - run: uv run python scripts/main.py
      - name: Log scraping results
        run: |
          echo "::notice::Exhibitions found: $(jq '.exhibitions | length' docs/data/exhibitions.json)"
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

### Phase 1: プロジェクト基盤
1. [ ] プロジェクト構造の作成
2. [ ] pyproject.toml (uv init)
3. [ ] pytest 設定 (conftest.py)
4. [ ] CI ワークフロー (ci.yml)

### Phase 2: コアモジュール + テスト
5. [ ] 基底スクレイパークラス (base.py) + テスト
6. [ ] フィルタリングモジュール (filters.py) + テスト
7. [ ] JSON/ICS生成 (generator.py) + テスト

### Phase 3: スクレイパー実装 + テスト
8. [ ] Tokyo Art Beat スクレイパー + テスト
9. [ ] 美術手帖スクレイパー + テスト
10. [ ] ICC スクレイパー + テスト
11. [ ] 21_21 DESIGN SIGHT スクレイパー + テスト
12. [ ] 森美術館スクレイパー + テスト
13. [ ] 東京都現代美術館スクレイパー + テスト

### Phase 4: 統合
14. [ ] メインスクリプト (main.py)
15. [ ] デプロイワークフロー (deploy.yml)

### Phase 5: フロントエンド
16. [ ] index.html
17. [ ] style.css
18. [ ] app.js

### Phase 6: 本番稼働
19. [ ] GitHub Pages 設定
20. [ ] 動作確認・監視設定

## 検証方法

1. **セットアップ**:
   ```bash
   uv sync --dev
   ```

2. **ユニットテスト**:
   ```bash
   uv run pytest --cov=scripts
   ```

3. **リンター**:
   ```bash
   uv run ruff check scripts tests
   ```

4. **ローカル実行**:
   ```bash
   uv run python scripts/main.py
   # docs/data/exhibitions.json と exhibitions.ics を確認
   ```

5. **フロントエンド確認**:
   ```bash
   uv run python -m http.server 8000 -d docs
   # http://localhost:8000 で表示確認
   ```

6. **CI/CD**:
   - PR 作成時: CI が自動でテスト実行
   - main マージ: 自動デプロイ
   - Actions タブでログ確認

## 注意事項

- スクレイピングは各サイトの利用規約を確認
- 過度なリクエストを避けるため1日1回の更新に制限
- 画像は直接リンク（キャッシュはしない）
- robots.txtを尊重
