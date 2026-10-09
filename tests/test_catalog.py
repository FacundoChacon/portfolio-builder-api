from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_catalog_returns_200() -> None:
    response = client.get("/catalog")
    assert response.status_code == 200


def test_catalog_has_all_required_sections() -> None:
    data = client.get("/catalog").json()
    assert set(data) == {
        "project_types",
        "entities",
        "services",
        "payment_methods",
        "discounts",
    }
    for section in data.values():
        assert isinstance(section, list)
        assert len(section) > 0


def test_catalog_project_types_shape_and_ids() -> None:
    data = client.get("/catalog").json()
    ids = [pt["id"] for pt in data["project_types"]]
    assert ids == ["landing", "tienda", "blog", "corporativa", "institucional"]
    for pt in data["project_types"]:
        assert set(pt) == {"id", "name", "base_price", "description"}
        assert isinstance(pt["base_price"], float)
        assert pt["name"]
        assert pt["description"]


def test_catalog_entities_shape_and_ids() -> None:
    data = client.get("/catalog").json()
    ids = [e["id"] for e in data["entities"]]
    assert ids == ["organizacion", "empresa", "comercio", "local", "pyme"]
    for entity in data["entities"]:
        assert set(entity) == {"id", "name", "multiplier"}
        assert isinstance(entity["multiplier"], float)
        assert entity["multiplier"] > 0


def test_catalog_services_shape_and_ids() -> None:
    data = client.get("/catalog").json()
    ids = [s["id"] for s in data["services"]]
    assert ids == [
        "diseno",
        "seo",
        "mantenimiento",
        "integracion_pagos",
        "redaccion",
        "dominio_hosting",
    ]
    for service in data["services"]:
        assert set(service) == {"id", "name", "price", "description"}
        assert isinstance(service["price"], float)
        assert service["price"] > 0


def test_catalog_payment_methods_shape_and_ids() -> None:
    data = client.get("/catalog").json()
    ids = [p["id"] for p in data["payment_methods"]]
    assert ids == ["transferencia", "mercado_pago", "tarjeta", "efectivo", "cuota"]
    for payment in data["payment_methods"]:
        assert set(payment) == {"id", "name"}
        assert payment["name"]


def test_catalog_discounts_shape_and_codes() -> None:
    data = client.get("/catalog").json()
    ids = [d["id"] for d in data["discounts"]]
    assert ids == ["lanzamiento", "referido", "paquete_completo"]
    for discount in data["discounts"]:
        assert set(discount) == {"id", "name", "percent", "description", "code"}
        assert isinstance(discount["percent"], float)
        assert 0 < discount["percent"] < 100
        assert discount["code"]
