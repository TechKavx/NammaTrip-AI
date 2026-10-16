# NammaTrip AI

NammaTrip AI is an intelligent local tourism planner. The existing planner UI,
weather-aware recommendations, route map, hidden gems, and travel assistant are
being progressively upgraded from the hackathon prototype.

## Phase 1 foundation

- Flask application with the existing frontend and `/api/plan` contract preserved
- SQLAlchemy 2 with a local SQLite database
- `Place` model with nullable fields for data that is not verified yet
- Coimbatore place records loaded from `data/processed/places.csv`
- `GET /api/places` with optional `?city=Coimbatore` filtering
- Repeatable seed script in `data/seed_database.py`

The current dataset contains real named Coimbatore destinations carried forward
from the prototype. Values that were not verified from an open source are not
presented as authoritative; those fields remain blank in the normalized dataset.
The next data phase should replace or extend it with an explicitly downloaded
OpenStreetMap/Overpass or Wikidata dataset and preserve its license/source URL.

## Run on Windows

```powershell
py -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python data\seed_database.py
python app.py
```

Open http://127.0.0.1:5000.

The app also initializes the schema and repeats the idempotent seed on startup.
The database file is `namma_trip.db` and is ignored by Git.

## API smoke tests

```powershell
curl http://127.0.0.1:5000/api/places
curl "http://127.0.0.1:5000/api/places?city=Coimbatore"
curl -X POST http://127.0.0.1:5000/api/plan `
	-H "Content-Type: application/json" `
	-d '{"city":"Coimbatore","budget":1500,"number_of_persons":1,"start":"10:00","end":"19:00","interests":["nature","photography"],"transport":"car"}'
```

## Configuration

Copy `.env.example` to `.env`. Open-Meteo currently does not require an API key.
Secrets must remain server-side and `.env` is ignored.

## Data ownership

- Application data: SQLite records seeded from `data/processed/places.csv`
- Open data: source and license must be recorded in `data/raw/` when imported
- External data: current weather is fetched by the Flask backend from Open-Meteo
- User content: not implemented in Phase 1
- AI explanations: existing prototype logic, not a factual source of place data

## Next phases

Add a verified open tourism import, separate weather/maps services, itinerary and
budget services, tests, user accounts, saved trips, reviews, and PostgreSQL
configuration incrementally. These are intentionally not claimed as complete in
Phase 1.
