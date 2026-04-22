from __future__ import annotations
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship
from app.core.base import Base
from app.core.fields import field

class Event(Base):
    __tablename__ = "community_events_event"
    __abstract__ = False
    __model__ = "event"
    __service__ = "modules.community_events.services.events.EventService"

    __selector_config__ = {
        "label_field": "title",
        "search_fields": ["title", "slug", "location"],
        "columns": [
            {"field": "title", "label": "Título"},
            {"field": "status", "label": "Estado"},
            {"field": "start_at", "label": "Inicio"},
        ],
    }

    title = field(String(200), required=True, public=True, editable=True,
                  info={"label": {"es": "Título del evento", "en": "Event title"}})
    slug = field(String(200), required=True, public=True, editable=True,
                 info={"label": {"es": "Enlace", "en": "Slug"}})
    summary = field(String(500), required=False, public=True, editable=True,
                    info={"label": {"es": "Resumen", "en": "Summary"}})
    description = field(Text, required=False, public=True, editable=True,
                        info={"label": {"es": "Descripción", "en": "Description"}})
    status = field(
        String(20), required=True, default="draft", public=True, editable=True,
        info={
            "label": {"es": "Estado", "en": "Status"},
            "choices": [
                {"label": "Borrador", "value": "draft"},
                {"label": "Publicado", "value": "published"},
                {"label": "Cerrado", "value": "closed"},
                {"label": "Cancelado", "value": "cancelled"},
            ],
        },
    )
    start_at = field(DateTime(timezone=True), required=True, public=True, editable=True,
                     info={"label": {"es": "Comienzo", "en": "Start at"}})
    end_at = field(DateTime(timezone=True), required=True, public=True, editable=True,
                   info={"label": {"es": "Termina", "en": "End at"}})
    location = field(String(255), required=False, public=True, editable=True,
                     info={"label": {"es": "Localización", "en": "Location"}})
    capacity_total = field(Integer, required=True, default=0, public=True, editable=True,
                           info={"label": {"es": "Capacidad total", "en": "Total capacity"}})
    is_public = field(Boolean, required=True, default=False, public=True, editable=True,
                      info={"label": {"es": "Evento público", "en": "Public event"}})

    organizer_user_id = field(
        UUID(as_uuid=True), ForeignKey("core_user.id"),
        required=False, public=True, editable=True,
        info={"label": {"es": "Organizado por", "en": "Organizer"}},
    )
    organizer_user = relationship(
        "User",
        foreign_keys=lambda: [Event.organizer_user_id],
        info={"public": True, "recursive": False, "editable": True},
    )

    sessions = relationship(
        "modules.community_events.models.events.Session",
        cascade="all, delete-orphan",
        info={"public": True, "recursive": False, "editable": False},
    )
    registrations = relationship(
        "modules.community_events.models.events.Registration",
        cascade="all, delete-orphan",
        info={"public": True, "recursive": False, "editable": False},
    )

class Session(Base):
    __tablename__ = "community_events_session"
    __abstract__ = False
    __model__ = "session"
    __service__ = "modules.community_events.services.events.SessionService"

    __selector_config__ = {
        "label_field": "title",
        "search_fields": ["title", "speaker_name", "room"],
        "columns": [
            {"field": "title", "label": "Sesión"},
            {"field": "speaker_name", "label": "Ponente"},
            {"field": "start_at", "label": "Inicio"},
        ],
    }

    event_id = field(
        Integer, ForeignKey("community_events_event.id", ondelete="CASCADE"),
        required=True, public=True, editable=True,
        info={"label": {"es": "Evento", "en": "Event"}},
    )
    event = relationship(
    "modules.community_events.models.events.Event",
    foreign_keys=lambda: [Session.event_id],
    overlaps="sessions",
    info={"public": True, "recursive": False, "editable": True},
)
    title = field(String(200), required=True, public=True, editable=True,
                  info={"label": {"es": "Título", "en": "Title"}})
    start_at = field(DateTime(timezone=True), required=True, public=True, editable=True,
                     info={"label": {"es": "Inicio", "en": "Start at"}})
    end_at = field(DateTime(timezone=True), required=True, public=True, editable=True,
                   info={"label": {"es": "Fin", "en": "End at"}})
    speaker_name = field(String(150), required=False, public=True, editable=True,
                         info={"label": {"es": "Ponente", "en": "Speaker"}})
    room = field(String(100), required=False, public=True, editable=True,
                 info={"label": {"es": "Sala", "en": "Room"}})
    capacity = field(Integer, required=False, public=True, editable=True,
                     info={"label": {"es": "Capacidad", "en": "Capacity"}})
    status = field(String(20), required=True, default="active", public=True, editable=True,
                   info={"label": {"es": "Estado", "en": "Status"}})

class Registration(Base):
    __tablename__ = "community_events_registration"
    __abstract__ = False
    __model__ = "registration"
    __service__ = "modules.community_events.services.events.RegistrationService"

    __selector_config__ = {
        "label_field": "attendee_name",
        "search_fields": ["attendee_name", "attendee_email"],
        "columns": [
            {"field": "attendee_name", "label": "Asistente"},
            {"field": "attendee_email", "label": "Email"},
            {"field": "status", "label": "Estado"},
        ],
    }

    event_id = field(
        Integer, ForeignKey("community_events_event.id", ondelete="CASCADE"),
        required=True, public=True, editable=True,
        info={"label": {"es": "Evento", "en": "Event"}},
    )
    event = relationship(
    "modules.community_events.models.events.Event",
    foreign_keys=lambda: [Registration.event_id],
    overlaps="registrations",
    info={"public": True, "recursive": False, "editable": True},
)
    session_id = field(
        Integer, ForeignKey("community_events_session.id", ondelete="SET NULL"),
        required=False, public=True, editable=True,
        info={"label": {"es": "Sesión", "en": "Session"}},
    )
    session = relationship(
        "modules.community_events.models.events.Session",
        foreign_keys=lambda: [Registration.session_id],
        info={"public": True, "recursive": False, "editable": True},
    )
    attendee_name = field(String(150), required=True, public=True, editable=True,
                          info={"label": {"es": "Nombre asistente", "en": "Attendee name"}})
    attendee_email = field(String(150), required=True, public=True, editable=True,
                           info={"label": {"es": "Email asistente", "en": "Attendee email"}})
    attendee_user_id = field(
        UUID(as_uuid=True), ForeignKey("core_user.id", ondelete="SET NULL"),
        required=False, public=True, editable=True,
        info={"label": {"es": "Usuario", "en": "User"}},
    )
    attendee_user = relationship(
        "User",
        foreign_keys=lambda: [Registration.attendee_user_id],
        info={"public": True, "recursive": False, "editable": True},
    )
    status = field(
        String(20), required=True, default="pending", public=True, editable=True,
        info={
            "label": {"es": "Estado", "en": "Status"},
            "choices": [
                {"label": "Pendiente", "value": "pending"},
                {"label": "Confirmado", "value": "confirmed"},
                {"label": "Lista de Espera", "value": "waitlist"},
                {"label": "Cancelado", "value": "cancelled"},
            ],
        },
    )
    registered_at = field(DateTime(timezone=True), required=False, public=True, editable=False,
                          info={"label": {"es": "Registrado el", "en": "Registered at"}})
    checkin_at = field(DateTime(timezone=True), required=False, public=True, editable=False,
                       info={"label": {"es": "Check-in el", "en": "Checkin at"}})
    notes = field(Text, required=False, public=True, editable=True,
                  info={"label": {"es": "Notas", "en": "Notes"}})