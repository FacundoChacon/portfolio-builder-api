"""Motor de cotización.

Lógica pura (sin HTTP ni DB): recibe ids + catálogo y devuelve el desglose.
Los errores de dominio se exponen como excepciones para que la capa HTTP
decida el status (404 para referencias, 422 para descuento inexistente).

Reglas de cálculo (fijas):
    subtotal = base_price * entity_multiplier + suma(services)
    discount = subtotal * discount_percent / 100  (solo si el code coincide)
    total    = subtotal - discount
"""

from typing import Any

Catalog = dict[str, list[dict[str, Any]]]


class UnknownReferenceError(Exception):
    """project_type_id, entity_id o algún service_id no existe en el catálogo."""


class UnknownDiscountError(Exception):
    """El discount_code fue provisto pero no existe en el catálogo."""


def _index(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in items}


def build_quote(
    project_type_id: str,
    entity_id: str,
    service_ids: list[str],
    discount_code: str | None,
    catalog: Catalog,
) -> dict[str, Any]:
    project_types = _index(catalog["project_types"])
    entities = _index(catalog["entities"])
    services = _index(catalog["services"])
    discounts = {discount["code"]: discount for discount in catalog["discounts"]}

    project_type = project_types.get(project_type_id)
    if project_type is None:
        raise UnknownReferenceError(f"project_type_id desconocido: {project_type_id!r}")

    entity = entities.get(entity_id)
    if entity is None:
        raise UnknownReferenceError(f"entity_id desconocido: {entity_id!r}")

    selected_services: list[dict[str, Any]] = []
    for service_id in service_ids:
        service = services.get(service_id)
        if service is None:
            raise UnknownReferenceError(f"service_id desconocido: {service_id!r}")
        selected_services.append(service)

    discount_percent = 0.0
    if discount_code:
        discount = discounts.get(discount_code)
        if discount is None:
            raise UnknownDiscountError(f"discount_code desconocido: {discount_code!r}")
        discount_percent = float(discount["percent"])

    base_price = float(project_type["base_price"])
    entity_multiplier = float(entity["multiplier"])
    services_total = sum(float(service["price"]) for service in selected_services)

    subtotal = base_price * entity_multiplier + services_total
    discount_amount = subtotal * discount_percent / 100.0
    total = subtotal - discount_amount

    return {
        "subtotal": subtotal,
        "discount_percent": discount_percent,
        "discount_amount": discount_amount,
        "total": total,
        "breakdown": {
            "project_type": {"name": project_type["name"], "price": base_price},
            "entity_multiplier": entity_multiplier,
            "services": [
                {"name": service["name"], "price": float(service["price"])}
                for service in selected_services
            ],
        },
    }
