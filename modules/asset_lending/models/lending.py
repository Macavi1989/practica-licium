from __future__ import annotations

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship
from app.core.base import Base
from app.core.fields import field


class Location(Base):
    __tablename__ = "asset_lending_location"
    __abstract__ = False
    __model__ = "location"
    __service__ = "modules.asset_lending.services.lending.LocationService"

    __selector_config__ = {
        "label_field": "name",
        "search_fields": ["name", "code"],
        "columns": [
            {"field": "name", "label": "Nombre"},
            {"field": "code", "label": "Código"},
        ],
    }

    name = field(String(100), required=True, public=True, editable=True,
                 info={"label": {"es": "Nombre", "en": "Name"}})
    code = field(String(20), required=True, public=True, editable=True,
                 info={"label": {"es": "Código", "en": "Code"}})
    is_active = field(Boolean, default=True, required=True, public=True, editable=True,
                      info={"label": {"es": "Activo", "en": "Active"}})


class Asset(Base):
    __tablename__ = "asset_lending_asset"
    __abstract__ = False
    __model__ = "asset"
    __service__ = "modules.asset_lending.services.lending.AssetService"

    __selector_config__ = {
        "label_field": "name",
        "search_fields": ["name", "asset_code"],
        "columns": [
            {"field": "name", "label": "Recurso"},
            {"field": "asset_code", "label": "Código"},
            {"field": "status", "label": "Estado"},
        ],
    }

    name = field(String(180), required=True, public=True, editable=True,
                 info={"label": {"es": "Nombre", "en": "Name"}})
    asset_code = field(String(50), required=True, public=True, editable=True,
                       info={"label": {"es": "Código", "en": "Code"}})
    status = field(
        String(20), required=True, default="available", public=True, editable=True,
        info={
            "label": {"es": "Estado", "en": "Status"},
            "choices": [
                {"label": "Disponible", "value": "available"},
                {"label": "Prestado", "value": "loaned"},
                {"label": "Mantenimiento", "value": "maintenance"},
            ],
        },
    )
    location_id = field(
        Integer, ForeignKey("asset_lending_location.id"),
        required=True, public=True, editable=True,
        info={"label": {"es": "Ubicación", "en": "Location"}},
    )
    location = relationship(
        "modules.asset_lending.models.lending.Location",
        foreign_keys=lambda: [Asset.location_id],
        backref=backref("assets"),
        info={"public": True, "recursive": False, "editable": True},
    )
    responsible_user_id = field(
        UUID(as_uuid=True), ForeignKey("core_user.id"),
        required=False, public=True, editable=True,
        info={"label": {"es": "Responsable", "en": "Responsible"}},
    )
    responsible_user = relationship(
        "User",
        foreign_keys=lambda: [Asset.responsible_user_id],
        info={"public": True, "recursive": False, "editable": True},
    )
    notes = field(Text, required=False, public=True, editable=True,
                  info={"label": {"es": "Notas", "en": "Notes"}})


class Loan(Base):
    __tablename__ = "asset_lending_loan"
    __abstract__ = False
    __model__ = "loan"
    __service__ = "modules.asset_lending.services.lending.AssetLoanService"

    __selector_config__ = {
        "label_field": "id",
        "search_fields": [],
        "columns": [
            {"field": "asset", "label": "Recurso"},
            {"field": "status", "label": "Estado"},
            {"field": "due_at", "label": "Devolución"},
        ],
    }

    asset_id = field(
        Integer, ForeignKey("asset_lending_asset.id"),
        required=True, public=True, editable=True,
        info={"label": {"es": "Recurso", "en": "Asset"}},
    )
    asset = relationship(
        "modules.asset_lending.models.lending.Asset",
        foreign_keys=lambda: [Loan.asset_id],
        backref=backref("loans"),
        info={"public": True, "recursive": False, "editable": True},
    )
    borrower_user_id = field(
        UUID(as_uuid=True), ForeignKey("core_user.id"),
        required=True, public=True, editable=True,
        info={"label": {"es": "Prestatario", "en": "Borrower"}},
    )
    borrower_user = relationship(
        "User",
        foreign_keys=lambda: [Loan.borrower_user_id],
        info={"public": True, "recursive": False, "editable": True},
    )
    checkout_at = field(DateTime(timezone=True), required=False, public=True, editable=False,
                        info={"label": {"es": "Fecha de salida", "en": "Checkout at"}})
    due_at = field(DateTime(timezone=True), required=True, public=True, editable=True,
                   info={"label": {"es": "Fecha de devolución", "en": "Due at"}})
    returned_at = field(DateTime(timezone=True), required=False, public=True, editable=False,
                        info={"label": {"es": "Devuelto el", "en": "Returned at"}})
    status = field(
        String(20), required=True, default="open", public=True, editable=True,
        info={
            "label": {"es": "Estado", "en": "Status"},
            "choices": [
                {"label": "Abierto", "value": "open"},
                {"label": "Devuelto", "value": "returned"},
                {"label": "Atrasado", "value": "overdue"},
            ],
        },
    )
    checkout_note = field(Text, required=False, public=True, editable=True,
                          info={"label": {"es": "Nota de salida", "en": "Checkout note"}})
    return_note = field(Text, required=False, public=True, editable=True,
                        info={"label": {"es": "Nota de devolución", "en": "Return note"}})