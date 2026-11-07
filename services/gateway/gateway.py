"""Front Desk.

The web page talks only to this program.
This program asks the City Book for the city, then the Sky Report for the sky.
"""

import json
import logging
import os
import re
import time

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO, format="%(message)s")

CITY_ID = re.compile(r"^[a-z0-9-]{1,40}$")
HELPER_DOWN = (
    "A helper program did not answer. "
    "In Argo CD, check that every box is green."
)

app = FastAPI(title="Front Desk", version="1.0.0")


def service_url(name: str, fallback: str) -> str:
    return os.environ.get(name, fallback).rstrip("/")


def get_json(url: str, params: dict | None = None) -> httpx.Response:
    try:
        with httpx.Client(timeout=3.0) as client:
            return client.get(url, params=params)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=HELPER_DOWN) from exc


def detail_from(response: httpx.Response, fallback: str) -> str:
    try:
        body = response.json()
    except json.JSONDecodeError:
        return fallback
    detail = body.get("detail", fallback)
    if isinstance(detail, str) and detail.strip():
        return detail
    return fallback


@app.exception_handler(RequestValidationError)
def bad_input(_request, _exc) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": "Use a city id like lagos."},
    )


@app.middleware("http")
async def log_request(request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    if request.url.path != "/health":
        logging.info(
            json.dumps(
                {
                    "service": "gateway",
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
    return {"status": "ok", "service": "gateway"}


@app.get("/cities")
def cities() -> list:
    url = service_url("LOCATIONS_URL", "http://127.0.0.1:8001") + "/cities"
    response = get_json(url)
    if response.status_code != 200:
        raise HTTPException(
            status_code=502 if response.status_code >= 500 else response.status_code,
            detail=detail_from(response, "The City Book had a problem."),
        )
    return response.json()


@app.get("/weather")
def weather(city: str = Query(..., min_length=1, max_length=40)) -> dict:
    if CITY_ID.fullmatch(city) is None:
        raise HTTPException(status_code=400, detail="Use a city id like lagos.")

    locations = service_url("LOCATIONS_URL", "http://127.0.0.1:8001")
    forecast = service_url("FORECAST_URL", "http://127.0.0.1:8002")

    city_response = get_json(f"{locations}/cities/{city}")
    if city_response.status_code == 404:
        raise HTTPException(status_code=404, detail="That city is not in the city book.")
    if city_response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=detail_from(city_response, "The City Book had a problem."),
        )

    found = city_response.json()
    sky_response = get_json(
        f"{forecast}/forecast",
        params={
            "lat": found["latitude"],
            "lon": found["longitude"],
            "city": found["name"],
        },
    )
    if sky_response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=detail_from(sky_response, "The Sky Report had a problem."),
        )

    return {"city": found, "forecast": sky_response.json()}
