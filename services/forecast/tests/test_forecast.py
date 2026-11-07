from datetime import date

from fastapi.testclient import TestClient

from forecast import CONDITIONS, app, build_forecast, feels_like

client = TestClient(app)
DAY = date(2026, 11, 7)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "forecast"


def test_lagos_is_warmer_than_london() -> None:
    lagos = build_forecast(6.5244, 3.3792, "Lagos", DAY)
    london = build_forecast(51.5074, -0.1278, "London", DAY)
    assert lagos.temperature_c > london.temperature_c
    assert lagos.feels == feels_like(lagos.temperature_c)


def test_same_input_same_sky() -> None:
    first = build_forecast(6.5244, 3.3792, "Lagos", DAY)
    second = build_forecast(6.5244, 3.3792, "Lagos", DAY)
    assert first == second
    assert first.condition in CONDITIONS
    assert 0 <= first.humidity_percent <= 100
    assert first.wind_kph >= 0
    assert first.summary.endswith(".")


def test_equator_is_hot() -> None:
    sky = build_forecast(0.0, 0.0, "Equator", DAY)
    assert sky.temperature_c >= 28
    assert sky.feels == "Hot"


def test_route_uses_the_date_you_send() -> None:
    response = client.get(
        "/forecast",
        params={"lat": 6.52, "lon": 3.38, "city": "Lagos", "on": "2026-11-07"},
    )
    assert response.status_code == 200
    assert response.json()["date"] == "2026-11-07"


def test_bad_date() -> None:
    response = client.get(
        "/forecast",
        params={"lat": 6.52, "lon": 3.38, "city": "Lagos", "on": "tomorrow"},
    )
    assert response.status_code == 400
    assert "2026-11-07" in response.json()["detail"]
