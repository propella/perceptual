from scripts.scrapers.base import Exhibition

FILTER_KEYWORDS = [
    # ジャンル
    "キネティック",
    "kinetic",
    "サウンドアート",
    "sound art",
    "メディアアート",
    "media art",
    "インスタレーション",
    "installation",
    "インタラクティブ",
    "interactive",
    "テクノロジー",
    "technology",
    # 関連作家名
    "テオ・ヤンセン",
    "Theo Jansen",
    "ジャン・ティンゲリー",
    "Tinguely",
    "藤本由紀夫",
    "野村仁",
    "鈴木昭男",
    "カワクボリョウタ",
    "rhizomatiks",
    # 関連キーワード
    "機械",
    "動く彫刻",
    "サウンド",
    "音響",
    "光と影",
    "ライトアート",
    "light art",
    "空間芸術",
]


def matches_filter(exhibition: Exhibition) -> bool:
    """Check if exhibition matches any filter keyword."""
    text = " ".join(
        [
            exhibition.title,
            exhibition.description or "",
            " ".join(exhibition.tags or []),
        ]
    ).lower()

    for keyword in FILTER_KEYWORDS:
        if keyword.lower() in text:
            return True
    return False


def filter_exhibitions(exhibitions: list[Exhibition]) -> list[Exhibition]:
    """Filter exhibitions by keywords."""
    return [e for e in exhibitions if matches_filter(e)]
