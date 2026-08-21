from __future__ import annotations

import math

from matplotlib.lines import Line2D
from matplotlib.offsetbox import AnnotationBbox, DrawingArea
from matplotlib.patches import Circle


WIND_DIRECTION_DEG = {
    "北": 0.0, "北北東": 22.5, "北東": 45.0, "東北東": 67.5,
    "東": 90.0, "東南東": 112.5, "南東": 135.0, "南南東": 157.5,
    "南": 180.0, "南南西": 202.5, "南西": 225.0, "西南西": 247.5,
    "西": 270.0, "西北西": 292.5, "北西": 315.0, "北北西": 337.5,
}


def _rot(x: float, y: float, deg: float) -> tuple[float, float]:
    rad = math.radians(-deg)
    c, s = math.cos(rad), math.sin(rad)
    return x * c - y * s, x * s + y * c


def make_wind_force_glyph(
    force: int,
    direction_deg: float = 0.0,
    *,
    circle_radius: float = 4.4,
    shaft_length = 24.0,
    feather_spacing = 2.8,
    feather_length = 5.0,
    first_feather_length = 7.2,
    feather_angle_deg: float = 20.0,
    force1_tip_extension: float = 5.7,
    normal_tip_extension: float = 0.8,
    line_width: float = 0.85,
    padding: float = 18.0,
    show_circle: bool = True,
):
    """
    日本の中学校理科で用いる風向・風力記号を DrawingArea として返す。

    ・主軸は円周から開始
    ・先端側1本目の矢羽だけ長い
    ・矢羽はすべて平行
    ・風力1のみ主軸の突き抜けを明瞭にする
    """
    force = int(force)
    if not 0 <= force <= 12:
        raise ValueError("force must be 0..12")

    side = 2 * (shaft_length + padding)
    cx = cy = side / 2
    da = DrawingArea(side, side, 0, 0)

    if show_circle:
        da.add_artist(
            Circle(
                (cx, cy), circle_radius,
                facecolor="white", edgecolor="black",
                linewidth=line_width
            )
        )

    if force == 0:
        return da

    sx0, sy0 = _rot(0.0, circle_radius, direction_deg)
    sx1, sy1 = _rot(0.0, shaft_length, direction_deg)
    da.add_artist(
        Line2D(
            [cx + sx0, cx + sx1],
            [cy + sy0, cy + sy1],
            color="black",
            linewidth=line_width,
            solid_capstyle="round",
        )
    )

    right_count = min(force, 6)
    left_count = max(0, force - 6)

    angle = math.radians(feather_angle_deg)
    ux, uy = math.cos(angle), math.sin(angle)

    def add_feathers(count: int, side_sign: int, *, primary_side: bool):
        if count <= 0:
            return

        if force == 1 and primary_side:
            first_base_y = shaft_length - force1_tip_extension
        else:
            first_base_y = shaft_length - normal_tip_extension

        for i in range(count):
            base_y = first_base_y - i * feather_spacing
            length = first_feather_length if i == 0 else feather_length

            fx = side_sign * length * ux
            fy = length * uy

            bx, by = _rot(0.0, base_y, direction_deg)
            ex, ey = _rot(fx, base_y + fy, direction_deg)

            da.add_artist(
                Line2D(
                    [cx + bx, cx + ex],
                    [cy + by, cy + ey],
                    color="black",
                    linewidth=line_width,
                    solid_capstyle="round",
                )
            )

    add_feathers(right_count, +1, primary_side=True)
    add_feathers(left_count, -1, primary_side=False)
    return da


def add_wind_force_symbol(
    ax, x: float, y: float, force: int,
    *,
    direction: str | None = None,
    direction_deg: float | None = None,
    xycoords="data",
    zorder: int = 20,
    **glyph_kwargs,
):
    """Axes 上の (x,y) に固定サイズの風向・風力記号を置く。"""
    if direction_deg is None:
        direction_deg = 0.0 if direction is None else WIND_DIRECTION_DEG[direction]

    glyph = make_wind_force_glyph(force, direction_deg=direction_deg, **glyph_kwargs)
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
