from flask import Flask, render_template, request, jsonify
import math
import requests

from backend.database.db import init_db
from backend.services.places_service import list_places
from data.seed_database import seed_database

app = Flask(__name__)

init_db()
seed_database()

# -----------------------------
# Demo local tourism dataset
# Add more places here for your hackathon city.

# -----------------------------
PLACES = [
    {"name":"Marudamalai Temple","city":"Coimbatore","category":["spiritual","photography","nature"],
     "lat":11.0461,"lon":76.8820,"cost":0,"duration":90,"open":6,"close":20,
     "description":"Hilltop temple with scenic views and a peaceful atmosphere."},
    {"name":"Gedee Car Museum","city":"Coimbatore","category":["history","photography","indoor"],
     "lat":11.0074,"lon":76.9845,"cost":200,"duration":90,"open":9,"close":18,
     "description":"Automobile museum with vintage and classic vehicles."},
    {"name":"VOC Park","city":"Coimbatore","category":["nature","family","photography"],
     "lat":11.0027,"lon":76.9577,"cost":20,"duration":75,"open":10,"close":19,
     "description":"Relaxing city park suitable for families and casual photography."},
    {"name":"Brookefields Mall","city":"Coimbatore","category":["shopping","food","indoor"],
     "lat":11.0142,"lon":76.9634,"cost":0,"duration":120,"open":10,"close":22,
     "description":"Popular shopping and entertainment destination with many food options."},
    {"name":"Isha Yoga Center","city":"Coimbatore","category":["nature","spiritual","photography"],
     "lat":10.9725,"lon":76.7360,"cost":0,"duration":150,"open":6,"close":20,
     "description":"Scenic spiritual destination at the foothills of the Velliangiri Hills."},
    {"name":"Eachanari Vinayagar Temple","city":"Coimbatore","category":["spiritual","photography"],
     "lat":10.9345,"lon":76.9684,"cost":0,"duration":60,"open":6,"close":21,
     "description":"Well-known local temple and cultural landmark."},
    {"name":"Kovai Kondattam","city":"Coimbatore","category":["adventure","family","nature"],
     "lat":10.9680,"lon":76.8520,"cost":750,"duration":180,"open":10,"close":18,
     "description":"Water-based amusement and recreational activities."},
    {"name":"Gass Forest Museum","city":"Coimbatore","category":["history","indoor","nature"],
     "lat":11.0020,"lon":76.9480,"cost":10,"duration":60,"open":9,"close":17,
     "description":"Small natural-history museum with local exhibits."},
    {"name":"Ukkadam Lake","city":"Coimbatore","category":["nature","photography"],
     "lat":10.9890,"lon":76.9660,"cost":0,"duration":60,"open":6,"close":19,
     "description":"Urban lake area suited for a short scenic stop."},
    {"name":"RS Puram Food Street","city":"Coimbatore","category":["food","shopping"],
     "lat":11.0178,"lon":76.9550,"cost":300,"duration":90,"open":17,"close":22,
        "description":"Area with many local food choices and evening street activity."},

        # Chennai dataset estimates
        {"name":"Marina Beach","city":"Chennai","category":["nature","family","photography"],
        "lat":13.0500,"lon":80.2824,"cost":0,"duration":90,"open":5,"close":21,
        "description":"Chennai's well-known urban beach and promenade, suited for a scenic walk."},
        {"name":"Kapaleeshwarar Temple","city":"Chennai","category":["spiritual","history","photography"],
        "lat":13.0338,"lon":80.2697,"cost":0,"duration":60,"open":6,"close":21,
        "description":"Historic Dravidian-style temple in the Mylapore neighbourhood."},
        {"name":"Fort St. George","city":"Chennai","category":["history","photography"],
        "lat":13.0795,"lon":80.2870,"cost":20,"duration":90,"open":9,"close":17,"description":"Historic fort complex and early colonial landmark in Chennai."},
        {"name":"Government Museum Chennai","city":"Chennai","category":["history","indoor","family"],
        "lat":13.0694,"lon":80.2574,"cost":20,"duration":120,"open":9,"close":17,
        "description":"Museum complex with archaeology, art and natural-history collections."},
        {"name":"San Thome Basilica","city":"Chennai","category":["history","spiritual","photography"],
        "lat":13.0339,"lon":80.2761,"cost":0,"duration":45,"open":6,"close":20,
        "description":"Historic basilica and prominent landmark near the Marina coast."},
        {"name":"Guindy National Park","city":"Chennai","category":["nature","family","photography"],
        "lat":13.0068,"lon":80.2206,"cost":20,"duration":120,"open":9,"close":17,
        "description":"Urban national park known for its greenery and protected wildlife habitat."},

        # Madurai dataset estimates
        {"name":"Meenakshi Amman Temple","city":"Madurai","category":["spiritual","history","photography"],
        "lat":9.9195,"lon":78.1193,"cost":0,"duration":120,"open":5,"close":22,
        "description":"Famous historic temple complex and central landmark of Madurai."},
        {"name":"Thirumalai Nayakkar Palace","city":"Madurai","category":["history","photography"],
        "lat":9.9177,"lon":78.1194,"cost":50,"duration":90,"open":9,"close":17,
        "description":"Seventeenth-century palace known for its grand courtyard and architecture."},
        {"name":"Gandhi Memorial Museum","city":"Madurai","category":["history","indoor"],
        "lat":9.9312,"lon":78.1376,"cost":0,"duration":90,"open":10,"close":17,"description":"Museum documenting India's freedom movement and Gandhi's life."},
        {"name":"Alagar Koyil","city":"Madurai","category":["spiritual","history","nature"],
        "lat":10.0756,"lon":78.3340,"cost":0,"duration":90,"open":6,"close":20,
        "description":"Historic hill temple set in a scenic area north of Madurai."},
        {"name":"Vandiyur Mariamman Teppakulam","city":"Madurai","category":["spiritual","photography","nature"],
        "lat":9.9065,"lon":78.1420,"cost":0,"duration":60,"open":6,"close":20,
        "description":"Large temple tank and local landmark, especially atmospheric in the evening."},
        {"name":"Samanar Hills","city":"Madurai","category":["history","nature","photography"],
        "lat":9.8958,"lon":78.0165,"cost":0,"duration":90,"open":6,"close":18,
        "description":"Rocky hill site with ancient Jain carvings and broad surrounding views."},

        # Ooty dataset estimates
        {"name":"Government Botanical Garden","city":"Ooty","category":["nature","photography","family"],
        "lat":11.4116,"lon":76.7115,"cost":50,"duration":120,"open":7,"close":18,"description":"Landscaped hillside garden with diverse plants and seasonal flowers."},
        {"name":"Ooty Lake","city":"Ooty","category":["nature","family","photography"],
        "lat":11.4064,"lon":76.6932,"cost":20,"duration":90,"open":9,"close":18,"description":"Scenic mountain lake with boating and a relaxed lakeside setting."},
        {"name":"Doddabetta Peak","city":"Ooty","category":["nature","photography","adventure"],
        "lat":11.4064,"lon":76.7353,"cost":10,"duration":90,"open":7,"close":18,"description":"The highest peak in the Nilgiris, offering expansive hill views."},
        {"name":"Government Rose Garden","city":"Ooty","category":["nature","photography"],
        "lat":11.4085,"lon":76.7031,"cost":50,"duration":90,"open":7,"close":18,"description":"Terraced garden featuring a large collection of roses on the hillside."},
        {"name":"Tea Factory and Tea Museum","city":"Ooty","category":["history","indoor","photography"],
        "lat":11.3974,"lon":76.6996,"cost":25,"duration":75,"open":9,"close":18,"description":"Tea-focused museum explaining local production and Nilgiri tea culture."},
        {"name":"Pykara Lake","city":"Ooty","category":["nature","photography","family"],
        "lat":11.4477,"lon":76.6194,"cost":20,"duration":120,"open":8,"close":18,"description":"Popular lake and waterfall area surrounded by Nilgiri forest scenery."},

        # Bangalore dataset estimates
        {"name":"Lalbagh Botanical Garden","city":"Bangalore","category":["nature","photography","family"],
        "lat":12.9507,"lon":77.5848,"cost":30,"duration":120,"open":6,"close":19,"description":"Historic botanical garden with landscaped grounds and plant collections."},
        {"name":"Cubbon Park","city":"Bangalore","category":["nature","family","photography"],
        "lat":12.9763,"lon":77.5929,"cost":0,"duration":90,"open":6,"close":18,"description":"Large central city park suited for walking, relaxation and photography."},
        {"name":"Bangalore Palace","city":"Bangalore","category":["history","photography"],
        "lat":12.9987,"lon":77.5920,"cost":250,"duration":90,"open":10,"close":17,"description":"Historic palace known for its Tudor-inspired architecture and grounds."},
        {"name":"Vidhana Soudha","city":"Bangalore","category":["history","photography"],
        "lat":12.9796,"lon":77.5907,"cost":0,"duration":45,"open":9,"close":18,"description":"Iconic government building and landmark of Bangalore's central district."},
        {"name":"Visvesvaraya Industrial and Technological Museum","city":"Bangalore","category":["history","indoor","family"],
        "lat":12.9753,"lon":77.5963,"cost":100,"duration":120,"open":9,"close":18,"description":"Interactive science and technology museum near Cubbon Park."},
        {"name":"ISKCON Temple Bangalore","city":"Bangalore","category":["spiritual","photography","family"],
        "lat":13.0104,"lon":77.5511,"cost":0,"duration":75,"open":7,"close":20,"description":"Large modern temple complex and cultural centre on Hare Krishna Hill."}
]
# -----------------------------
# Hidden gems / local secrets
# -----------------------------

