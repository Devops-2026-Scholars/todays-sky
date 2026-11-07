import httpx
from fastapi.testclient import TestClient

import gateway
from gateway import app

client = TestClient(app)

LAGOS = {
    "id": "lagos",
    "name": "Lagos",
    "country": "Nigeria",
    "latitude": 6.5244,
    "longitude": 3.3792,
}
SKY = {
    "city": "Lagos",
    "date": "2026-11-07",
    "temperature_c": 31,
    "feels": "Hot",
    "condition": "Sunny",
    "humidity_percent": 50,
    "wind_kph": 12,
    "summary": "The sun is out. It feels bright.",
}


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "gateway"


def test_weather_joins_city_and_sky(monkeypatch) -> None:
    def fake(url: str, params=None):
        if url.endswith("/cities/lagos"):
            return httpx.Response(200, json=LAGOS)
        if url.endswith("/forecast"):
            assert params["city"] == "Lagos"
            return httpx.Response(200, json=SKY)
        raise AssertionError(url)

    monkeypatch.setattr(gateway, "get_json", fake)
    response = client.get("/weather", params={"city": "lagos"})
    assert response.status_code == 200
    body = response.json()
    assert body["city"]["name"] == "Lagos"
    assert body["forecast"]["temperature_c"] == 31


def test_unknown_city(monkeypatch) -> None:
    def fake(url: str, params=None):
        return httpx.Response(404, json={"detail": "That city is not in the city book."})

    monkeypatch.setattr(gateway, "get_json", fake)
    response = client.get("/weather", params={"city": "accra"})
    assert response.status_code == 404


def test_bad_id_never_calls_helpers(monkeypatch) -> None:
    def fake(url: str, params=None):
        raise AssertionError("helper should not be called")

    monkeypatch.setattr(gateway, "get_json", fake)
    response = client.get("/weather", params={"city": "Lagos"})
    assert response.status_code == 400
    assert "lagos" in response.json()["detail"]


def test_helper_down(monkeypatch) -> None:
    monkeypatch.setenv("LOCATIONS_URL", "http://127.0.0.1:9")
    response = client.get("/cities")
    assert response.status_code == 502
    assert "did not answer" in response.json()["detail"]
