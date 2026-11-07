"""City Book.

This program knows each city and where it sits on the map.
It does not know the weather. The Sky Report does that job.
"""

import json
import logging
import os
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

logging.basicConfig(level=logging.INFO, format="%(message)s")

DEFAULT_CITIES = [
    {
        "id": "lagos",
        "name": "Lagos",
        "country": "Nigeria",
        "latitude": 6.5244,
        "longitude": 3.3792,
    },
    {
        "id": "london",
        "name": "London",
        "country": "United Kingdom",
        "latitude": 51.5074,
        "longitude": -0.1278,
    },
    {
        "id": "new-york",
        "name": "New York",
        "country": "United States",
        "latitude": 40.7128,
        "longitude": -74.0060,
    },
    {
        "id": "tokyo",
        "name": "Tokyo",
        "country": "Japan",
        "latitude": 35.6762,
        "longitude": 139.6503,
    },
    {
        "id": "nairobi",
        "name": "Nairobi",
        "country": "Kenya",
        "latitude": -1.2921,
        "longitude": 36.8219,
    },
    {
        "id": "paris",
        "name": "Paris",
        "country": "France",
        "latitude": 48.8566,
        "longitude": 2.3522,
    },
]


class City(BaseModel):
    id: str = Field(min_length=1, max_length=40, pattern=r"^[a-z0-9-]+$")
    name: str = Field(min_length=1, max_length=80)
    country: str = Field(min_length=1, max_length=80)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


app = FastAPI(title="City Book", version="1.0.0")


def cities_path() -> Path:
    return Path(os.environ.get("CITIES_PATH", "/config/cities.json"))


def load_cities() -> list[City]:
    """Read the city file. If the file is missing, use the built-in list."""
    path = cities_path()
    if not path.is_file():
        return [City(**item) for item in DEFAULT_CITIES]

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail="The city list file is not valid. Check the commas and quotes.",
        ) from exc

    if not isinstance(raw, list):
        raise HTTPException(
            status_code=500,
            detail="The city list file must be a list of cities.",
        )

    try:
        cities = [City(**item) for item in raw]
    except (TypeError, ValidationError) as exc:
        raise HTTPException(
            status_code=500,
            detail="The city list file is not valid. Check the commas and quotes.",
        ) from exc

    seen: set[str] = set()
    for city in cities:
        if city.id in seen:
            raise HTTPException(
                status_code=500,
                detail=f"Two cities use the id {city.id}. Each id must be used once.",
            )
        seen.add(city.id)
    return sorted(cities, key=lambda city: city.name.lower())


@app.exception_handler(RequestValidationError)
def bad_input(_request, _exc) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": "Check the city id. Use a small id like lagos."},
    )


@app.middleware("http")
async def log_request(request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    if request.url.path != "/health":
        logging.info(
            json.dumps(
                {
                    "service": "locations",
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
    return {"status": "ok", "service": "locations"}


@app.get("/cities", response_model=list[City])
def list_cities() -> list[City]:
    return load_cities()


@app.get("/cities/{city_id}", response_model=City)
def get_city(city_id: str) -> City:
    for city in load_cities():
        if city.id == city_id:
            return city
    raise HTTPException(status_code=404, detail="That city is not in the city book.")
