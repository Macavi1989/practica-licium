from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship
from app.core.base import Base
from app.core.fields import field

suggestion_tag_rel = Table(
    "feedback_moderation_suggestion_tag_rel",
    Base.metadata,
    Column("suggestion_id", Integer, ForeignKey("feedback_moderation_suggestion.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("feedback_moderation_tag.id", ondelete="CASCADE"), primary_key=True),
    extend_existing=True,
)


class Tag(Base):
    __tablename__ = "feedback_moderation_tag"
    __abstract__ = False
    __model__ = "tag"
    __service__ = "modules.feedback_moderation.services.feedback.TagService"

    __selector_config__ = {
        "label_field": "name",
        "search_fields": ["name", "slug"],
        "columns": [
            {"field": "name", "label": "Etiqueta"},
            {"field": "color", "label": "Color"},
        ],
    }

    name = field(String(100), required=True, public=True, editable=True,
                 info={"label": {"es": "Nombre", "en": "Name"}})
    slug = field(String(100), required=True, public=True, editable=True,
                 info={"label": {"es": "Slug", "en": "Slug"}})
    color = field(String(20), required=False, public=True, editable=True, default="#808080",
                  info={"label": {"es": "Color", "en": "Color"}})


class Suggestion(Base):
    __tablename__ = "feedback_moderation_suggestion"
    __abstract__ = False
    __model__ = "suggestion"
    __service__ = "modules.feedback_moderation.services.feedback.SuggestionService"

    __selector_config__ = {
        "label_field": "title",
        "search_fields": ["title", "author_email", "author_name"],
        "columns": [
            {"field": "title", "label": "Título"},
            {"field": "status", "label": "Estado"},
            {"field": "author_email", "label": "Autor"},
        ],
    }

    title = field(String(200), required=True, public=True, editable=True,
                  info={"label": {"es": "Título", "en": "Title"}})
    content = field(Text, required=True, public=True, editable=True,
                    info={"label": {"es": "Contenido", "en": "Content"}})
    status = field(
        String(20), required=True, default="pending", public=True, editable=True,
        info={
            "label": {"es": "Estado", "en": "Status"},
            "choices": [
                {"label": "Pendiente", "value": "pending"},
                {"label": "Publicada", "value": "published"},
                {"label": "Rechazada", "value": "rejected"},
                {"label": "Fusionada", "value": "merged"},
            ],
        },
    )
    author_email = field(String(150), required=True, public=True, editable=True,
                         info={"label": {"es": "Email del autor", "en": "Author email"}})
    author_name = field(String(100), required=False, public=True, editable=True,
                        info={"label": {"es": "Nombre del autor", "en": "Author name"}})
    is_public = field(Boolean, required=True, default=False, public=True, editable=True,
                      info={"label": {"es": "Público", "en": "Public"}})
    moderation_note = field(Text, required=False, public=True, editable=True,
                            info={"label": {"es": "Nota de moderación", "en": "Moderation note"}})
    published_at = field(DateTime(timezone=True), required=False, public=True, editable=False,
                         info={"label": {"es": "Publicado el", "en": "Published at"}})


    reviewed_by_id = field(
        UUID(as_uuid=True), ForeignKey("core_user.id"),
        required=False, public=True, editable=True,
        info={"label": {"es": "Revisado por", "en": "Reviewed by"}},
    )
    reviewed_by = relationship(
        "User",
        foreign_keys=lambda: [Suggestion.reviewed_by_id],
        info={"public": True, "recursive": False, "editable": True},
    )


    tags = relationship(
        "modules.feedback_moderation.models.feedback.Tag",
        secondary=suggestion_tag_rel,
        info={"public": True, "editable": True},
    )


class Comment(Base):
    __tablename__ = "feedback_moderation_comment"
    __abstract__ = False
    __model__ = "comment"
    __service__ = "modules.feedback_moderation.services.feedback.CommentService"

    __selector_config__ = {
        "label_field": "id",
        "search_fields": ["author_email", "content"],
        "columns": [
            {"field": "suggestion", "label": "Sugerencia"},
            {"field": "author_email", "label": "Autor"},
            {"field": "status", "label": "Estado"},
        ],
    }


    suggestion_id = field(
        Integer, ForeignKey("feedback_moderation_suggestion.id", ondelete="CASCADE"),
        required=True, public=True, editable=True,
        info={"label": {"es": "Sugerencia", "en": "Suggestion"}},
    )
    suggestion = relationship(
        "modules.feedback_moderation.models.feedback.Suggestion",
        foreign_keys=lambda: [Comment.suggestion_id],
        backref=backref("comments", cascade="all, delete-orphan"),
        info={"public": True, "recursive": False, "editable": True},
    )

    content = field(Text, required=True, public=True, editable=True,
                    info={"label": {"es": "Contenido", "en": "Content"}})
    status = field(
        String(20), required=True, default="pending", public=True, editable=True,
        info={
            "label": {"es": "Estado", "en": "Status"},
            "choices": [
                {"label": "Pendiente", "value": "pending"},
                {"label": "Publicado", "value": "published"},
                {"label": "Rechazado", "value": "rejected"},
            ],
        },
    )
    author_email = field(String(150), required=True, public=True, editable=True,
                         info={"label": {"es": "Email del autor", "en": "Author email"}})
    is_public = field(Boolean, required=True, default=False, public=True, editable=True,
                      info={"label": {"es": "Público", "en": "Public"}})
    published_at = field(DateTime(timezone=True), required=False, public=True, editable=False,
                         info={"label": {"es": "Publicado el", "en": "Published at"}})
