import datetime
from pathlib import Path

import toml

from travel_history.list import TravelList
from travel_history.record import TravelRecord

import pandas as pd

# Load the TOML file
config = toml.load("config.toml")
data_dir = Path(config['data_dir'])
travel_history = Path(config['travel_history'])
airports_data = Path(config['airports'])
results_path = Path('results')

travel_history = pd.read_excel(io=travel_history, sheet_name="data")
airports = pd.read_excel(io=airports_data, sheet_name="data", index_col=0).to_dict()
travel_list = TravelList([TravelRecord.from_row(row)
                          for _, row in travel_history.iterrows()],
                         airports)
travel_list.generate_map(data_dir, results_path)
travel_list.generate_video_map(data_dir=data_dir,
                               results_dir=results_path / "video",
                               initial_date=datetime.datetime(2020, 1, 1),
                               final_date=datetime.datetime(2024, 5, 1)
                               )
