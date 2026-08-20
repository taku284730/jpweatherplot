from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Station:
    """気象通報で使用する観測地点の基本情報。"""
    name: str
    lat: float
    lon: float
    region: str
    aliases: tuple[str, ...] = ()


_STATION_LIST = [
    Station("石垣島", 24.34, 124.16, "沖縄・奄美"),
    Station("那覇", 26.21, 127.68, "沖縄・奄美"),
    Station("南大東島", 25.83, 131.23, "沖縄・奄美"),
    Station("名瀬", 28.38, 129.49, "沖縄・奄美"),
    Station("鹿児島", 31.56, 130.56, "九州"),
    Station("福江", 32.69, 128.84, "九州"),
    Station("厳原", 34.20, 129.29, "九州"),
    Station("足摺岬", 32.72, 133.01, "四国"),
    Station("室戸岬", 33.25, 134.18, "四国"),
    Station("松山", 33.84, 132.77, "四国"),
    Station("浜田", 34.90, 132.08, "中国"),
    Station("西郷", 36.20, 133.33, "中国"),
    Station("大阪", 34.68, 135.52, "近畿"),
    Station("潮岬", 33.45, 135.76, "近畿"),
    Station("八丈島", 33.11, 139.79, "関東・東海"),
    Station("大島", 34.75, 139.36, "関東・東海"),
    Station("御前崎", 34.60, 138.22, "関東・東海"),
    Station("銚子", 35.73, 140.86, "関東・東海"),
    Station("前橋", 36.39, 139.06, "関東・東海"),
    Station("小名浜", 36.95, 140.90, "東北・北陸"),
    Station("輪島", 37.39, 136.90, "東北・北陸"),
    Station("相川", 38.03, 138.24, "東北・北陸"),
    Station("仙台", 38.26, 140.90, "東北・北陸"),
    Station("宮古", 39.64, 141.95, "東北・北陸"),
    Station("秋田", 39.72, 140.10, "東北・北陸"),
    Station("函館", 41.77, 140.73, "北海道"),
    Station("浦河", 42.16, 142.78, "北海道"),
    Station("根室", 43.33, 145.58, "北海道"),
    Station("稚内", 45.42, 141.68, "北海道"),
]

STATIONS: dict[str, Station] = {s.name: s for s in _STATION_LIST}

_ALIASES: dict[str, str] = {}
for s in _STATION_LIST:
    for alias in s.aliases:
        _ALIASES[alias] = s.name


def get_station(name: str) -> Station:
    canonical = _ALIASES.get(name, name)
    try:
        return STATIONS[canonical]
    except KeyError as exc:
        raise KeyError(f"未登録の観測地点です: {name}") from exc


def list_stations(*, region: str | None = None) -> list[Station]:
    if region is None:
        return list(_STATION_LIST)
    return [s for s in _STATION_LIST if s.region == region]


def station_names(*, region: str | None = None) -> list[str]:
    return [s.name for s in list_stations(region=region)]


def regions() -> list[str]:
    result = []
    for s in _STATION_LIST:
        if s.region not in result:
            result.append(s.region)
    return result


def find_stations(text: str) -> list[Station]:
    text = text.strip()
    if not text:
        return []
    hits = []
    for s in _STATION_LIST:
        names = (s.name, *s.aliases)
        if any(text in name for name in names):
            hits.append(s)
    return hits