HIDDEN_GEMS = [
    {
        "name": "Ukkadam Lake Sunset Point",
        "city": "Coimbatore",
        "category": ["nature", "photography"],
        "cost": 0,
        "description": "A peaceful local spot for sunset views, photography and a relaxed evening."
    },
    {
        "name": "Gass Forest Museum",
        "city": "Coimbatore",
        "category": ["history", "nature", "indoor"],
        "cost": 10,
        "description": "A compact museum featuring interesting natural-history exhibits."
    },
    {
        "name": "Eachanari Local Food Trail",
        "city": "Coimbatore",
        "category": ["food", "photography"],
        "cost": 250,
        "description": "Explore local food choices around one of Coimbatore's popular neighbourhoods."
    },
    {
        "name": "Race Course Evening Walk",
        "city": "Coimbatore",
        "category": ["nature", "photography", "family"],
        "cost": 0,
        "description": "A pleasant evening walking area popular for casual strolls and city photography."
    },
    {
        "name": "Perur Temple Heritage Area",
        "city": "Coimbatore",
        "category": ["spiritual", "history", "photography"],
        "cost": 0,
        "description": "A culturally rich area offering traditional architecture and local heritage."
    },
    {
        "name": "Valankulam Lake",
        "city": "Coimbatore",
        "category": ["nature", "photography"],
        "cost": 0,
        "description": "An urban lake area that works well for a quiet break and casual photography."
    },
    {
        "name": "Theosophical Society Gardens",
        "city": "Chennai",
        "category": ["nature", "photography"],
        "cost": 0,
        "description": "Quiet riverside gardens in Adyar known for mature trees and peaceful walks."
    },
    {
        "name": "Cholamandal Artists' Village",
        "city": "Chennai",
        "category": ["history", "photography"],
        "cost": 50,
        "description": "Artist community and gallery space showcasing modern Indian art."
    },
    {
        "name": "Puthu Mandapam Market",
        "city": "Madurai",
        "category": ["shopping", "history", "photography"],
        "cost": 200,
        "description": "Historic market area near the temple with local crafts and textiles."
    },
    {
        "name": "Koodal Azhagar Temple",
        "city": "Madurai",
        "category": ["spiritual", "history", "photography"],
        "cost": 0,
        "description": "An important historic Vishnu temple in the heart of Madurai."
    },
    {
        "name": "Ketti Valley View",
        "city": "Ooty",
        "category": ["nature", "photography"],
        "cost": 10,
        "description": "Viewpoint overlooking the broad Ketti Valley and surrounding Nilgiri hills."
    },
    {
        "name": "St. Stephen's Church Ooty",
        "city": "Ooty",
        "category": ["history", "photography"],
        "cost": 0,
        "description": "Historic hill-station church with distinctive colonial-era architecture."
    },
    {
        "name": "Bugle Rock Park",
        "city": "Bangalore",
        "category": ["nature", "photography", "family"],
        "cost": 0,
        "description": "Rocky park in Basavanagudi with shaded paths and a relaxed local atmosphere."
    },
    {
        "name": "KR Market Flower Market",
        "city": "Bangalore",
        "category": ["shopping", "photography", "food"],
        "cost": 100,
        "description": "Lively historic market area known for early-morning flower trading and local produce."
    }
]
CITY_COORDS = {
    "coimbatore": (11.0168, 76.9558),
    "chennai": (13.0827, 80.2707),
    "madurai": (9.9252, 78.1198),
    "ooty": (11.4102, 76.6950),
    "bangalore": (12.9716, 77.5946)
}

