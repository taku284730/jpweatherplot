"""
jpweatherplot
=============

日本の中学校理科・気象通報教材向けの個人用 Matplotlib/MetPy 描画ライブラリ。

これは気象庁公式ライブラリではありません。
"""

from .weather import WEATHER_TYPES, WEATHER_ALIASES, add_weather_symbol, add_blank_station_circle, make_weather_glyph
from .wind import WIND_DIRECTION_DEG, add_wind_force_symbol, make_wind_force_glyph
from .station import add_station_model, add_station_model_geo

__version__ = "0.1.1"

__all__ = [
    "WEATHER_TYPES",
    "WEATHER_ALIASES",
    "WIND_DIRECTION_DEG",
    "add_weather_symbol",
    "add_blank_station_circle",
    "make_weather_glyph",
    "add_wind_force_symbol",
    "make_wind_force_glyph",
    "add_station_model",
    "add_station_model_geo",
]
