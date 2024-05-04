from datetime import datetime
from pathlib import Path

import toml
import geopandas as gpd
import matplotlib.pylab as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from travel_history.record import TravelRecord

from collections import defaultdict

import pandas as pd
from pyproj import Geod
from shapely import LineString

# Load the TOML file
config = toml.load("config.toml")
data_dir = Path(config['data_dir'])
travel_history = Path(config['travel_history'])
airports_data = Path(config['airports'])

travel_history = pd.read_excel(io=travel_history, sheet_name="data")
airports = pd.read_excel(io=airports_data, sheet_name="data", index_col=0).to_dict()
travel_list = [TravelRecord.from_row(row) for _, row in travel_history.iterrows()]

world = gpd.read_file(data_dir / 'maps' / 'ne_10m_admin_0_countries.shp')
world = world[~world['ISO_A3'].isin(['ATA'])]
world = world.to_crs(epsg=4326)
geod = Geod(ellps='WGS84')
lines = []
fig, ax = plt.subplots(figsize=(9.2, 4.75), dpi=100)
for travel_record in travel_list:
    latitudes = airports["Latitude"]
    longitudes = airports["Longitude"]
    lon1, lat1 = (longitudes[travel_record.airport_origin],
                  latitudes[travel_record.airport_origin])
    lon2, lat2 = (longitudes[travel_record.airport_destination],
                  latitudes[travel_record.airport_destination])

    num_points = 100
    lon_lats = geod.npts(lon1, lat1, lon2, lat2, num_points)
    lon_lats = [(lon1, lat1)] + lon_lats + [(lon2, lat2)]
    line = LineString(lon_lats)
    lines.append(line)
    ax.scatter([lon1, lon2], [lat1, lat2], zorder=2, color='r',
               lw=0, s=10)

lines_gdf = gpd.GeoDataFrame(geometry=lines)

world.plot(ax=ax, color='#d1f1c5', edgecolor='#4d5056', lw=0.5)
lines_gdf.plot(ax=ax, linewidth=0.3, color='k', alpha=0.5)
ax.set_axis_off()
ax.set_ylim(-30, 65)
ax.set_xlim(-133, 51)
plt.tight_layout()
plt.show()
