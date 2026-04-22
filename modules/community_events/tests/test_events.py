from __future__ import annotations
import datetime as dt
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest

def make_event_service(model_instance):
    from modules.community_events.services.events import EventService
    service = object.__new__(EventService)
    session = MagicMock()
    session.get.return_value = model_instance
    service.repo = MagicMock()
    service.repo.session = session
    return service


def make_registration_service(model_instance):
    from modules.community_events.services.events import RegistrationService
    service = object.__new__(RegistrationService)
    session = MagicMock()
    session.get.return_value = model_instance
    service.repo = MagicMock()
    service.repo.session = session
    return service

class TestPublishEvent:

    def test_publish_cambia_status(self):
        event = SimpleNamespace(id=1, status="draft", is_public=False)
        service = make_event_service(event)
        with patch("modules.community_events.services.events.serialize", return_value={}):
            service.publish_event(id=1)
        assert event.status == "published"

    def test_publish_hace_publico_el_evento(self):
        event = SimpleNamespace(id=1, status="draft", is_public=False)
        service = make_event_service(event)
        with patch("modules.community_events.services.events.serialize", return_value={}):
            service.publish_event(id=1)
        assert event.is_public is True

    def test_publish_not_found(self):
        from fastapi import HTTPException
        service = make_event_service(None)
        with pytest.raises(HTTPException) as exc:
            service.publish_event(id=999)
        assert exc.value.status_code == 404

class TestCancelEvent:

    def test_cancel_cambia_status(self):
        event = SimpleNamespace(id=2, status="published", is_public=True)
        service = make_event_service(event)
        with patch("modules.community_events.services.events.serialize", return_value={}):
            service.cancel_event(id=2, reason="Lluvia extrema")
        assert event.status == "cancelled"

    def test_cancel_oculta_el_evento(self):
        event = SimpleNamespace(id=2, status="published", is_public=True)
        service = make_event_service(event)
        with patch("modules.community_events.services.events.serialize", return_value={}):
            service.cancel_event(id=2, reason="Lluvia extrema")
        assert event.is_public is False

    def test_cancel_not_found(self):
        from fastapi import HTTPException
        service = make_event_service(None)
        with pytest.raises(HTTPException) as exc:
            service.cancel_event(id=999, reason="No existe")
        assert exc.value.status_code == 404

class TestCheckin:

    def test_checkin_guarda_fecha(self):
        reg = SimpleNamespace(id=10, status="confirmed", checkin_at=None, notes="")
        service = make_registration_service(reg)
        with patch("modules.community_events.services.events.serialize", return_value={}):
            service.checkin(id=10, source="scanner")
        assert reg.checkin_at is not None

    def test_checkin_funciona_con_pending(self):
        reg = SimpleNamespace(id=11, status="pending", checkin_at=None, notes="")
        service = make_registration_service(reg)
        with patch("modules.community_events.services.events.serialize", return_value={}):
            service.checkin(id=11)
        assert reg.checkin_at is not None

    def test_checkin_falla_con_cancelled(self):
        from fastapi import HTTPException
        reg = SimpleNamespace(id=12, status="cancelled", checkin_at=None, notes="")
        service = make_registration_service(reg)
        with pytest.raises(HTTPException) as exc:
            service.checkin(id=12)
        assert exc.value.status_code == 400
        assert "confirmados" in exc.value.detail

    def test_checkin_not_found(self):
        from fastapi import HTTPException
        service = make_registration_service(None)
        with pytest.raises(HTTPException) as exc:
            service.checkin(id=999)
        assert exc.value.status_code == 404

