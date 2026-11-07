import json
from pathlib import Path

from fastapi.testclient import TestClient

from locations import DEFAULT_CITIES, City, app

client = TestClient(app)
ROOT = Path(__file__).resolve().parents[3]


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "locations"


def test_built_in_list_includes_lagos(monkeypatch) -> None:
    monkeypatch.setenv("CITIES_PATH", "/no/such/cities.json")
    response = client.get("/cities")
    assert response.status_code == 200
    ids = {city["id"] for city in response.json()}
    assert "lagos" in ids
    assert len(response.json()) == len(DEFAULT_CITIES)


def test_one_city(monkeypatch) -> None:
    monkeypatch.setenv("CITIES_PATH", "/no/such/cities.json")
    response = client.get("/cities/lagos")
    assert response.status_code == 200
    assert response.json()["name"] == "Lagos"
    assert response.json()["country"] == "Nigeria"


def test_missing_city(monkeypatch) -> None:
    monkeypatch.setenv("CITIES_PATH", "/no/such/cities.json")
    response = client.get("/cities/accra")
    assert response.status_code == 404
    assert "not in the city book" in response.json()["detail"]


def test_bad_json_is_a_clear_error(tmp_path, monkeypatch) -> None:
    bad = tmp_path / "cities.json"
    bad.write_text("{ not json", encoding="utf-8")
    monkeypatch.setenv("CITIES_PATH", str(bad))
    response = client.get("/cities")
    assert response.status_code == 500
    assert "not valid" in response.json()["detail"]


def test_duplicate_id_is_a_clear_error(tmp_path, monkeypatch) -> None:
    cities = [dict(DEFAULT_CITIES[0]), dict(DEFAULT_CITIES[0])]
    path = tmp_path / "cities.json"
    path.write_text(json.dumps(cities), encoding="utf-8")
    monkeypatch.setenv("CITIES_PATH", str(path))
    response = client.get("/cities")
    assert response.status_code == 500
    assert "lagos" in response.json()["detail"]


def test_deploy_file_matches_the_shape() -> None:
    raw = json.loads((ROOT / "deploy" / "cities.json").read_text(encoding="utf-8"))
    cities = [City(**item) for item in raw]
    assert any(city.id == "lagos" for city in cities)
