import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables
load_dotenv()
OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")

# Fixed PM2.5 parameter ID
PARAMETER_ID = 2


def get_city_coordinates(city, country=None):
    """Fetch bounding box coordinates for a city using Nominatim."""
    try:
        query = f"{city}, {country}" if country else city
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json"
        resp = requests.get(url, headers={"User-Agent": "AI-Agent/1.0"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if not data:
            return {"status": "error", "message": f"City '{city}' not found."}

        if country:
            for entry in data:
                if country.lower() in entry["display_name"].lower():
                    return {"status": "ok", "boundingbox": entry["boundingbox"]}

        return {"status": "ok", "boundingbox": data[0]["boundingbox"]}

    except Exception as e:
        return {"status": "error", "message": f"Error fetching city coordinates: {e}"}


def get_active_station(city, country, parameter_id=PARAMETER_ID):
    """Find the most recent active OpenAQ station for a city."""
    coords = get_city_coordinates(city, country)
    if coords.get("status") == "error":
        return coords

    bbox = coords["boundingbox"]
    aq_url = (
        f"https://api.openaq.org/v3/locations?"
        f"bbox={bbox[2]},{bbox[0]},{bbox[3]},{bbox[1]}"
        f"&limit=100&parameters_id={parameter_id}"
    )

    try:
        headers = {"X-API-Key": OPENAQ_API_KEY} if OPENAQ_API_KEY else {}
        resp = requests.get(aq_url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])
        if not results:
            return {"status": "error", "message": f"No active stations found for {city}."}

        # Sort by datetimeLast (most recent)
        results.sort(
            key=lambda s: s.get("datetimeLast", {}).get("utc", ""),
            reverse=True,
        )

        return {"status": "ok", "station": results[0]}

    except Exception as e:
        return {"status": "error", "message": f"Error fetching active station: {e}"}


def get_latest_value_from_sensor(station, parameter_id=PARAMETER_ID):
    """Get the latest PM2.5 measurement from a given station."""
    try:
        sensors = station.get("sensors", [])
        sensor = next((s for s in sensors if s["parameter"]["id"] == parameter_id), None)
        if not sensor:
            return {"status": "error", "message": "No PM2.5 sensor found."}

        sensor_id = sensor["id"]
        url = f"https://api.openaq.org/v3/sensors/{sensor_id}"
        headers = {"X-API-Key": OPENAQ_API_KEY} if OPENAQ_API_KEY else {}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        return {"status": "ok", "data": data}

    except Exception as e:
        return {"status": "error", "message": f"Error fetching sensor data: {e}"}


def get_air_quality(city: str, country: str | None = None) -> dict:
    """
    Main OpenAQ function for AI use.
    Returns structured PM2.5 data that the model can interpret itself.
    """
    try:
        station_info = get_active_station(city, country)
        if station_info.get("status") == "error":
            return station_info

        station = station_info["station"]
        sensor_data = get_latest_value_from_sensor(station)
        if sensor_data.get("status") == "error":
            return sensor_data

        data = sensor_data["data"]
        if not data.get("results"):
            return {"status": "error", "message": "No sensor data available."}

        result = data["results"][0]
        latest = result.get("latest", {})
        pm25 = latest.get("value")

        if pm25 is None:
            return {"status": "error", "message": "No PM2.5 reading available."}

        timestamp = latest.get("datetime", {}).get("utc", datetime.now(timezone.utc).isoformat())

        return {
            "status": "ok",
            "city": city,
            "country": country,
            "pm25": pm25,
            "unit": result.get("parameter", {}).get("units", "µg/m³"),
            "timestamp": timestamp,
            "note": (
                "This is the latest PM2.5 concentration from OpenAQ. "
                "The AI agent should interpret this value and describe the air quality meaningfully."
            ),
        }

    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {e}"}


def get_historical_average(city: str, country: str | None = None) -> dict:
    """
    Fetch yearly historical average PM2.5 for a city from OpenAQ.
    """
    try:
        # Get the best station
        station_info = get_active_station(city, country, parameter_id=PARAMETER_ID)
        if station_info.get("status") == "error":
            return station_info

        station = station_info["station"]

        # Find PM2.5 sensor
        sensors = station.get("sensors", [])
        sensor = next((s for s in sensors if s["parameter"]["id"] == PARAMETER_ID), None)
        if not sensor:
            return {"status": "error", "message": "No PM2.5 sensor found at this station."}

        sensor_id = sensor["id"]
        url = f"https://api.openaq.org/v3/sensors/{sensor_id}/years?limit=100"
        headers = {"X-API-Key": OPENAQ_API_KEY} if OPENAQ_API_KEY else {}

        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if not data.get("results"):
            return {"status": "error", "message": f"No historical data found for {city}."}

        # Build yearly average structure
        events = []
        for result in data["results"]:
            events.append({
                "year": result.get("year"),
                "average_value": result.get("average"),
                "unit": result.get("parameter", {}).get("units", "µg/m³"),
                "summary": result.get("summary")
            })

        return {
            "status": "ok",
            "city": city,
            "country": country,
            "parameter": "PM2.5",
            "events": events,
            "note": "This is historical yearly average PM2.5 from OpenAQ. The AI can interpret this data to provide trends or insights."
        }

    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {e}"}
