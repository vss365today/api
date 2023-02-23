from marshmallow import Schema, fields

from src.core.models.v2 import Hosts


__all__ = [
    "Media",
    "MediaId",
    "MediaItems",
    "Prompt",
    "PromptDate",
    "PromptId",
    "PromptUpdate",
]


class Media(Schema):
    _id = fields.Integer(strict=True, dump_only=True)
    alt_text = fields.String(required=True, allow_none=True)
    media = fields.String(required=True, allow_none=True, dump_only=True)
    url = fields.Url(required=True, load_only=True)


class MediaId(Schema):
    media_id = fields.Integer(strict=True, required=True)


class MediaItems(Schema):
    items = fields.List(fields.Nested(Media))


class Navigation(Schema):
    next = fields.Date(allow_none=True)
    previous = fields.Date(allow_none=True)


class Prompt(Schema):
    # "Standard" fields
    content = fields.String(required=True)
    date = fields.Date("iso", required=True)
    twitter_id = fields.String(required=True)
    word = fields.String(required=True)

    # Fields that are only present in Prompt creation
    host_handle = fields.String(required=True, load_only=True)
    is_additional = fields.Boolean(missing=False, load_only=True)

    # Fields that are only present in Prompt fetching
    _id = fields.Integer(strict=True, dump_only=True)
    date_added = fields.DateTime("iso", dump_only=True)
    host = fields.Nested(Hosts.Basic, dump_only=True)
    media = fields.List(fields.Nested(Media), allow_none=True, dump_only=True)
    navigation = fields.Nested(Navigation, dump_only=True)
    url = fields.String(dump_only=True)


class PromptUpdate(Schema):
    content = fields.String()
    date = fields.Date("iso")
    host_handle = fields.String()
    word = fields.String()


class PromptDate(Schema):
    date = fields.Date("iso", required=True)


class PromptId(Schema):
    id = fields.Integer(strict=True, required=True)
