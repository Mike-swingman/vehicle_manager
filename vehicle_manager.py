import math
from dataclasses import KW_ONLY, asdict, dataclass
from datetime import date

import requests


@dataclass(frozen=True)
class Vehicle:
    _: KW_ONLY
    name: str
    model: str
    year: date
    color: str
    price: int
    latitude: float
    longitude: float
    id: int | None = None

    def __repr__(self):
        return f"<Vehicle: {self.name} {self.model} {self.year} {self.color} {self.price}>"


class VehicleManager:

    def __init__(self, *, url: str):
        self.url = url

    def _get_vehicles(self) -> list[dict]:
        response = requests.get(url=f'{self.url}/vehicles')
        response.raise_for_status()
        return response.json()

    @staticmethod
    def calculate_distance(latitude_1: float, longitude_1: float,
                           latitude_2: float, longitude_2: float) -> float:
        radius_earth = 6371000

        lat_1 = math.radians(latitude_1)
        lat_2 = math.radians(latitude_2)
        delta_lat = lat_2 - lat_1
        delta_long = math.radians(longitude_2) - math.radians(longitude_1)

        # формула для подсчета расстояния
        pre_result = (pow(math.sin(delta_lat / 2), 2) + math.cos(lat_1) *
                      math.cos(lat_2) * pow(math.sin(delta_long / 2), 2))
        distance = radius_earth * (
            2 * math.atan2(math.sqrt(pre_result), math.sqrt(1 - pre_result)))

        return distance

    def get_vehicles(self) -> list[Vehicle]:
        response = self._get_vehicles()
        return [Vehicle(**v) for v in response]

    def filter_vehicles(self, params: dict) -> list[Vehicle]:
        response = self._get_vehicles()
        for key, value in params.items():
            response = filter(lambda x: x[key] == value, response)
        return [Vehicle(**v) for v in response]

    def get_vehicle(self, vehicle_id) -> Vehicle:
        response = requests.get(url=f'{self.url}/vehicles/{vehicle_id}')
        response.raise_for_status()
        return Vehicle(**response.json())

    def add_vehicle(self, vehicle: Vehicle) -> Vehicle:
        json = asdict(vehicle)
        del json['id']
        response = requests.post(url=f'{self.url}/vehicles', json=json)
        response.raise_for_status()
        return Vehicle(**response.json())

    def update_vehicle(self, vehicle: Vehicle) -> Vehicle:
        json = asdict(vehicle)
        del json['id']
        response = requests.put(url=f'{self.url}/vehicles/{vehicle.id}',
                                json=json)
        response.raise_for_status()
        return Vehicle(**response.json())

    def delete_vehicle(self, id) -> None:
        response = requests.delete(url=f'{self.url}/vehicles/{id}')
        response.raise_for_status()
        return None

    def get_distance(self, id1: int, id2: int) -> float:
        vehicle_1 = self.get_vehicle(id1)
        vehicle_2 = self.get_vehicle(id2)
        return self.calculate_distance(vehicle_1.latitude, vehicle_1.longitude,
                                       vehicle_2.latitude, vehicle_2.longitude)

    def get_nearest_vehicle(self, id: int) -> Vehicle | None:
        vehicle = self.get_vehicle(id)
        min_distance = math.inf
        nearest_vehicle = None
        for v in self._get_vehicles():
            current_vehicle = Vehicle(**v)
            if vehicle.id == current_vehicle.id:
                continue
            distance = self.calculate_distance(vehicle.latitude,
                                               vehicle.longitude,
                                               current_vehicle.latitude,
                                               current_vehicle.longitude)
            if min_distance > distance:
                min_distance = distance
                nearest_vehicle = current_vehicle
        return nearest_vehicle

