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

travel_history = pd.read_excel(io=travel_history, sheet_name="data")
airports = pd.read_excel(io=airports_data, sheet_name="data", index_col=0).to_dict()
travel_list = TravelList([TravelRecord.from_row(row)
                          for _, row in travel_history.iterrows()])
travel_list.generate_map(airports)
