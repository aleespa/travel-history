import datetime
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import pandas as pd
import toml
from matplotlib import pyplot as plt
from pyproj import Geod
from shapely import LineString
import geopandas as gpd

from travel_history.record import TravelRecord


@dataclass
class TravelList:
    travel_list: List[TravelRecord]
    airport_locations: dict
    world = None

    @classmethod
    def from_list(cls, travel_list, airport_locations):
        cls(travel_list=travel_list,
            airport_locations=airport_locations)

    def init_world_map(self,
                       data_dir: Path):
        self.world = gpd.read_file(data_dir / 'maps' / 'ne_10m_admin_0_countries.shp')
        self.world = self.world[~self.world['ISO_A3'].isin(['ATA'])]
        self.world = self.world.to_crs(epsg=4326)

    def generate_video_map(self,
                           results_dir: Path,
                           data_dir: Path,
                           initial_date: datetime.datetime,
                           final_date: datetime.datetime,
                           video_name="travel_history"):
        self.init_world_map(data_dir)
        fig, ax = plt.subplots(figsize=(9.2, 4.75), dpi=100)
        months = pd.date_range(start=initial_date,
                               end=final_date,
                               freq='ME')
        for month in months:
            self.generate_map(results_dir=results_dir,
                              data_dir=data_dir,
                              name=f'{month.date()}',
                              max_date=month,
                              fig=fig, ax=ax)
            ax.clear()

        images_to_video(str(results_dir),
                        video_name + ".mp4")
        remove_png_files(results_dir)

    def generate_map(self,
                     data_dir,
                     results_dir: Path,
                     name="travel_map",
                     max_date: Optional[datetime.datetime] = None,
                     fig=None,
                     ax=None):
        if max_date is None:
            max_date = max(travel_record.date
                           for travel_record in self.travel_list)
        geod = Geod(ellps='WGS84')
        if ax is None:
            self.init_world_map(data_dir)
            fig, ax = plt.subplots(figsize=(9.2, 4.75), dpi=100)
        sub_travel_list = [travel_record
                           for travel_record in self.travel_list
                           if travel_record.date <= max_date]
        lines = []
        for travel_record in sub_travel_list:
            latitudes = self.airport_locations["Latitude"]
            longitudes = self.airport_locations["Longitude"]
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

        self.world.plot(ax=ax, color='#d1f1c5', edgecolor='#4d5056', lw=0.5)
        lines_gdf.plot(ax=ax, linewidth=0.6, color='k', alpha=0.3)
        ax.set_axis_off()
        ax.set_ylim(-30, 65)
        ax.set_xlim(-133, 51)
        ax.text(x=-130, y=-20, s=f"Date: {max_date.date()}")
        plt.tight_layout()
        plt.savefig(results_dir / (name + ".png"))


def images_to_video(image_folder, video_name='video.mp4', fps=6):
    import cv2
    """
    Convert a folder of images into an MP4 video.

    Parameters:
    - image_folder: Folder containing image frames.
    - video_name: Name of the output video file (including .mp4 extension).
    - fps: Frames per second for the output video.
    """
    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    images.sort()

    frame = cv2.imread(os.path.join(image_folder, images[0]))
    h, w, layers = frame.shape
    size = (w, h)

    # Create a video writer object
    out = cv2.VideoWriter(image_folder + "\\" + video_name,
                          cv2.VideoWriter_fourcc(*'avc1'),
                          fps, size)

    for image in images:
        img_path = os.path.join(image_folder, image)
        img = cv2.imread(img_path)
        out.write(img)

    out.release()


def remove_png_files(directory):
    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        # Check if the file ends with .png
        if filename.endswith(".png"):
            file_path = os.path.join(directory, filename)  # Get the full file path
            os.remove(file_path)
