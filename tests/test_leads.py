import json
import sqlite3
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.main import app


def _lead(**overrides: object) -> dict:
    body: dict = {
        "name": "Ana Perez",
        "email": "ana@example.com",
        "phone": "+54 11 5555-5555",
        "project_type_id": "landing",
        "entity_id": "pyme",
        "service_ids": ["diseno", "seo"],
        "payment_method_id": "transferencia",
        "discount_code": None,
    }
    body.update(overrides)
    return body


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "leads.db"))
    with TestClient(app) as test_client:
        yield test_client


def _read_rows(db_path) -> list[dict]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in conn.execute("SELECT * FROM leads ORDER BY id")]
    finally:
        conn.close()


def test_create_lead_happy_path(client, tmp_path) -> None:
    response = client.post("/leads", json=_lead())

    assert response.status_code == 201
    data = response.json()
    assert isinstance(data["id"], int)
    assert data["name"] == "Ana Perez"
    assert data["email"] == "ana@example.com"
    assert data["total"] == pytest.approx(1100.0)
    created_at = datetime.fromisoformat(data["created_at"])
    assert created_at.tzinfo is not None

    rows = _read_rows(tmp_path / "leads.db")
    assert len(rows) == 1
    row = rows[0]
    assert row["id"] == data["id"]
    assert row["name"] == "Ana Perez"
    assert row["email"] == "ana@example.com"
    assert row["phone"] == "+54 11 5555-5555"
    assert row["project_type_id"] == "landing"
    assert row["entity_id"] == "pyme"
    assert json.loads(row["service_ids"]) == ["diseno", "seo"]
    assert row["payment_method_id"] == "transferencia"
    assert row["discount_code"] is None
    assert row["subtotal"] == pytest.approx(1100.0)
    assert row["discount_amount"] == pytest.approx(0.0)
    assert row["total"] == pytest.approx(1100.0)


def test_create_lead_total_matches_quote(client) -> None:
    quote = client.post(
        "/quote",
        json={
            "project_type_id": "landing",
            "entity_id": "pyme",
            "service_ids": ["diseno", "seo"],
            "discount_code": None,
        },
    ).json()

    response = client.post("/leads", json=_lead())
    assert response.status_code == 201
    assert response.json()["total"] == pytest.approx(quote["total"])


def test_create_lead_optional_phone_null(client, tmp_path) -> None:
    response = client.post("/leads", json=_lead(phone=None))
    assert response.status_code == 201
    row = _read_rows(tmp_path / "leads.db")[0]
    assert row["phone"] is None


def test_create_lead_empty_services(client, tmp_path) -> None:
    response = client.post("/leads", json=_lead(service_ids=[]))

    assert response.status_code == 201
    assert response.json()["total"] == pytest.approx(550.0)
    row = _read_rows(tmp_path / "leads.db")[0]
    assert row["subtotal"] == pytest.approx(550.0)
    assert json.loads(row["service_ids"]) == []


def test_create_lead_applies_valid_discount(client, tmp_path) -> None:
    response = client.post("/leads", json=_lead(discount_code="LANZAMIENTO10"))

    assert response.status_code == 201
    assert response.json()["total"] == pytest.approx(990.0)
    row = _read_rows(tmp_path / "leads.db")[0]
    assert row["discount_code"] == "LANZAMIENTO10"
    assert row["discount_amount"] == pytest.approx(110.0)
    assert row["total"] == pytest.approx(990.0)


def test_create_lead_null_discount_means_no_discount(client) -> None:
    response = client.post("/leads", json=_lead(discount_code=None))
    assert response.status_code == 201
    assert response.json()["total"] == pytest.approx(1100.0)


def test_create_lead_empty_string_discount_means_no_discount(client, tmp_path) -> None:
    response = client.post("/leads", json=_lead(discount_code=""))
    assert response.status_code == 201
    assert response.json()["total"] == pytest.approx(1100.0)
    row = _read_rows(tmp_path / "leads.db")[0]
    assert row["discount_amount"] == pytest.approx(0.0)


def test_create_lead_missing_name_returns_422(client) -> None:
    body = _lead()
    del body["name"]
    response = client.post("/leads", json=body)
    assert response.status_code == 422


def test_create_lead_invalid_email_returns_422(client) -> None:
    response = client.post("/leads", json=_lead(email="no-es-un-email"))
    assert response.status_code == 422


def test_create_lead_name_too_short_returns_422(client) -> None:
    response = client.post("/leads", json=_lead(name="A"))
    assert response.status_code == 422


def test_create_lead_phone_too_long_returns_422(client) -> None:
    response = client.post("/leads", json=_lead(phone="9" * 31))
    assert response.status_code == 422


def test_create_lead_unknown_project_type_returns_404(client) -> None:
    response = client.post("/leads", json=_lead(project_type_id="no-existe"))
    assert response.status_code == 404
    assert "detail" in response.json()


def test_create_lead_unknown_payment_method_returns_404(client) -> None:
    response = client.post("/leads", json=_lead(payment_method_id="no-existe"))
    assert response.status_code == 404
    assert "detail" in response.json()


def test_create_lead_unknown_service_returns_404(client) -> None:
    response = client.post("/leads", json=_lead(service_ids=["diseno", "no-existe"]))
    assert response.status_code == 404
    assert "detail" in response.json()


def test_create_lead_unknown_discount_returns_422(client) -> None:
    response = client.post("/leads", json=_lead(discount_code="NOEXISTE"))
    assert response.status_code == 422
    assert "detail" in response.json()


def test_create_lead_persists_two_rows_with_distinct_ids(client, tmp_path) -> None:
    first = client.post("/leads", json=_lead(name="Primero"))
    second = client.post("/leads", json=_lead(name="Segundo", service_ids=[]))

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] != second.json()["id"]

    rows = _read_rows(tmp_path / "leads.db")
    assert len(rows) == 2
    assert rows[0]["name"] == "Primero"
    assert rows[1]["name"] == "Segundo"
    assert rows[1]["subtotal"] == pytest.approx(550.0)


def test_leads_read_is_not_exposed(client) -> None:
    response = client.get("/leads")
    assert response.status_code in (404, 405)
