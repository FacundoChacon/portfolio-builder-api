"""Persistencia del lead de contacto.

El servidor recalcula el presupuesto con build_quote(...) (fuente de verdad):
el cliente nunca envía ni influye en el total. Se guarda un snapshot completo
del lead y su desglose de precios en SQLite.
"""

import json
import re
from contextlib import closing
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.db import get_connection
from app.quote import Catalog, UnknownReferenceError, build_quote

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

_INSERT_LEAD = """
INSERT INTO leads (
    created_at, name, email, phone,
    project_type_id, entity_id, service_ids,
    payment_method_id, discount_code,
    subtotal, discount_amount, total
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


class LeadRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(max_length=254)
    phone: str | None = Field(default=None, max_length=30)
    project_type_id: str
    entity_id: str
    service_ids: list[str]
    payment_method_id: str
    discount_code: str | None = None

    @field_validator("email")
    @classmethod
    def _email_must_be_valid(cls, value: str) -> str:
        if not _EMAIL_RE.match(value):
            raise ValueError("email inválido")
        return value


def _payment_method_exists(catalog: Catalog, payment_method_id: str) -> bool:
    return any(
        payment_method["id"] == payment_method_id
        for payment_method in catalog["payment_methods"]
    )


def _insert_lead(
    *,
    created_at: str,
    payload: LeadRequest,
    quote: dict[str, Any],
) -> int:
    values = (
        created_at,
        payload.name,
        payload.email,
        payload.phone,
        payload.project_type_id,
        payload.entity_id,
        json.dumps(payload.service_ids),
        payload.payment_method_id,
        payload.discount_code or None,
        quote["subtotal"],
        quote["discount_amount"],
        quote["total"],
    )
    with closing(get_connection()) as connection, connection:
        cursor = connection.execute(_INSERT_LEAD, values)
        return int(cursor.lastrowid)


def create_lead(payload: LeadRequest, catalog: Catalog) -> dict[str, Any]:
    quote = build_quote(
        project_type_id=payload.project_type_id,
        entity_id=payload.entity_id,
        service_ids=payload.service_ids,
        discount_code=payload.discount_code,
        catalog=catalog,
    )

    if not _payment_method_exists(catalog, payload.payment_method_id):
        raise UnknownReferenceError(
            f"payment_method_id desconocido: {payload.payment_method_id!r}"
        )

    created_at = datetime.now(timezone.utc).isoformat()
    lead_id = _insert_lead(created_at=created_at, payload=payload, quote=quote)

    return {
        "id": lead_id,
        "created_at": created_at,
        "name": payload.name,
        "email": payload.email,
        "total": quote["total"],
    }
