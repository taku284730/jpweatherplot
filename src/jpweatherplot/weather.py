from __future__ import annotations

import math

from matplotlib.lines import Line2D
from matplotlib.offsetbox import AnnotationBbox, DrawingArea
from matplotlib.patches import Arc, Circle, Polygon, Wedge
from matplotlib.text import Text


WEATHER_TYPES = (
    "快晴", "雨", "雪", "煙霧", "雷",
    "晴れ", "にわか雨", "にわか雪", "雷強し",
    "くもり", "雨強し", "雪強し", "ひょう",
    "霧", "霧雨", "みぞれ", "地ふぶき", "あられ", "不明",
)

WEATHER_ALIASES = {
    "晴": "晴れ",
    "曇": "くもり",
    "雲": "くもり",
    "地吹雪": "地ふぶき",
    "天気不明": "不明",
    "霙": "みぞれ",
}


def _line(da, x1, y1, x2, y2, lw=1.15):
    da.add_artist(
        Line2D(
            [x1, x2], [y1, y2],
            color="black", linewidth=lw, solid_capstyle="round"
        )
    )


def _circle(da, cx, cy, r, *, fill=False, lw=1.15):
    da.add_artist(
        Circle(
            (cx, cy), r,
            facecolor="black" if fill else "white",
            edgecolor="black", linewidth=lw
        )
    )


def _modifier(da, cx, cy, r, text, *, fontsize=8.6, x_offset=2.7, y_offset=-0.55):
    # ニ = にわか / ツ = 強し / キ = 霧雨
    da.add_artist(
        Text(
            x=cx + r + x_offset,
            y=cy + r * y_offset,
            text=text,
            fontsize=fontsize,
            ha="left", va="center",
            color="black",
        )
    )


def _snow_spokes(da, cx, cy, r, lw=1.05):
    for deg in (0, 60, 120):
        th = math.radians(deg)
        dx = r * 0.90 * math.cos(th)
        dy = r * 0.90 * math.sin(th)
        _line(da, cx-dx, cy-dy, cx+dx, cy+dy, lw)