# The planner keeps its existing dictionary contract, but records now come
# from SQLite so the rest of the prototype does not need a rewrite yet.
PLACES = list_places()

# -----------------------------
# Ask NammaTrip knowledge data
# -----------------------------

PLACE_DETAILS = {
    "marudamalai temple": {
        "best_time": "Early morning or evening (demo estimate)",
        "activities": ["Temple visit", "Hilltop photography", "Enjoying the views"],
        "tips": ["Wear comfortable footwear", "Carry water", "Check local notices on festival days"]
    },
    "gedee car museum": {
        "best_time": "Late morning or early afternoon",
        "activities": ["Viewing vintage cars", "Museum photography", "Learning about automobiles"],
        "tips": ["Allow around 90 minutes", "Confirm holiday timings before visiting"]
    },
    "voc park": {
        "best_time": "Morning or late afternoon",
        "activities": ["Walking", "Family recreation", "Casual photography"],
        "tips": ["Late afternoon may be more comfortable", "Carry water for a longer walk"]
    },
    "brookefields mall": {
        "best_time": "Afternoon or evening",
        "activities": ["Shopping", "Dining", "Indoor entertainment"],
        "tips": ["Useful during hot or wet weather", "Allow extra time for food and shopping"]
    },
    "isha yoga center": {
        "best_time": "Morning or late afternoon",
        "activities": ["Exploring the centre", "Scenic photography", "Quiet reflection"],
        "tips": ["Follow visitor guidelines", "Comfortable clothing is recommended"]
    },
    "eachanari vinayagar temple": {
        "best_time": "Morning or evening",
        "activities": ["Temple visit", "Cultural observation", "Photography from permitted areas"],
        "tips": ["Dress respectfully", "Check local crowd and festival timings"]
    },
    "kovai kondattam": {
        "best_time": "Late morning to afternoon",
        "activities": ["Water activities", "Family recreation", "Outdoor leisure"],
        "tips": ["Carry a change of clothes", "Confirm ride availability and entry rates"]
    },
    "gass forest museum": {
        "best_time": "Late morning or afternoon",
        "activities": ["Viewing natural-history exhibits", "Educational visit", "Indoor photography where permitted"],
        "tips": ["Allow about an hour", "Confirm opening days before visiting"]
    },
    "ukkadam lake": {
        "best_time": "Early morning or sunset",
        "activities": ["Scenic walk", "Bird and landscape observation", "Photography"],
        "tips": ["Sunset visibility depends on weather", "Stay in public viewing areas"]
    },
    "rs puram food street": {
        "best_time": "Evening",
        "activities": ["Trying local food", "Street photography", "Neighbourhood walk"],
        "tips": ["Carry small change", "Popular stalls may be busy at peak dinner time"]
    },
    "marina beach": {
        "best_time": "Early morning or evening",
        "activities": ["Beach walk", "Photography", "Enjoying the promenade"],
        "tips": ["Avoid entering the water unless local conditions permit", "Carry sun protection"]
    },
    "kapaleeshwarar temple": {
        "best_time": "Early morning or evening",
        "activities": ["Temple visit", "Architecture viewing", "Cultural photography where permitted"],
        "tips": ["Dress respectfully", "Expect larger crowds during festivals"]
    },
    "fort st. george": {
        "best_time": "Morning",
        "activities": ["Historic site visit", "Museum visit", "Architecture photography"],
        "tips": ["Carry identification if required at entry", "Allow time for security checks"]
    },
    "government museum chennai": {
        "best_time": "Late morning or afternoon",
        "activities": ["Viewing art and archaeology exhibits", "Educational visit", "Indoor exploration"],
        "tips": ["Allow two hours for a relaxed visit", "Confirm museum holiday timings"]
    },
    "san thome basilica": {
        "best_time": "Morning or late afternoon",
        "activities": ["Architecture viewing", "Quiet visit", "Photography where permitted"],
        "tips": ["Maintain silence during services", "Dress respectfully"]
    },
    "guindy national park": {
        "best_time": "Early morning",
        "activities": ["Nature walk", "Wildlife observation", "Photography"],
        "tips": ["Follow park instructions", "Carry water and avoid feeding animals"]
    },
    "meenakshi amman temple": {
        "best_time": "Early morning or evening",
        "activities": ["Temple visit", "Architecture viewing", "Cultural observation"],
        "tips": ["Dress respectfully", "Security and photography rules may apply"]
    },
    "thirumalai nayakkar palace": {
        "best_time": "Morning or late afternoon",
        "activities": ["Architecture viewing", "History visit", "Photography"],
        "tips": ["Allow around 90 minutes", "Check show timings separately if applicable"]
    },
    "gandhi memorial museum": {
        "best_time": "Late morning or afternoon",
        "activities": ["Viewing historical exhibits", "Educational visit", "Indoor exploration"],
        "tips": ["Allow about 90 minutes", "Confirm opening days before visiting"]
    },
    "alagar koyil": {
        "best_time": "Morning or late afternoon",
        "activities": ["Temple visit", "Hill-area scenery", "Photography from permitted areas"],
        "tips": ["Carry water", "Travel time from central Madurai can vary"]
    },
    "vandiyur mariamman teppakulam": {
        "best_time": "Early morning or evening",
        "activities": ["Scenic walk", "Local landmark visit", "Photography"],
        "tips": ["Evenings may be busier", "Stay clear of restricted edges"]
    },
    "samanar hills": {
        "best_time": "Early morning or late afternoon",
        "activities": ["Heritage viewing", "Short climb", "Landscape photography"],
        "tips": ["Wear sturdy footwear", "Avoid climbing during very hot weather"]
    },
    "government botanical garden": {
        "best_time": "Morning or late afternoon",
        "activities": ["Garden walk", "Plant viewing", "Photography"],
        "tips": ["Wear comfortable walking shoes", "Weather can change quickly in Ooty"]
    },
    "ooty lake": {
        "best_time": "Morning or late afternoon",
        "activities": ["Lakeside walk", "Boating subject to availability", "Photography"],
        "tips": ["Confirm boating availability", "Carry a light jacket"]
    },
    "doddabetta peak": {
        "best_time": "Morning for clearer views",
        "activities": ["Viewpoint visit", "Hill photography", "Short outdoor walk"],
        "tips": ["Visibility depends on clouds", "Carry warm clothing and water"]
    },
    "government rose garden": {
        "best_time": "Morning or late afternoon",
        "activities": ["Garden walk", "Flower viewing", "Photography"],
        "tips": ["Allow time for the hillside paths", "Wear comfortable footwear"]
    },
    "tea factory and tea museum": {
        "best_time": "Late morning or afternoon",
        "activities": ["Tea-making overview", "Museum visit", "Tea tasting where available"],
        "tips": ["Confirm factory access before visiting", "Carry a jacket for the hill climate"]
    },
    "pykara lake": {
        "best_time": "Morning or early afternoon",
        "activities": ["Lake visit", "Waterfall viewing", "Photography"],
        "tips": ["Travel time can be significant", "Confirm boating and local access conditions"]
    },
    "lalbagh botanical garden": {
        "best_time": "Early morning or late afternoon",
        "activities": ["Garden walk", "Plant viewing", "Photography"],
        "tips": ["Wear comfortable shoes", "Special events may affect entry arrangements"]
    },
    "cubbon park": {
        "best_time": "Morning or evening",
        "activities": ["Walking", "Relaxing outdoors", "Photography"],
        "tips": ["Use marked paths", "Carry water for longer walks"]
    },
    "bangalore palace": {
        "best_time": "Late morning or afternoon",
        "activities": ["Palace visit", "Architecture viewing", "Photography where permitted"],
        "tips": ["Confirm entry charges and event access", "Allow around 90 minutes"]
    },
    "vidhana soudha": {
        "best_time": "Late afternoon for exterior viewing",
        "activities": ["Landmark viewing", "Architecture photography", "Central Bengaluru walk"],
        "tips": ["Exterior access may be restricted", "Follow security instructions"]
    },
    "visvesvaraya industrial and technological museum": {
        "best_time": "Late morning or afternoon",
        "activities": ["Interactive exhibits", "Science learning", "Indoor exploration"],
        "tips": ["Allow about two hours", "Useful option during hot or rainy weather"]
    },
    "iskcon temple bangalore": {
        "best_time": "Morning or evening",
        "activities": ["Temple visit", "Cultural observation", "Architecture viewing"],
        "tips": ["Dress respectfully", "Follow visitor and photography rules"]
    }
}

