from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.catalog import CATALOG
from app.db import init_db
from app.leads import LeadRequest, create_lead
from app.quote import UnknownDiscountError, UnknownReferenceError, build_quote


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(title="Portfolio Builder API", lifespan=lifespan)


class QuoteRequest(BaseModel):
    project_type_id: str
    entity_id: str
    service_ids: list[str]
    discount_code: str | None = None


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/catalog")
def get_catalog() -> dict[str, Any]:
    return CATALOG


@app.post("/quote")
def create_quote(payload: QuoteRequest) -> dict[str, Any]:
    try:
        return build_quote(
            project_type_id=payload.project_type_id,
            entity_id=payload.entity_id,
            service_ids=payload.service_ids,
            discount_code=payload.discount_code,
            catalog=CATALOG,
        )
    except UnknownReferenceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except UnknownDiscountError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/leads", status_code=201)
def create_lead_endpoint(payload: LeadRequest) -> dict[str, Any]:
    try:
        return create_lead(payload, CATALOG)
    except UnknownReferenceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except UnknownDiscountError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
