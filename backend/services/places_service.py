from sqlalchemy import select

from backend.database.db import SessionLocal
from backend.models.place import Place


def place_to_dict(place: Place) -> dict:
    categories = [item for item in (place.category or "").split(",") if item]
    return {
        "id": place.id,
        "name": place.name,
        "city": place.city,
        "category": categories,
        "lat": place.latitude,
        "lon": place.longitude,
        "cost": place.ticket_price or 0,
        "duration": place.average_visit_duration or 60,
        "open": place.opening_time,
        "close": place.closing_time,
        "description": place.description or "",
        "address": place.address,
        "rating": place.rating,
        "indoor_outdoor": place.indoor_outdoor,
    }


def list_places(city: str | None = None) -> list[dict]:
    with SessionLocal() as session:
        statement = select(Place).order_by(Place.name)
        if city:
            statement = statement.where(Place.city.ilike(city.strip()))
        return [place_to_dict(place) for place in session.scalars(statement).all()]
