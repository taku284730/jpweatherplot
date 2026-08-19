import matplotlib.pyplot as plt
from metpy.units import units
from jpweatherplot import add_station_model

fig, ax = plt.subplots(figsize=(5, 5))

add_station_model(
    ax, 0, 0,
    weather="晴れ",
    wind_direction=22.5 * units.degree,
    wind_force=3,
    temperature=28 * units.degC,
    pressure=1011 * units.hPa,
)

ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_aspect("equal")
ax.axis("off")
plt.show()
