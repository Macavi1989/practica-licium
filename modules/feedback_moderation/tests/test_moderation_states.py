from __future__ import annotations

import datetime as dt
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest


def make_suggestion_service(model_instance):

    from modules.feedback_moderation.services.feedback import SuggestionService
    service = object.__new__(SuggestionService)
    session = MagicMock()
    session.get.return_value = model_instance
    service.repo = MagicMock()
    service.repo.session = session
    return service


def make_comment_service(model_instance):

    from modules.feedback_moderation.services.feedback import CommentService
    service = object.__new__(CommentService)
    session = MagicMock()
    session.get.return_value = model_instance
    service.repo = MagicMock()
    service.repo.session = session
    return service


class TestCreate:

    def test_create_fuerza_estado_pending(self):
        from modules.feedback_moderation.services.feedback import SuggestionService
        service = object.__new__(SuggestionService)
        service.repo = MagicMock()

        with patch.object(SuggestionService, '__bases__', ()):
            pass

        payload = {"title": "Añadir modo oscuro", "content": "Sería genial.", "is_public": True}

        with patch("app.core.base.BaseService.create", side_effect=lambda x: x):
            result = service.create(payload)

        assert result["status"] == "pending"
        assert result["is_public"] is False

class TestPublish:

    def test_publish_cambia_status(self):
        suggestion = SimpleNamespace(
            id=1, status="pending", is_public=False,
            moderation_note=None, published_at=None, reviewed_by_id=None
        )
        service = make_suggestion_service(suggestion)

        with patch("modules.feedback_moderation.services.feedback.get_current_user_id", return_value="uuid-mod"):
            with patch("modules.feedback_moderation.services.feedback.serialize", return_value={}):
                service.publish(id=1)

        assert suggestion.status == "published"

    def test_publish_hace_publica_la_sugerencia(self):
        suggestion = SimpleNamespace(
            id=1, status="pending", is_public=False,
            moderation_note=None, published_at=None, reviewed_by_id=None
        )
        service = make_suggestion_service(suggestion)

        with patch("modules.feedback_moderation.services.feedback.get_current_user_id", return_value="uuid-mod"):
            with patch("modules.feedback_moderation.services.feedback.serialize", return_value={}):
                service.publish(id=1)

        assert suggestion.is_public is True

    def test_publish_guarda_nota(self):
        suggestion = SimpleNamespace(
            id=1, status="pending", is_public=False,
            moderation_note=None, published_at=None, reviewed_by_id=None
        )
        service = make_suggestion_service(suggestion)

        with patch("modules.feedback_moderation.services.feedback.get_current_user_id", return_value="uuid-mod"):
            with patch("modules.feedback_moderation.services.feedback.serialize", return_value={}):
                service.publish(id=1, note="Aprobado por moderación")

        assert suggestion.moderation_note == "Aprobado por moderación"

    def test_publish_not_found(self):
        from fastapi import HTTPException
        service = make_suggestion_service(None)

        with patch("modules.feedback_moderation.services.feedback.get_current_user_id", return_value="uuid-mod"):
            with pytest.raises(HTTPException) as exc:
                service.publish(id=999)

        assert exc.value.status_code == 404

class TestReject:

    def test_reject_cambia_status(self):
        suggestion = SimpleNamespace(
            id=2, status="pending", is_public=False,
            moderation_note=None, reviewed_by_id=None
        )
        service = make_suggestion_service(suggestion)

        with patch("modules.feedback_moderation.services.feedback.get_current_user_id", return_value="uuid-mod"):
            with patch("modules.feedback_moderation.services.feedback.serialize", return_value={}):
                service.reject(id=2, note="No es viable")

        assert suggestion.status == "rejected"

    def test_reject_mantiene_privada(self):
        suggestion = SimpleNamespace(
            id=2, status="pending", is_public=False,
            moderation_note=None, reviewed_by_id=None
        )
        service = make_suggestion_service(suggestion)

        with patch("modules.feedback_moderation.services.feedback.get_current_user_id", return_value="uuid-mod"):
            with patch("modules.feedback_moderation.services.feedback.serialize", return_value={}):
                service.reject(id=2, note="No es viable")

        assert suggestion.is_public is False

    def test_reject_not_found(self):
        from fastapi import HTTPException
        service = make_suggestion_service(None)

        with patch("modules.feedback_moderation.services.feedback.get_current_user_id", return_value="uuid-mod"):
            with pytest.raises(HTTPException) as exc:
                service.reject(id=999, note="No existe")

        assert exc.value.status_code == 404

class TestMerge:

    def test_merge_falla_si_mismo_id(self):
        from fastapi import HTTPException
        service = make_suggestion_service(None)

        with pytest.raises(HTTPException) as exc:
            service.merge(id=5, target_id=5)

        assert exc.value.status_code == 400
        assert "fusionar consigo misma" in exc.value.detail

    def test_merge_cambia_status_a_merged(self):
        source = SimpleNamespace(
            id=1, status="pending", is_public=False, moderation_note=None
        )
        target = SimpleNamespace(id=2, status="pending")

        service = make_suggestion_service(source)
        service.repo.session.get.side_effect = lambda model, id: source if id == 1 else target

        with patch("modules.feedback_moderation.services.feedback.serialize", return_value={}):
            service.merge(id=1, target_id=2)

        assert source.status == "merged"