NEARBY_PLACES = [
    {"name":"Demo local restaurant near Marudamalai","city":"Coimbatore","type":"restaurant","near":"Marudamalai Temple","lat":11.0440,"lon":76.8790,"description":"Demo local restaurant option near the temple area.","price_level":"Estimated budget"},
    {"name":"Demo cafe near RS Puram","city":"Coimbatore","type":"cafe","near":"RS Puram Food Street","lat":11.0190,"lon":76.9560,"description":"Demo cafe option for a short break in the RS Puram area.","price_level":"Estimated moderate"},
    {"name":"Demo hotel near Coimbatore centre","city":"Coimbatore","type":"hotel","near":"Coimbatore","lat":11.0160,"lon":76.9580,"description":"Demo hotel listing for hackathon conversations, not live availability.","price_level":"Estimated moderate"},
    {"name":"Demo budget stay near Ukkadam","city":"Coimbatore","type":"budget_stay","near":"Ukkadam Lake","lat":10.9870,"lon":76.9640,"description":"Demo budget-stay category near the Ukkadam area.","price_level":"Estimated budget"},
    {"name":"Brookefields Mall","city":"Coimbatore","type":"shopping","near":"Coimbatore","lat":11.0142,"lon":76.9634,"description":"Existing tourism dataset location with shopping and food options.","price_level":"Varies"},
    {"name":"Demo hospital near Coimbatore centre","city":"Coimbatore","type":"hospital","near":"Coimbatore","lat":11.0180,"lon":76.9550,"description":"Demo hospital category for trip-planning guidance, not live navigation.","price_level":"Not applicable"},
    {"name":"Demo pharmacy near Coimbatore centre","city":"Coimbatore","type":"pharmacy","near":"Coimbatore","lat":11.0170,"lon":76.9570,"description":"Demo pharmacy category for hackathon guidance.","price_level":"Varies"},
    {"name":"Demo ATM near Coimbatore centre","city":"Coimbatore","type":"atm","near":"Coimbatore","lat":11.0160,"lon":76.9560,"description":"Demo ATM category; verify the nearest live option locally.","price_level":"Not applicable"},
    {"name":"Demo petrol station near Coimbatore centre","city":"Coimbatore","type":"petrol_station","near":"Coimbatore","lat":11.0200,"lon":76.9600,"description":"Demo petrol-station category; verify current availability locally.","price_level":"Varies"},
    {"name":"Demo taxi and bus pickup near Coimbatore centre","city":"Coimbatore","type":"transport","near":"Coimbatore","lat":11.0168,"lon":76.9558,"description":"Demo transport option; local routes and fares are estimated.","price_level":"Estimated"},
    {"name":"Demo restaurant near Marina Beach","city":"Chennai","type":"restaurant","near":"Marina Beach","lat":13.0505,"lon":80.2800,"description":"Demo local restaurant option near the Marina area.","price_level":"Estimated budget"},
    {"name":"Demo hotel near Marina Beach","city":"Chennai","type":"hotel","near":"Marina Beach","lat":13.0550,"lon":80.2820,"description":"Demo hotel listing, not live availability.","price_level":"Estimated moderate"},
    {"name":"Demo cafe near Kapaleeshwarar Temple","city":"Chennai","type":"cafe","near":"Kapaleeshwarar Temple","lat":13.0350,"lon":80.2690,"description":"Demo cafe option near the Mylapore area.","price_level":"Estimated moderate"},
    {"name":"Demo shopping area near Madurai temple","city":"Madurai","type":"shopping","near":"Meenakshi Amman Temple","lat":9.9205,"lon":78.1210,"description":"Demo shopping category near the central temple area.","price_level":"Varies"},
    {"name":"Demo restaurant near Meenakshi Temple","city":"Madurai","type":"restaurant","near":"Meenakshi Amman Temple","lat":9.9180,"lon":78.1210,"description":"Demo local restaurant option near the temple area.","price_level":"Estimated budget"},
    {"name":"Demo budget stay near Madurai centre","city":"Madurai","type":"budget_stay","near":"Madurai","lat":9.9250,"lon":78.1200,"description":"Demo budget-stay category, not live availability.","price_level":"Estimated budget"},
    {"name":"Demo cafe near Ooty Lake","city":"Ooty","type":"cafe","near":"Ooty Lake","lat":11.4070,"lon":76.6950,"description":"Demo cafe option near Ooty Lake.","price_level":"Estimated moderate"},
    {"name":"Demo hotel near Ooty Lake","city":"Ooty","type":"hotel","near":"Ooty Lake","lat":11.4050,"lon":76.6940,"description":"Demo hotel listing, not live availability.","price_level":"Estimated moderate"},
    {"name":"Demo restaurant near Lalbagh","city":"Bangalore","type":"restaurant","near":"Lalbagh Botanical Garden","lat":12.9500,"lon":77.5820,"description":"Demo restaurant option near Lalbagh.","price_level":"Estimated budget"},
    {"name":"Demo hotel near Cubbon Park","city":"Bangalore","type":"hotel","near":"Cubbon Park","lat":12.9750,"lon":77.5910,"description":"Demo hotel listing, not live availability.","price_level":"Estimated moderate"},
    {"name":"Demo metro and bus connection near Cubbon Park","city":"Bangalore","type":"transport","near":"Cubbon Park","lat":12.9760,"lon":77.5915,"description":"Demo transport category; verify current routes and timings.","price_level":"Estimated"}
]

