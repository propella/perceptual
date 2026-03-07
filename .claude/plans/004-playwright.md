# Playwright 対応

## 課題

`artscape`・`mot`（東京都現代美術館）・`tokyo_art_beat` の3スクレイパーが 0 件を返している。
原因は JavaScript による動的レンダリングで、`requests` + BeautifulSoup の静的 HTML 取得では
展覧会リストが存在しない。

| スクレイパー | 現状 | 原因 |
|------------|------|------|
| `artscape` | 0件 | JS レンダリング（WordPress + React） |
| `mot` | 0件 | JS レンダリング |
| `tokyo_art_beat` | 0件 | Next.js（`__NEXT_DATA__` 抽出の不具合の可能性） |

## 実装プラン

### 方針

`BaseScraper` を継承した `PlaywrightBaseScraper` を新設し、`fetch_js(url)` メソッドを追加する。
JS レンダリングが必要なスクレイパーはこのクラスを継承し、`self.fetch()` の代わりに
`self.fetch_js()` を呼ぶ。既存の `requests` ベーススクレイパーは変更不要。

```
BaseScraper (requests ベース)
└── PlaywrightBaseScraper (Playwright ベース)
    ├── MOTScraper        （既存クラスを更新）
    └── ArtscapeScraper   （既存クラスを更新）
```

`tokyo_art_beat` は `__NEXT_DATA__` 抽出の調査・修正で対応を試みる（Playwright 不要な可能性）。

### 懸念点

| 懸念 | 詳細 | 対策 |
|------|------|------|
| **CI/CD 実行時間の増大** | Chromium インストール（~200MB）＋ ブラウザ起動・networkidle 待機で 1 スクレイパーあたり 30〜60 秒増加 | deploy.yml のみに追加（ci.yml のテストはモックで高速に保つ） |
| **GitHub Actions メモリ使用量** | ヘッドレス Chromium はメモリ消費が大きい（~300MB） | `ubuntu-latest` の 7GB RAM で問題なし。同時実行はしない |
| **Anti-bot 対策** | サイトがヘッドレスブラウザを検出してブロックする可能性 | User-Agent を設定済み。必要に応じて `stealth` 対応を検討 |
| **networkidle タイムアウト** | SPA でネットワークがアイドルにならないケースがある | `wait_for_load_state("networkidle")` + 30 秒タイムアウト。失敗時は `domcontentloaded` にフォールバック |
| **Playwright 依存の複雑さ** | Linux では `--with-deps` で OS 依存ライブラリが必要 | `uv run playwright install chromium --with-deps` で解決 |
| **テストの実行速度** | 実際の Playwright を使うとテストが遅い | すべてのテストは `mock.patch` でモック化し、ユニットテストは高速に保つ |

### テスト方法

`responses` ライブラリは HTTP レベルのモックのため Playwright では使えない。
`unittest.mock.patch` で `fetch_js()` を差し替える：

```python
from unittest.mock import patch

def mock_fetch_js(self, url):
    return BeautifulSoup(SAMPLE_HTML, "lxml")

class TestMOTScraper:
    def test_scrape(self):
        with patch.object(MOTScraper, "fetch_js", mock_fetch_js):
            exhibitions = MOTScraper().scrape()
            assert len(exhibitions) > 0
```

### deploy.yml への追加

```yaml
- name: Install Playwright browsers
  run: uv run playwright install chromium --with-deps
```

## 実装順序

- [ ] `pyproject.toml` に `playwright>=1.50` を追加
- [ ] `scripts/scrapers/base_playwright.py` を新規作成（`PlaywrightBaseScraper`）
- [ ] `scripts/scrapers/__init__.py` に `PlaywrightBaseScraper` を追加
- [ ] `scripts/scrapers/mot.py` を `PlaywrightBaseScraper` 継承に更新
- [ ] `tests/scrapers/test_mot.py` を Playwright モック対応に更新
- [ ] `scripts/scrapers/artscape.py` を `PlaywrightBaseScraper` 継承に更新
- [ ] `tests/scrapers/test_artscape.py` を Playwright モック対応に更新
- [ ] `scripts/scrapers/tokyo_art_beat.py` の `__NEXT_DATA__` 抽出を調査・修正
- [ ] `.github/workflows/deploy.yml` に Playwright ブラウザインストールステップを追加

## 変更対象ファイル

- `pyproject.toml`
- `scripts/scrapers/base_playwright.py` （新規）
- `scripts/scrapers/__init__.py`
- `scripts/scrapers/mot.py`
- `scripts/scrapers/artscape.py`
- `scripts/scrapers/tokyo_art_beat.py`
- `tests/scrapers/test_mot.py`
- `tests/scrapers/test_artscape.py`
- `.github/workflows/deploy.yml`

## 検証方法

```bash
# Playwright ブラウザを一度インストール（初回のみ）
uv run playwright install chromium

# テスト実行
uv run pytest --cov=scripts

# 実際のスクレイピングで件数確認
uv run python -m scripts.main
```

- artscape, MOT が 0 件から 1 件以上に増えることを確認
- 全テスト通過を確認
