"""Catálogo de opciones del wizard de cotización.

Datos estáticos en Python (sin DB todavía): el hito de contactos es el que
introduce SQLite. El frontend consume este catálogo vía GET /catalog.
"""

from typing import Any

CATALOG: dict[str, list[dict[str, Any]]] = {
    "project_types": [
        {
            "id": "landing",
            "name": "Landing Page",
            "base_price": 500.0,
            "description": "Página de aterrizaje de una sola vista, ideal para campañas.",
        },
        {
            "id": "tienda",
            "name": "Tienda Online",
            "base_price": 1500.0,
            "description": "E-commerce con carrito, catálogo y gestión de productos.",
        },
        {
            "id": "blog",
            "name": "Blog",
            "base_price": 800.0,
            "description": "Sitio de contenidos con artículos, categorías y buscador.",
        },
        {
            "id": "corporativa",
            "name": "Web Corporativa",
            "base_price": 2000.0,
            "description": "Sitio multi-sección para empresas con servicios y contacto.",
        },
        {
            "id": "institucional",
            "name": "Web Institucional",
            "base_price": 1200.0,
            "description": "Sitio institucional para organismos, entidades y ONGs.",
        },
    ],
    "entities": [
        {
            "id": "organizacion",
            "name": "Organización",
            "multiplier": 1.5,
        },
        {
            "id": "empresa",
            "name": "Empresa",
            "multiplier": 1.3,
        },
        {
            "id": "comercio",
            "name": "Comercio",
            "multiplier": 1.2,
        },
        {
            "id": "local",
            "name": "Local",
            "multiplier": 1.0,
        },
        {
            "id": "pyme",
            "name": "PyME",
            "multiplier": 1.1,
        },
    ],
    "services": [
        {
            "id": "diseno",
            "name": "Diseño UX/UI",
            "price": 300.0,
            "description": "Diseño de interfaz y experiencia a medida.",
        },
        {
            "id": "seo",
            "name": "SEO",
            "price": 250.0,
            "description": "Optimización para motores de búsqueda.",
        },
        {
            "id": "mantenimiento",
            "name": "Mantenimiento",
            "price": 150.0,
            "description": "Mantenimiento y actualizaciones periódicas.",
        },
        {
            "id": "integracion_pagos",
            "name": "Integración de Pagos",
            "price": 400.0,
            "description": "Integración de pasarela de pagos online.",
        },
        {
            "id": "redaccion",
            "name": "Redacción de Contenidos",
            "price": 200.0,
            "description": "Redacción de textos y contenidos del sitio.",
        },
        {
            "id": "dominio_hosting",
            "name": "Dominio + Hosting",
            "price": 120.0,
            "description": "Registro de dominio y hosting por un año.",
        },
    ],
    "payment_methods": [
        {"id": "transferencia", "name": "Transferencia bancaria"},
        {"id": "mercado_pago", "name": "Mercado Pago"},
        {"id": "tarjeta", "name": "Tarjeta de crédito/débito"},
        {"id": "efectivo", "name": "Efectivo"},
        {"id": "cuota", "name": "Pago en cuotas"},
    ],
    "discounts": [
        {
            "id": "lanzamiento",
            "name": "Descuento de Lanzamiento",
            "percent": 10.0,
            "description": "10% off por lanzamiento.",
            "code": "LANZAMIENTO10",
        },
        {
            "id": "referido",
            "name": "Descuento por Referido",
            "percent": 15.0,
            "description": "15% off para clientes referidos.",
            "code": "REFERIDO15",
        },
        {
            "id": "paquete_completo",
            "name": "Paquete Completo",
            "percent": 20.0,
            "description": "20% off al contratar el paquete completo.",
            "code": "PACK20",
        },
    ],
}