def haversine(lat1, lon1, lat2, lon2):
    r = 6371
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2-lat1)
    dl = math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(math.sqrt(a))

def geocode_city(city):
    key = city.strip().lower()
    if key in CITY_COORDS:
        return CITY_COORDS[key]
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        data = requests.get(url, params={"name": city, "count": 1, "language":"en", "format":"json"}, timeout=4).json()
        if data.get("results"):
            return data["results"][0]["latitude"], data["results"][0]["longitude"]
    except Exception:
        pass
    return None

def get_weather(lat, lon):
    try:
        data = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude":lat,"longitude":lon,"current":"temperature_2m,precipitation,rain,weather_code","timezone":"auto"},
            timeout=4
        ).json()
        cur = data.get("current", {})
        rain = float(cur.get("rain", 0) or 0) + float(cur.get("precipitation", 0) or 0)
        code = int(cur.get("weather_code", 0) or 0)
        if rain > 0 or code in [51,53,55,61,63,65,80,81,82,95,96,99]:
            label = "Rainy / Wet"
            mode = "indoor"
        elif code in [1,2,3,45,48]:
            label = "Cloudy"
            mode = "normal"
        else:
            label = "Clear"
            mode = "outdoor"
        return {"temperature": cur.get("temperature_2m"), "label": label, "mode": mode}
    except Exception:
        return {"temperature":"—", "label":"Weather unavailable", "mode":"normal"}

def parse_time(s):
    # HTML time -> decimal hour
    h, m = map(int, s.split(":"))
    return h + m/60

def score_place(place, interests, budget_left, weather_mode, center, used_names):
    interest_score = sum(1 for x in interests if x in place["category"]) * 25
    if "indoor" in place["category"] and weather_mode == "indoor":
        weather_score = 25
    elif weather_mode == "outdoor" and "indoor" not in place["category"]:
        weather_score = 20
    else:
        weather_score = 10

    distance = haversine(center[0], center[1], place["lat"], place["lon"])
    distance_score = max(0, 25 - min(distance, 25))
    budget_score = 20 if place["cost"] <= budget_left else max(0, 20 - (place["cost"]-budget_left)/20)
    repeat_penalty = 100 if place["name"] in used_names else 0

    return interest_score + weather_score + distance_score + budget_score - repeat_penalty, distance

