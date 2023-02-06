from marshmallow import Schema, fields

from src.core.models.v2 import Hosts


__all__ = ["Prompt", "PromptDate", "PromptId"]


class Media(Schema):
    alt_text = fields.String(required=True, allow_none=True)
    media = fields.String(required=True, allow_none=True)
    replace = fields.Boolean(required=True, allow_none=True, load_only=True)


class Navigation(Schema):
    next = fields.String(allow_none=True)
    previous = fields.String(allow_none=True)


class Prompt(Schema):
    _id = fields.Integer(strict=True, dump_only=True)
    content = fields.String(required=True)
    date = fields.Date("iso", required=True)
    date_added = fields.DateTime("iso", dump_only=True)
    host = fields.Nested(Hosts.Basic, dump_only=True)
    host_handle = fields.String(required=True, load_only=True)
    is_duplicate = fields.Boolean(missing=None, allow_None=True, load_only=True)
    media = fields.List(fields.Nested(Media, missing=None), dump_only=True)
    navigation = fields.Nested(Navigation, missing=None, dump_only=True)
    twitter_id = fields.String(required=True)
    url = fields.String(dump_only=True)
    word = fields.String(required=True)


class PromptDate(Schema):
    date = fields.Date("iso", required=True)


class PromptId(Schema):
    id = fields.Integer(strict=True, required=True)
