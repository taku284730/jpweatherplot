from __future__ import annotations

from numbers import Real

from matplotlib.offsetbox import AnnotationBbox, TextArea

from .weather import add_weather_symbol
from .wind import WIND_DIRECTION_DEG, add_wind_force_symbol


def _quantity_to(value, unit: str):
    """Pint/MetPy Quantity なら unit に変換。通常の数値ならそのまま。"""
    if value is None:
        return None
    if hasattr(value, "to"):
        q = value.to(unit)
        magnitude = getattr(q, "m", getattr(q, "magnitude", q))
        return float(magnitude)
    return float(value)


def _normalize_direction(direction):
    """
    方位文字列または MetPy/Pint の角度 Quantity を受け取る。
    数値は度として扱う。
    """
    if isinstance(direction, str):
        if direction not in WIND_DIRECTION_DEG:
            raise ValueError(f"unsupported wind direction: {direction!r}")
        return direction, None

    if hasattr(direction, "to"):
        q = direction.to("degree")
        magnitude = getattr(q, "m", getattr(q, "magnitude", q))
        return None, float(magnitude)

    if isinstance(direction, Real):
        return None, float(direction)

    raise TypeError("wind_direction must be a 16-point Japanese direction, degrees, or a Quantity")


def _add_fixed_text(
    ax, x, y, text,
    *,
    dx_pt, dy_pt,
    fontsize=7.5,
    xycoords="data",
    zorder=30,
):
    txt = TextArea(
        str(text),
        textprops=dict(
            fontsize=fontsize,
            ha="center", va="center",
            color="black",
        ),
    )
    ab = AnnotationBbox(
        txt,
        (x, y),
        xycoords=xycoords,
        boxcoords=("offset points"),
        xybox=(dx_pt, dy_pt),
        frameon=False,
        box_alignment=(0.5, 0.5),
        pad=0.0,
        zorder=zorder,
    )
    ax.add_artist(ab)
    return ab


def add_station_model(
    ax,
    x: float,
    y: float,
    *,
    weather: str,
    wind_direction,
    wind_force: int,
    temperature=None,
    pressure=None,
    xycoords="data",
    zorder: int = 20,

    symbol_radius: float = 4.8,
    weather_line_width: float = 0.95,
    wind_line_width: float = 0.85,

    shaft_length: float = 34.0,
    feather_spacing: float = 4.2,
    feather_length: float = 7.4,
    first_feather_length: float = 10.6,
    feather_angle_deg: float = 20.0,
    force1_tip_extension: float = 5.2,
    normal_tip_extension: float = 0.7,

    modifier_fontsize: float = 7.2,
    value_fontsize: float = 7.3,
    temp_offset_pt: tuple[float, float] = (-14.0, 10.5),
    pressure_offset_pt: tuple[float, float] = (17.0, 10.5),
):
    """
    日本式観測点モデルを1地点分描く。

    MetPy/Pint Quantity 対応:
        temperature=28 * units.degC
        pressure=1011 * units.hPa
        wind_direction=22.5 * units.degree

    wind_force は気象通報の風力階級(0〜12)を渡す。
    """
    direction_name, direction_deg = _normalize_direction(wind_direction)

    wind_kwargs = dict(
        ax=ax, x=x, y=y,
        force=wind_force,
        xycoords=xycoords,
        zorder=zorder,
        circle_radius=symbol_radius,
        shaft_length=shaft_length,
        feather_spacing=feather_spacing,
        feather_length=feather_length,
        first_feather_length=first_feather_length,
        feather_angle_deg=feather_angle_deg,
        force1_tip_extension=force1_tip_extension,
        normal_tip_extension=normal_tip_extension,
        line_width=wind_line_width,
        show_circle=False,
    )
    if direction_name is not None:
        wind_kwargs["direction"] = direction_name
    else:
        wind_kwargs["direction_deg"] = direction_deg

    wind = add_wind_force_symbol(**wind_kwargs)

    weather_artist = add_weather_symbol(
        ax, x, y, weather,
        xycoords=xycoords,
        zorder=zorder + 1,
        radius=symbol_radius,
        line_width=weather_line_width,
        modifier_fontsize=modifier_fontsize,
    )

    temp_artist = None
    if temperature is not None:
        t = _quantity_to(temperature, "degC")
        temp_artist = _add_fixed_text(
            ax, x, y, f"{t:g}",
            dx_pt=temp_offset_pt[0], dy_pt=temp_offset_pt[1],
            fontsize=value_fontsize,
            xycoords=xycoords,
            zorder=zorder + 2,
        )

    pressure_artist = None
    if pressure is not None:
        p = _quantity_to(pressure, "hPa")
        pressure_artist = _add_fixed_text(
            ax, x, y, f"{p:g}",
            dx_pt=pressure_offset_pt[0], dy_pt=pressure_offset_pt[1],
            fontsize=value_fontsize,
            xycoords=xycoords,
            zorder=zorder + 2,
        )

    return {
        "wind": wind,
        "weather": weather_artist,
        "temperature": temp_artist,
        "pressure": pressure_artist,
    }


def add_station_model_geo(
    ax,
    lon: float,
    lat: float,
    *,
    source_crs=None,
    **kwargs,
):
    """
    Cartopy GeoAxes 上に緯度経度で観測点モデルを置く。

    source_crs を省略すると PlateCarree()。
    Cartopy は optional dependency。
    """
    try:
        import cartopy.crs as ccrs
    except ImportError as exc:
        raise ImportError(
            "add_station_model_geo() requires cartopy. "
            "Install with: pip install 'jpweatherplot[cartopy]'"
        ) from exc

    if source_crs is None:
        source_crs = ccrs.PlateCarree()

    if not hasattr(ax, "projection"):
        raise TypeError("ax must be a Cartopy GeoAxes with a projection")

    x, y = ax.projection.transform_point(lon, lat, source_crs)
    return add_station_model(ax, x, y, **kwargs)