def build_itinerary(city, budget, start, end, interests, transport, weather,
                    required_places=None, number_of_persons=1):
    center = geocode_city(city)
    if not center:
        center = CITY_COORDS["coimbatore"]

    # Use only destinations belonging to the selected city.
    candidates = [p for p in PLACES if p["city"].strip().lower() == city.strip().lower()]
    required_places = required_places or []
    required_names = {p["name"] for p in required_places}
    existing_names = {p["name"] for p in candidates}
    candidates.extend(
        place for place in required_places
        if place["name"] not in existing_names
    )
    number_of_persons = max(1, int(number_of_persons or 1))

    current = start
    spent_per_person = 0
    total_distance = 0
    items = []
    used = set()
    pending_required = set(required_names)

    # Greedy context-aware recommendation.
    while current < end and len(items) < 5:
        remaining = budget - (spent_per_person * number_of_persons)
        scored = []
        for p in candidates:
            if p["name"] in used:
                continue
            if pending_required and p["name"] not in pending_required:
                continue
            group_cost = p["cost"] * number_of_persons
            if group_cost > remaining:
                continue
            if p["name"] not in pending_required and not (p["open"] <= current < p["close"]):
                continue
            if p["name"] in pending_required and current >= p["close"]:
                continue
            s, d = score_place(
                p,
                interests,
                max(0, remaining / number_of_persons),
                weather["mode"],
                center,
                used
            )
            scored.append((s, p, d))

        if not scored:
            break

        scored.sort(
            key=lambda x: (x[1]["name"] not in required_names, -x[0])
        )
        _, p, d = scored[0]

        # Estimate travel time from previous stop.
        travel_km = d if not items else haversine(items[-1]["lat"], items[-1]["lon"], p["lat"], p["lon"])
        speed = {"walk":4, "bike":20, "car":30, "bus":22}.get(transport, 25)
        travel_min = max(5, round((travel_km / speed) * 60))
        arrival = current + travel_min/60
        if p["name"] in required_names and arrival < p["open"]:
            arrival = p["open"]
        if arrival + p["duration"]/60 > end:
            used.add(p["name"])
            if len(used) >= len(candidates):
                break
            continue

        start_h = int(arrival)
        start_m = int(round((arrival-start_h)*60))
        if start_m == 60:
            start_h += 1; start_m = 0
        finish = arrival + p["duration"]/60
        fh = int(finish)
        fm = int(round((finish-fh)*60))
        if fm == 60:
            fh += 1; fm = 0

        items.append({
            "name":p["name"],
            "description":p["description"],
            "cost":p["cost"],
            "duration":p["duration"],
            "distance":round(travel_km,1),
            "travel_min":travel_min,
            "start":f"{start_h:02d}:{start_m:02d}",
            "end":f"{fh:02d}:{fm:02d}",
            "lat":p["lat"], "lon":p["lon"]
        })
        spent_per_person += p["cost"]
        total_distance += travel_km
        current = finish
        used.add(p["name"])
        pending_required.discard(p["name"])

    return items, round(spent_per_person), round(total_distance,1)
# -----------------------------
# Hidden gem recommendation
# -----------------------------

def get_hidden_gems(city, interests, budget):

    city_gems = [
        gem for gem in HIDDEN_GEMS
        if gem["city"].lower() == city.lower()
    ]

    scored = []

    for gem in city_gems:

        if gem["cost"] > budget:
            continue

        score = 0

        # Match user interests
        for interest in interests:
            if interest in gem["category"]:
                score += 30

        # Free / low-cost places get a small bonus
        if gem["cost"] == 0:
            score += 10
        elif gem["cost"] <= budget * 0.2:
            score += 5

        scored.append((score, gem))

    scored.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return [
        {
            "name": gem["name"],
            "description": gem["description"],
            "cost": gem["cost"],
            "category": gem["category"]
        }
        for score, gem in scored[:3]
    ]

def normalize_text(value):
    return " ".join(str(value or "").strip().lower().split())

def find_place(city, query):
    query_text = normalize_text(query)
    if not query_text:
        return None

    city_key = normalize_text(city)
    aliases = {
        "marudamalai": "marudamalai temple",
        "meenakshi": "meenakshi amman temple",
        "marina": "marina beach",
        "lalbagh": "lalbagh botanical garden",
        "cubbon": "cubbon park"
    }
    query_text = aliases.get(query_text, query_text)
    city_places = [
        place for place in PLACES
        if normalize_text(place["city"]) == city_key
    ]
    exact = next(
        (place for place in city_places if normalize_text(place["name"]) == query_text),
        None
    )
    if exact:
        return exact
    return next(
        (place for place in city_places if normalize_text(place["name"]) in query_text),
        None
    )

def resolve_ask_place(city, message, current_place):
    message_text = normalize_text(message)
    city_places = [
        place for place in PLACES
        if normalize_text(place["city"]) == normalize_text(city)
    ]
    explicit = sorted(city_places, key=lambda place: len(place["name"]), reverse=True)
    for place in explicit:
        if normalize_text(place["name"]) in message_text:
            return place

    for gem in HIDDEN_GEMS:
        if normalize_text(gem["city"]) == normalize_text(city) and normalize_text(gem["name"]) in message_text:
            return resolve_hidden_gem(city, gem["name"])

    aliases = {
        "marudamalai": "Marudamalai Temple",
        "meenakshi": "Meenakshi Amman Temple",
        "marina": "Marina Beach",
        "lalbagh": "Lalbagh Botanical Garden",
        "cubbon": "Cubbon Park"
    }
    for alias, place_name in aliases.items():
        if alias in message_text:
            return find_place(city, place_name)

    exact_hidden_gem = resolve_hidden_gem(city, current_place)
    return exact_hidden_gem or find_place(city, current_place)

def detect_ask_intent(message):
    text = normalize_text(message)
    keywords = {
        "opening_hours": [
            "open", "close", "closing", "timing", "time", "evening", "morning",
            "eppo", "neram", "திறந்த", "நேரம்", "மாலை", "காலை"
        ],
        "nearby_hotels": [
            "hotel", "hotels", "stay", "stays", "lodging", "room", "தங்க", "ஹோட்டல்"
        ],
        "nearby_food": [
            "restaurant", "restaurants", "food", "eat", "cafe", "cafes", "saap", "sapadu", "sappida", "சாப்ப", "உணவு", "ஹோட்டல்"
        ],
        "nearby_shopping": [
            "shopping", "shop", "shops", "market", "mall", "கடை", "ஷாப்பிங்", "சந்தை"
        ],
        "travel_info": [
            "distance", "far", "travel time", "how long", "transport", "reach", "bus", "taxi",
            "evlo distance", "தூரம்", "எவ்வளவு", "எப்படி செல்ல"
        ],
        "activities": [
            "activity", "activities", "what can i do", "do there", "things to do", "enna activities",
            "என்ன செய்ய", "செயல்பாடு"
        ],
        "tips": [
            "tip", "tips", "advice", "carry", "should i", "கவனம்", "ஆலோசனை", "என்ன எடுத்துச்"
        ],
        "nearby_attractions": [
            "nearby", "near by", "what is nearby", "what else", "attractions", "around", "pakkathula",
            "அருகில்", "பக்கத்தில்", "அங்கே", "அந்த இடம்"
        ],
        "place_info": [
            "tell me", "about", "details", "describe", "information", "what is", "பற்றி", "விவரம்"
        ]
    }

    # More specific facility intents must win over generic nearby/place terms.
    intent_order = [
        "opening_hours", "nearby_hotels", "nearby_food", "nearby_shopping",
        "travel_info", "activities", "tips", "nearby_attractions", "place_info"
    ]
    for intent in intent_order:
        if any(keyword in text for keyword in keywords[intent]):
            return intent
    return "unknown"

