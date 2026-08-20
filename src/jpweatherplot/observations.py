from __future__ import annotations

from dataclasses import dataclass

from .stations import Station


@dataclass(frozen=True, slots=True)
class Observation:
    """
    1地点・1時刻の気象通報観測値。

    Parameters
    ----------
    station:
        観測地点。
    weather:
        天気。例: "晴れ", "くもり", "雨"
    wind_direction:
        16方位。例: "北北東"
    wind_force:
        気象庁風力階級 0〜12。
    pressure:
        海面気圧 [hPa]。
    temperature:
        気温 [degC]。
    """
    station: Station
    weather: str
    wind_direction: str
    wind_force: int
    pressure: float
    temperature: float

    @property
    def name(self) -> str:
        return self.station.name

    @property
    def lat(self) -> float:
        return self.station.lat

    @property
    def lon(self) -> float:
        return self.station.lon