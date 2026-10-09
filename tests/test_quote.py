import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _quote(**overrides: object) -> dict:
    body: dict = {
        "project_type_id": "landing",
        "entity_id": "pyme",
        "service_ids": [],
        "discount_code": None,
    }
    body.update(overrides)
    return body


def test_quote_typical_no_discount() -> None:
    response = client.post("/quote", json=_quote(service_ids=["diseno", "seo"]))
    assert response.status_code == 200
    data = response.json()
    # landing 500.0 * pyme 1.1 = 550.0 ; services 300.0 + 250.0 = 550.0
    assert data["subtotal"] == pytest.approx(1100.0)
    assert data["discount_percent"] == 0.0
    assert data["discount_amount"] == 0.0
    assert data["total"] == pytest.approx(1100.0)
    assert data["breakdown"]["project_type"]["price"] == pytest.approx(500.0)
    assert data["breakdown"]["project_type"]["name"]
    assert data["breakdown"]["entity_multiplier"] == pytest.approx(1.1)
    services = data["breakdown"]["services"]
    assert len(services) == 2
    assert [s["price"] for s in services] == pytest.approx([300.0, 250.0])
    assert all(s["name"] for s in services)


def test_quote_with_discount_code_applies() -> None:
    response = client.post(
        "/quote",
        json=_quote(service_ids=["diseno", "seo"], discount_code="LANZAMIENTO10"),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["subtotal"] == pytest.approx(1100.0)
    assert data["discount_percent"] == pytest.approx(10.0)
    assert data["discount_amount"] == pytest.approx(110.0)
    assert data["total"] == pytest.approx(990.0)


def test_quote_discount_applies_only_when_code_matches() -> None:
    response = client.post(
        "/quote",
        json=_quote(service_ids=["diseno"], discount_code="lanzamiento10"),
    )
    assert response.status_code == 422
    assert "detail" in response.json()


def test_quote_empty_services_is_ok() -> None:
    response = client.post("/quote", json=_quote(service_ids=[]))
    assert response.status_code == 200
    data = response.json()
    assert data["subtotal"] == pytest.approx(550.0)
    assert data["breakdown"]["services"] == []


def test_quote_integer_prices_stay_exact_floats() -> None:
    # landing base 500.0 + local 1.0 -> 500.0, sin error de redondeo
    response = client.post("/quote", json=_quote(entity_id="local", service_ids=[]))
    assert response.status_code == 200
    data = response.json()
    assert data["subtotal"] == 500.0
    assert data["total"] == 500.0
    assert isinstance(data["breakdown"]["entity_multiplier"], float)


def test_quote_discount_code_null_means_no_discount() -> None:
    response = client.post("/quote", json=_quote(discount_code=None))
    assert response.status_code == 200
    data = response.json()
    assert data["discount_percent"] == 0.0
    assert data["discount_amount"] == 0.0


def test_quote_discount_code_empty_string_means_no_discount() -> None:
    response = client.post("/quote", json=_quote(discount_code=""))
    assert response.status_code == 200
    data = response.json()
    assert data["discount_percent"] == 0.0
    assert data["discount_amount"] == 0.0


def test_quote_entity_id_is_case_sensitive() -> None:
    response = client.post("/quote", json=_quote(entity_id="PYME"))
    assert response.status_code == 404
    assert "detail" in response.json()


def test_quote_unknown_project_type_returns_404() -> None:
    response = client.post("/quote", json=_quote(project_type_id="no-existe"))
    assert response.status_code == 404
    assert "detail" in response.json()


def test_quote_unknown_entity_returns_404() -> None:
    response = client.post("/quote", json=_quote(entity_id="no-existe"))
    assert response.status_code == 404
    assert "detail" in response.json()


def test_quote_unknown_service_returns_404() -> None:
    response = client.post("/quote", json=_quote(service_ids=["diseno", "no-existe"]))
    assert response.status_code == 404
    assert "detail" in response.json()


def test_quote_unknown_discount_code_returns_422() -> None:
    response = client.post("/quote", json=_quote(discount_code="NOEXISTE"))
    assert response.status_code == 422
    assert "detail" in response.json()


def test_quote_invalid_body_returns_422() -> None:
    response = client.post("/quote", json={"project_type_id": "landing"})
    assert response.status_code == 422
    assert "detail" in response.json()