def get_itinerary_place_names(itinerary):
    names = []
    for item in itinerary or []:
        if isinstance(item, str):
            names.append(item)
        elif isinstance(item, dict) and item.get("name"):
            names.append(item["name"])
    return names

def nearby_facilities(city, place, facility_type):
    origin = (place["lat"], place["lon"])
    matches = [
        facility for facility in NEARBY_PLACES
        if normalize_text(facility["city"]) == normalize_text(city)
        and facility["type"] == facility_type
    ]
    results = []
    for facility in matches:
        result = {
            "name": facility["name"],
            "type": facility["type"],
            "distance": round(haversine(origin[0], origin[1], facility["lat"], facility["lon"]), 1),
            "description": facility["description"],
            "price_level": facility["price_level"]
        }
        results.append(result)
    return sorted(results, key=lambda result: result["distance"])[:3]

def nearby_attractions(city, place):
    attractions = []
    for candidate in PLACES:
        if normalize_text(candidate["city"]) != normalize_text(city):
            continue
        if candidate["name"] == place["name"]:
            continue
        attractions.append({
            "name": candidate["name"],
            "type": "attraction",
            "distance": round(haversine(place["lat"], place["lon"], candidate["lat"], candidate["lon"]), 1),
            "description": candidate["description"],
            "price_level": f"Estimated entry: ₹{candidate['cost']}"
        })
    return sorted(attractions, key=lambda result: result["distance"])[:3]

def ask_suggestions(intent):
    suggestions = {
        "place_info": ["What time does it open?", "What can I do there?", "What are some visitor tips?"],
        "opening_hours": ["What can I do there?", "What places are nearby?"],
        "nearby_hotels": ["Where can I eat nearby?", "How far is it from the next itinerary place?"],
        "nearby_food": ["What hotels are nearby?", "What shopping is nearby?"],
        "nearby_shopping": ["Where can I eat nearby?", "What attractions are nearby?"],
        "nearby_attractions": ["Tell me about the nearest place", "How far is the next place?"],
        "travel_info": ["What transport options are available?", "What places are nearby?"],
        "activities": ["What is the best time to visit?", "What are some visitor tips?"],
        "tips": ["What can I do there?", "What time does it open?"]
    }
    return suggestions.get(intent, [
        "Tell me about this place",
        "What hotels are nearby?",
        "What can I do there?"
    ])

def build_ask_response(message, city, current_place, itinerary):
    intent = detect_ask_intent(message)
    place = resolve_ask_place(city, message, current_place)
    place_name = place["name"] if place else (current_place or "")
    results = []

    if intent == "unknown":
        return {
            "answer": "I can help with place details, opening hours, nearby food, hotels, shopping, transport, activities and travel information.",
            "intent": intent,
            "place": place_name,
            "results": results,
            "suggestions": ask_suggestions(intent)
        }

    if not place:
        return {
            "answer": "Please mention a place or generate a trip first so I can use the right local context.",
            "intent": intent,
            "place": "",
            "results": results,
            "suggestions": ask_suggestions(intent)
        }

    details = PLACE_DETAILS.get(normalize_text(place["name"]), {})
    if intent == "place_info":
        answer = (
            f"{place['name']} is in {place['city']}. {place['description']} "
            f"Demo entry estimate: ₹{place['cost']}. Recommended visit duration: {place['duration']} minutes. "
            f"Best time: {details.get('best_time', 'Daytime, subject to local conditions')}. "
            f"Activities: {', '.join(details.get('activities', []))}. "
            f"Tips: {', '.join(details.get('tips', []))}."
        )
    elif intent == "opening_hours":
        answer = f"{place['name']} has demo opening hours from {place['open']:02d}:00 to {place['close']:02d}:00. Please verify local timings, especially on holidays or festival days."
    elif intent == "activities":
        answer = f"At {place['name']}, you can try: {', '.join(details.get('activities', ['Sightseeing and photography']))}."
    elif intent == "tips":
        answer = f"Visitor tips for {place['name']}: {'; '.join(details.get('tips', ['Check local conditions before visiting']))}."
    elif intent in {"nearby_hotels", "nearby_food", "nearby_shopping"}:
        facility_type = {
            "nearby_hotels": "hotel",
            "nearby_food": "restaurant",
            "nearby_shopping": "shopping"
        }[intent]
        results = nearby_facilities(city, place, facility_type)
        label = {"hotel": "hotel", "restaurant": "food", "shopping": "shopping"}[facility_type]
        answer = f"Here are the nearest demo {label} options around {place['name']}. These are hackathon dataset estimates, not live availability."
        if not results:
            answer = f"I do not have curated demo {label} records near {place['name']} yet."
    elif intent == "nearby_attractions":
        results = nearby_attractions(city, place)
        answer = f"Here are the nearest attractions in the {city} demo dataset to {place['name']}."
    else:
        itinerary_names = get_itinerary_place_names(itinerary)
        next_place = next((find_place(city, name) for name in itinerary_names if name != place["name"]), None)
        if next_place:
            distance = round(haversine(place["lat"], place["lon"], next_place["lat"], next_place["lon"]), 1)
            answer = f"The next itinerary place, {next_place['name']}, is approximately {distance} km from {place['name']}. Travel time depends on traffic and transport mode. Demo transport options include car, bike, bus and walking."
        else:
            center = CITY_COORDS.get(normalize_text(city))
            distance = round(haversine(place["lat"], place["lon"], center[0], center[1]), 1) if center else None
            answer = f"{place['name']} is approximately {distance} km from the {city} city centre. Travel time depends on traffic and transport mode. Demo transport options include car, bike, bus and walking."

    return {
        "answer": answer,
        "intent": intent,
        "place": place_name,
        "results": results[:3],
        "suggestions": ask_suggestions(intent)
    }