def make_weather_glyph(
    weather: str,
    *,
    radius: float = 10.5,
    line_width: float = 1.15,
    padding: float = 12.0,
    modifier_fontsize: float = 8.6,
):
    """日本式の教材用天気記号を DrawingArea として返す。"""
    weather = WEATHER_ALIASES.get(weather, weather)
    if weather not in WEATHER_TYPES:
        raise ValueError(f"unsupported weather: {weather!r}")

    side = 2 * (radius + padding)
    cx = cy = side / 2
    r = radius
    da = DrawingArea(side, side, 0, 0)

    if weather == "快晴":
        _circle(da, cx, cy, r, lw=line_width)

    elif weather == "晴れ":
        _circle(da, cx, cy, r, lw=line_width)
        _line(da, cx, cy-r, cx, cy+r, line_width)

    elif weather == "くもり":
        _circle(da, cx, cy, r, lw=line_width)
        _circle(da, cx, cy, r*0.52, lw=line_width)

    elif weather == "雨":
        _circle(da, cx, cy, r, fill=True, lw=line_width)

    elif weather == "雪":
        _circle(da, cx, cy, r, lw=line_width)
        _snow_spokes(da, cx, cy, r, line_width)

    elif weather == "煙霧":
        _circle(da, cx, cy, r, lw=line_width)
        da.add_artist(Arc((cx-r*0.27, cy), r*0.78, r*0.55,
                          theta1=0, theta2=360, color="black", linewidth=line_width))
        da.add_artist(Arc((cx+r*0.27, cy), r*0.78, r*0.55,
                          theta1=0, theta2=360, color="black", linewidth=line_width))

    elif weather == "霧":
        _circle(da, cx, cy, r, lw=line_width)
        _circle(da, cx, cy, r*0.18, fill=True, lw=0.8)

    elif weather == "地ふぶき":
        _circle(da, cx, cy, r, lw=line_width)
        _line(da, cx-r*0.72, cy, cx+r*0.72, cy, line_width)
        _line(da, cx, cy-r*0.72, cx, cy+r*0.72, line_width)
        _line(da, cx+r*0.35, cy, cx+r*0.78, cy, line_width)
        _line(da, cx+r*0.78, cy, cx+r*0.58, cy+r*0.16, line_width)
        _line(da, cx+r*0.78, cy, cx+r*0.58, cy-r*0.16, line_width)

    elif weather == "にわか雨":
        _circle(da, cx, cy, r, fill=True, lw=line_width)
        _modifier(da, cx, cy, r, "ニ", fontsize=modifier_fontsize)

    elif weather == "雨強し":
        _circle(da, cx, cy, r, fill=True, lw=line_width)
        _modifier(da, cx, cy, r, "ツ", fontsize=modifier_fontsize)

    elif weather == "にわか雪":
        _circle(da, cx, cy, r, lw=line_width)
        _snow_spokes(da, cx, cy, r, line_width)
        _modifier(da, cx, cy, r, "ニ", fontsize=modifier_fontsize)

    elif weather == "雪強し":
        _circle(da, cx, cy, r, lw=line_width)
        _snow_spokes(da, cx, cy, r, line_width)
        _modifier(da, cx, cy, r, "ツ", fontsize=modifier_fontsize)

    elif weather == "霧雨":
        _circle(da, cx, cy, r, fill=True, lw=line_width)
        _modifier(da, cx, cy, r, "キ", fontsize=modifier_fontsize)

    elif weather == "みぞれ":
        _circle(da, cx, cy, r, lw=line_width)
        da.add_artist(Wedge((cx, cy), r*0.96, 180, 360,
                            facecolor="black", edgecolor="none"))
        for deg in (30, 90, 150):
            th = math.radians(deg)
            _line(
                da, cx, cy,
                cx+r*0.88*math.cos(th),
                cy+r*0.88*math.sin(th),
                line_width,
            )

    elif weather == "あられ":
        _circle(da, cx, cy, r, lw=line_width)
        pts = [(cx, cy+r*0.72), (cx-r*0.68, cy-r*0.48), (cx+r*0.68, cy-r*0.48)]
        da.add_artist(Polygon(pts, closed=True, facecolor="white",
                              edgecolor="black", linewidth=line_width))

    elif weather == "ひょう":
        _circle(da, cx, cy, r, lw=line_width)
        pts = [(cx, cy+r*0.72), (cx-r*0.68, cy-r*0.48), (cx+r*0.68, cy-r*0.48)]
        da.add_artist(Polygon(pts, closed=True, facecolor="black",
                              edgecolor="black", linewidth=line_width))

    elif weather == "雷":
        _circle(da, cx, cy, r, lw=line_width)
        da.add_artist(Wedge((cx, cy), r*0.96, 180, 360,
                            facecolor="black", edgecolor="none"))
        _line(da, cx-r, cy, cx+r, cy, line_width)

    elif weather == "雷強し":
        _circle(da, cx, cy, r, lw=line_width)
        da.add_artist(Wedge((cx, cy), r*0.96, 180, 360,
                            facecolor="black", edgecolor="none"))
        _line(da, cx-r, cy, cx+r, cy, line_width)
        _modifier(da, cx, cy, r, "ツ", fontsize=modifier_fontsize)

    elif weather == "不明":
        _circle(da, cx, cy, r, lw=line_width)
        q = r * 0.68
        _line(da, cx-q, cy-q, cx+q, cy+q, line_width)
        _line(da, cx-q, cy+q, cx+q, cy-q, line_width)

    return da


def add_weather_symbol(
    ax, x: float, y: float, weather: str,
    *, xycoords="data", zorder: int = 20, **glyph_kwargs
):
    """Axes 上の (x, y) に固定サイズの天気記号を置く。"""
    glyph = make_weather_glyph(weather, **glyph_kwargs)
    ab = AnnotationBbox(
        glyph, (x, y),
        xycoords=xycoords,
        frameon=False,
        box_alignment=(0.5, 0.5),
        pad=0.0,
        zorder=zorder,
    )
    ax.add_artist(ab)
    return ab
