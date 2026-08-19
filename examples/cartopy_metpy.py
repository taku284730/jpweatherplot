import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from metpy.units import units
from jpweatherplot import add_station_model_geo

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax.coastlines(resolution="50m")
ax.set_extent([130, 145, 30, 45], crs=ccrs.PlateCarree())

add_station_model_geo(
    ax,
    136.90, 37.39,
    weather="晴れ",
    wind_direction="北東",
    wind_force=3,
    temperature=28 * units.degC,
    pressure=1011 * units.hPa,
)

plt.show()