@app.route("/api/ask", methods=["POST"])
def ask_nammatrip():
    data = request.get_json(force=True) or {}
    message = str(data.get("message", "")).strip()
    city = str(data.get("city", "Coimbatore")).strip() or "Coimbatore"
    current_place = data.get("current_place", "")
    itinerary = data.get("itinerary", [])

    if not message:
        return jsonify({
            "answer": "Please ask me about a place, opening hours, nearby facilities, activities or travel information.",
            "intent": "unknown",
            "place": current_place if isinstance(current_place, str) else "",
            "results": [],
            "suggestions": ask_suggestions("unknown")
        })

    return jsonify(build_ask_response(message, city, current_place, itinerary))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/places", methods=["GET"])
def places():
    city = request.args.get("city")
    return jsonify({"places": list_places(city)})


def resolve_hidden_gem(city, gem_name):
    city_key = normalize_text(city)
    name_key = normalize_text(gem_name)
    gem = next(
        (
            item for item in HIDDEN_GEMS
            if normalize_text(item["city"]) == city_key
            and normalize_text(item["name"]) == name_key
        ),
        None
    )
    if not gem:
        return None

    existing = next(
        (
            place for place in PLACES
            if normalize_text(place["city"]) == city_key
            and normalize_text(place["name"]) == name_key
        ),
        None
    )
    if existing:
        return existing.copy()

    city_center = CITY_COORDS.get(city_key, CITY_COORDS["coimbatore"])
    return {
        "name": gem["name"],
        "city": gem["city"],
        "category": gem["category"],
        "lat": city_center[0],
        "lon": city_center[1],
        "cost": gem["cost"],
        "duration": 60,
        "open": 6,
        "close": 20,
        "description": gem["description"]
    }


def plan_values(data):
    number_of_persons = max(1, int(data.get("number_of_persons", 1) or 1))
    budget_per_person = float(
        data.get("budget_per_person", data.get("budget", 1500)) or 1500
    )
    total_budget = round(budget_per_person * number_of_persons, 2)
    return number_of_persons, budget_per_person, total_budget


def plan_note(city):
    has_dataset = any(
        place["city"].strip().lower() == city.strip().lower()
        for place in PLACES
    )
    if not has_dataset:
        return (
            f"No tourism dataset is available for {city}. "
            "Try Coimbatore, Chennai, Madurai, Ooty, or Bangalore."
        )
    return (
        "Tourism places use a hackathon demo dataset with estimated costs. "
        "Weather is fetched live when internet is available."
    )


def plan_response(city, itinerary, hidden_gems, spent_per_person,
                  distance, weather, transport, number_of_persons,
                  budget_per_person, total_budget, success=None, message=None):
    total_spent = round(spent_per_person * number_of_persons, 2)
    response = {
        "city": city,
        "itinerary": itinerary,
        "hidden_gems": hidden_gems,
        "spent_per_person": round(spent_per_person, 2),
        "total_spent": total_spent,
        "spent": total_spent,
        "budget_per_person": round(budget_per_person, 2),
        "number_of_persons": number_of_persons,
        "total_budget": round(total_budget, 2),
        "remaining": round(total_budget - total_spent, 2),
        "distance": distance,
        "weather": weather,
        "transport": transport,
        "note": plan_note(city)
    }
    if success is not None:
        response["success"] = success
    if message:
        response["message"] = message
    return response


def request_plan(data, required_places=None):
    city = str(data.get("city", "Coimbatore")).strip() or "Coimbatore"
    number_of_persons, budget_per_person, total_budget = plan_values(data)
    start = parse_time(data.get("start", "10:00"))
    end = parse_time(data.get("end", "19:00"))
    interests = data.get("interests", [])
    transport = data.get("transport", "car")

    coords = geocode_city(city) or CITY_COORDS["coimbatore"]
    weather = get_weather(*coords)
    itinerary, spent_per_person, distance = build_itinerary(
        city,
        total_budget,
        start,
        end,
        interests,
        transport,
        weather,
        required_places=required_places,
        number_of_persons=number_of_persons
    )
    hidden_gems = get_hidden_gems(city, interests, budget_per_person)
    response = plan_response(
        city,
        itinerary,
        hidden_gems,
        spent_per_person,
        distance,
        weather,
        transport,
        number_of_persons,
        budget_per_person,
        total_budget
    )
    response.update({
        "start": data.get("start", "10:00"),
        "end": data.get("end", "19:00"),
        "interests": interests
    })
    return response


@app.route("/api/add-hidden-gem", methods=["POST"])
def add_hidden_gem():
    data = request.get_json(force=True) or {}
    city = str(data.get("city", "Coimbatore")).strip() or "Coimbatore"
    gem_name = str(data.get("hidden_gem", "")).strip()
    existing_itinerary = data.get("itinerary", [])
    existing_names = {
        normalize_text(item if isinstance(item, str) else item.get("name"))
        for item in existing_itinerary
        if item
    }

    if normalize_text(gem_name) in existing_names:
        return jsonify({
            "success": False,
            "message": "Already added to your trip."
        })

    required_place = resolve_hidden_gem(city, gem_name)
    if not required_place:
        return jsonify({
            "success": False,
            "message": "This Hidden Gem is not available for the selected city."
        })

    result = request_plan(data, required_places=[required_place])
    included = any(
        item["name"] == required_place["name"]
        for item in result["itinerary"]
    )
    if not included:
        return jsonify({
            "success": False,
            "message": "This Hidden Gem cannot fit within the selected time and budget."
        })

    result["success"] = True
    return jsonify(result)


@app.route("/api/plan", methods=["POST"])
def plan():
    return jsonify(request_plan(request.get_json(force=True) or {}))

if __name__ == "__main__":
    app.run(debug=True)
