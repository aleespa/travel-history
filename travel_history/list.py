from dataclasses import dataclass
from pathlib import Path
from typing import List

import toml
from pyproj import Geod
from shapely import LineString
import geopandas as gpd

from travel_history.record import TravelRecord


@dataclass
class TravelList:
    travel_list: List[TravelRecord]

    @classmethod
    def from_list(cls, travel_list):
        cls(travel_list=travel_list)

    def generate_map(self, airports):
        import matplotlib.pylab as plt
        config = toml.load("config.toml")
        data_dir = Path(config['data_dir'])
        world = gpd.read_file(data_dir / 'maps' / 'ne_10m_admin_0_countries.shp')
        world = world[~world['ISO_A3'].isin(['ATA'])]
        world = world.to_crs(epsg=4326)
        geod = Geod(ellps='WGS84')
        lines = []
        fig, ax = plt.subplots(figsize=(9.2, 4.75), dpi=100)
        for travel_record in self.travel_list:
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
        lines_gdf.plot(ax=ax, linewidth=0.6, color='k', alpha=0.3)
        ax.set_axis_off()
        ax.set_ylim(-30, 65)
        ax.set_xlim(-133, 51)
        plt.tight_layout()
        plt.show()