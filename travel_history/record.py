from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

import toml


@dataclass
class TravelRecord:
    airport_origin: str
    airport_destination: str
    flight_number: Optional[str]
    date: datetime

    @classmethod
    def from_row(cls, row):
        config = toml.load("config.toml")
        return cls(airport_origin=row['Origin Airport'],
                   airport_destination=row['Destination Airport'],
                   flight_number=None,
                   date=row['Date'])


def plot_trajectories(travel_list: List[TravelRecord]):
    ...
