import csv
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from backend.database.db import SessionLocal, init_db
from backend.models.place import Place

DATASET_PATH = BASE_DIR / "data" / "processed" / "places.csv"


def as_float(value):
    return float(value) if value not in ("", None) else None


def as_int(value):
    return int(value) if value not in ("", None) else None


def seed_database() -> int:
    init_db()
    with SessionLocal() as session:
        imported = 0
        with DATASET_PATH.open(newline="", encoding="utf-8") as dataset:
            for row in csv.DictReader(dataset):
                place = session.query(Place).filter_by(name=row["name"]).first()
                values = {
                    "description": row["description"],
                    "city": row["city"],
                    "state": row["state"],
                    "country": row["country"],
                    "category": row["category"],
                    "latitude": as_float(row["latitude"]),
                    "longitude": as_float(row["longitude"]),
                    "address": row["address"] or None,
                    "opening_time": as_int(row["opening_time"]),
                    "closing_time": as_int(row["closing_time"]),
                    "ticket_price": as_float(row["ticket_price"]),
                    "average_visit_duration": as_int(row["average_visit_duration"]),
                    "rating": as_float(row["rating"]),
                    "popularity": as_float(row["popularity"]),
                    "indoor_outdoor": row["indoor_outdoor"] or None,
                    "family_friendly": row["family_friendly"].lower() == "true" if row["family_friendly"] else None,
                    "photography_friendly": row["photography_friendly"].lower() == "true" if row["photography_friendly"] else None,
                    "nature_score": as_float(row["nature_score"]),
                    "adventure_score": as_float(row["adventure_score"]),
                    "culture_score": as_float(row["culture_score"]),
                    "food_score": as_float(row["food_score"]),
                }
                if place is None:
                    session.add(Place(name=row["name"], **values))
                    imported += 1
                else:
                    for key, value in values.items():
                        setattr(place, key, value)
        session.commit()
        return imported


if __name__ == "__main__":
    print(f"Imported or updated {seed_database()} places in {BASE_DIR / 'namma_trip.db'}")
