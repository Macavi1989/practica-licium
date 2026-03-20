from __future__ import annotations
import datetime as dt
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest


def make_service(model_instance):
    from modules.practice_checklist.services.checklist import PracticeChecklistService
    service = object.__new__(PracticeChecklistService)
    session = MagicMock()
    session.get.return_value = model_instance
    service.repo = MagicMock()
    service.repo.session = session
    return service


def make_item_service(item_instance):
    from modules.practice_checklist.services.checklist import PracticeChecklistItemService
    service = object.__new__(PracticeChecklistItemService)
    session = MagicMock()
    session.get.return_value = item_instance
    service.repo = MagicMock()
    service.repo.session = session
    return service


# ── Tests: close() ────────────────────────────────────────────────────────────

class TestClose:

    def test_close_cambia_status(self):
        checklist = SimpleNamespace(
            id=1, name="Test", status="open", is_public=False, description=""
        )
        service = make_service(checklist)

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={}):
            service.close(id=1)

        assert checklist.status == "closed"

    def test_close_guarda_closed_at(self):
        checklist = SimpleNamespace(
            id=1, name="Test", status="open", is_public=False, description=""
        )
        service = make_service(checklist)

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={}):
            service.close(id=1)

        assert checklist.closed_at is not None
        assert isinstance(checklist.closed_at, dt.datetime)

    def test_close_con_nota(self):
        checklist = SimpleNamespace(
            id=1, name="Test", status="open", is_public=False, description="Descripción original"
        )
        service = make_service(checklist)

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={}):
            service.close(id=1, close_note="Cerrado por vacaciones")

        assert "Cerrado por vacaciones" in checklist.description

    def test_close_make_public(self):
        checklist = SimpleNamespace(
            id=1, name="Test", status="open", is_public=False, description=""
        )
        service = make_service(checklist)

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={}):
            service.close(id=1, make_public=True)

        assert checklist.is_public is True

    def test_close_not_found(self):
        from fastapi import HTTPException
        service = make_service(None)

        with pytest.raises(HTTPException) as exc:
            service.close(id=999)

        assert exc.value.status_code == 404


class TestReopen:

    def test_reopen_cambia_status(self):
        checklist = SimpleNamespace(
            id=1, status="closed", closed_at=dt.datetime.now(dt.timezone.utc)
        )
        service = make_service(checklist)

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={}):
            service.reopen(id=1)

        assert checklist.status == "open"

    def test_reopen_borra_closed_at(self):
        checklist = SimpleNamespace(
            id=1, status="closed", closed_at=dt.datetime.now(dt.timezone.utc)
        )
        service = make_service(checklist)

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={}):
            service.reopen(id=1)

        assert checklist.closed_at is None

    def test_reopen_not_found(self):
        from fastapi import HTTPException
        service = make_service(None)

        with pytest.raises(HTTPException) as exc:
            service.reopen(id=999)

        assert exc.value.status_code == 404

class TestSetDone:

    def test_set_done_marca_hecho(self):
        item = SimpleNamespace(id=1, title="Tarea", is_done=False, done_at=None, note="")
        service = make_item_service(item)

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={}):
            service.set_done(id=1, done=True)

        assert item.is_done is True

    def test_set_done_guarda_done_at(self):
        item = SimpleNamespace(id=1, title="Tarea", is_done=False, done_at=None, note="")
        service = make_item_service(item)

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={}):
            service.set_done(id=1, done=True)

        assert item.done_at is not None

    def test_set_done_false_borra_done_at(self):
        item = SimpleNamespace(
            id=1, title="Tarea", is_done=True,
            done_at=dt.datetime.now(dt.timezone.utc), note=""
        )
        service = make_item_service(item)

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={}):
            service.set_done(id=1, done=False)

        assert item.is_done is False
        assert item.done_at is None

    def test_set_done_con_nota(self):
        item = SimpleNamespace(id=1, title="Tarea", is_done=False, done_at=None, note="")
        service = make_item_service(item)

        with patch("modules.practice_checklist.services.checklist.serialize", return_value={}):
            service.set_done(id=1, done=True, note="Revisado por Ana")

        assert "Revisado por Ana" in item.note

    def test_set_done_not_found(self):
        from fastapi import HTTPException
        service = make_item_service(None)

        with pytest.raises(HTTPException) as exc:
            service.set_done(id=999)

        assert exc.value.status_code == 404