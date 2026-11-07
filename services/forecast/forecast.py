"""Sky Report.

This program builds a practice forecast from a map spot and a date.
It does not call a real weather company. The number stays the same
all day for the same city, which makes the class easy to follow.
"""

import hashlib
import json
import logging
import math
import time
from datetime import date, datetime, timezone

from fastapi import FastAPI, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format="%(message)s")

CONDITIONS = ("Sunny", "Cloudy", "Rain", "Windy", "Storms")
SUMMARIES = {
    "Sunny": "The sun is out. It feels bright.",
    "Cloudy": "Clouds cover the sky.",
    "Rain": "Take a coat. Rain is in the sky.",
    "Windy": "The wind is strong. Hold your hat.",
    "Storms": "A storm is near. Stay inside.",
}


class Forecast(BaseModel):
    city: str
    date: str
    temperature_c: int
    feels: str
    condition: str
    humidity_percent: int = Field(ge=0, le=100)
    wind_kph: int = Field(ge=0, le=200)
    summary: str


app = FastAPI(title="Sky Report", version="1.0.0")


def pick_number(seed: str, low: int, high: int) -> int:
    """Pick a steady number in the range. The same seed always returns the same number."""
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    span = high - low + 1
    return low + (int(digest[:8], 16) % span)


def feels_like(temp_c: int) -> str:
    if temp_c >= 30:
        return "Hot"
    if temp_c >= 22:
        return "Warm"
    if temp_c >= 12:
        return "Mild"
    if temp_c >= 5:
        return "Cool"
    return "Cold"


def temperature_c(lat: float, lon: float, on: date) -> int:
    """Warm near the equator. Cooler toward the poles. A small swing by day of year."""
    day_of_year = on.timetuple().tm_yday
    seasonal = 6.0 * math.cos((day_of_year - 20) * 2.0 * math.pi / 365.0)
    wobble = (abs(lon) * 10) % 5 - 2
    raw = 32.0 - (abs(lat) * 0.42) + seasonal + wobble
    return int(round(raw))


def build_forecast(lat: float, lon: float, city: str, on: date) -> Forecast:
    condition = CONDITIONS[
        pick_number(f"{city.strip().lower()}|{on.isoformat()}", 0, len(CONDITIONS) - 1)
    ]
    humidity = pick_number(f"humidity|{city}|{on.isoformat()}", 35, 80)
    wind = pick_number(f"wind|{city}|{on.isoformat()}", 6, 24)

    if condition == "Sunny":
        humidity = min(humidity, 55)
    elif condition == "Rain":
        humidity = max(humidity, 68)
    elif condition == "Windy":
        wind = max(wind, 32)
    elif condition == "Storms":
        humidity = max(humidity, 78)
        wind = max(wind, 28)

    temp = temperature_c(lat, lon, on)
    return Forecast(
        city=city,
        date=on.isoformat(),
        temperature_c=temp,
        feels=feels_like(temp),
        condition=condition,
        humidity_percent=humidity,
        wind_kph=wind,
        summary=SUMMARIES[condition],
    )


def parse_day(raw: str | None) -> date:
    if raw is None or raw == "":
        return datetime.now(timezone.utc).date()
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Use a date like 2026-11-07.",
        ) from exc


@app.exception_handler(RequestValidationError)
def bad_input(_request, _exc) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": "Check the map numbers. Latitude and longitude must be valid."},
    )


@app.middleware("http")
async def log_request(request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    if request.url.path != "/health":
        logging.info(
            json.dumps(
                {
                    "service": "forecast",
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code,
                    "ms": round((time.perf_counter() - started) * 1000, 1),
                }
            )
        )
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "forecast"}


@app.get("/forecast", response_model=Forecast)
def forecast(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    city: str = Query(..., min_length=1, max_length=80),
    on: str | None = Query(default=None, max_length=10),
) -> Forecast:
    return build_forecast(lat, lon, city, parse_day(on))
