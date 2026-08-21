from __future__ import annotations

import re
from pathlib import Path

from .observations import Observation
from .stations import get_station, station_names


ZENKAKU_DIGITS = str.maketrans(
    "０１２３４５６７８９",
    "0123456789",
)


def _z2h(text: str) -> str:
    """全角数字を半角数字へ変換する。"""
    return text.translate(ZENKAKU_DIGITS)


def _station_pattern(name: str) -> str:
    """
    気象通報原稿の地点名に含まれる空白へ対応する。

    例:
        石垣島
        ↓
        石\\s*垣\\s*島
    """
    return r"\s*".join(map(re.escape, name))


def _decode_pressure(value: str) -> int:
    """
    気象通報の省略気圧を通常のhPaへ戻す。

    例:
        "０４" -> 1004
        "１３" -> 1013
        "９９７" -> 997
    """
    pressure = int(_z2h(value))

    if pressure < 100:
        pressure += 1000

    return pressure


def parse_tsuhou_text(text: str) -> list[Observation]:
    """
    漁業気象通報放送原稿から国内観測地点を読み取る。

    Parameters
    ----------
    text:
        気象庁の漁業気象通報テキスト全文。

    Returns
    -------
    list[Observation]
        登録済み国内観測地点の観測値。

    Notes
    -----
    現在は通常形式と、
    「風向・風力不明 天気不明 気圧不明 気温不明」
    の欠測形式に対応する。
    """
    observations: list[Observation] = []

    for name in station_names():
        name_pat = _station_pattern(name)

        # 通常の観測行
        normal_pattern = (
            name_pat
            + r"\s+([^\s]+)"
            + r"\s+風力\s+([０-９0-9]+)"
            + r"\s+([^\s]+)"
            + r"\s+([０-９0-9]+)ｈＰａ"
            + r"\s+([０-９0-9]+)度"
        )

        match = re.search(normal_pattern, text)

        if match:
            (
                wind_direction,
                wind_force,
                weather,
                pressure,
                temperature,
            ) = match.groups()

            observations.append(
                Observation(
                    station=get_station(name),
                    weather=weather,
                    wind_direction=wind_direction,
                    wind_force=int(_z2h(wind_force)),
                    pressure=_decode_pressure(pressure),
                    temperature=int(_z2h(temperature)),
                )
            )
            continue

        # 全項目不明
        unknown_pattern = (
            name_pat
            + r"\s+風向・風力\s+不明"
            + r"\s+天気不明"
            + r"\s+気圧不明"
            + r"\s+気温不明"
        )

        if re.search(unknown_pattern, text):
            observations.append(
                Observation(
                    station=get_station(name),
                    weather="天気不明",
                    wind_direction=None,
                    wind_force=None,
                    pressure=None,
                    temperature=None,
                )
            )
            continue

    return observations


def load_tsuhou(
    path: str | Path,
    *,
    encoding: str = "shift_jis",
) -> list[Observation]:
    """
    気象庁の漁業気象通報テキストファイルを読み込む。

    Examples
    --------
    >>> observations = load_tsuhou("data/day6_12.txt")
    >>> len(observations)
    29
    """
    path = Path(path)

    text = path.read_text(encoding=encoding)

    return parse_tsuhou_text(text)

from urllib.request import urlopen


def load_tsuhou_url(
    url: str,
    *,
    encoding: str = "shift_jis",
) -> list[Observation]:
    """
    気象庁の漁業気象通報テキストをURLから直接読み込む。
    """
    with urlopen(url) as response:
        data = response.read()

    text = data.decode(encoding)

    return parse_tsuhou_text(text)

import re
from urllib.request import urlopen

TSUHOU_BASE_URL = "https://www.data.jma.go.jp/yoho/gyogyou"


def list_tsuhou_available() -> list[tuple[str, str]]:
    """
    気象庁で公開されている過去1週間分の12時気象通報を取得する。

    Returns
    -------
    list[tuple[str, str]]
        (表示用日付, URL) のリスト。

    例
    ---
    [
        ("2026年8月15日 12時", "https://.../day6_12.txt"),
        ...
    ]
    """
    result = []

    for day in range(7):
        url = f"{TSUHOU_BASE_URL}/day{day}_12.txt"

        try:
            with urlopen(url) as response:
                data = response.read()

            text = data.decode("shift_jis")

            # 1行目:
            # 漁業気象通報放送原稿  その１  ２０２６年８月１５日正午
            first_line = text.splitlines()[0]

            m = re.search(
                r"([０-９]{4})年([０-９]{1,2})月([０-９]{1,2})日正午",
                first_line,
            )

            if not m:
                continue

            year, month, day_num = (
                int(_z2h(x)) for x in m.groups()
            )

            label = f"{year}年{month}月{day_num}日 12時"

            result.append((label, url))

        except Exception:
            continue

    # 新しい日付順
    result.reverse()

    return result