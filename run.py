from datetime import datetime
from pathlib import Path

import requests
import toml
import pandas as pd

from travel_history.record import TravelRecord


# Load the TOML file
config = toml.load("config.toml")

travel_history = pd.read_excel(io=Path(config['travel_history']), sheet_name="data")
travel_list = [TravelRecord.from_row(row) for _, row in travel_history.iterrows()]
for travel_record in travel_list:
    print(travel_record)
print(config['data_dir'])
