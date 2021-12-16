from marshmallow import Schema, fields


__all__ = ["KeyFull", "SingleKey", "KeyToken"]


class SingleKey(Schema):
    desc = fields.String()
    date_created = fields.DateTime()
    has_api_key = fields.Boolean()
    has_archive = fields.Boolean()
    has_broadcast = fields.Boolean()
    has_host = fields.Boolean()
    has_prompt = fields.Boolean()
    has_settings = fields.Boolean()
    has_subscription = fields.Boolean()


class KeyToken(Schema):
    token = fields.UUID()


class KeyFull(KeyToken, SingleKey):
    ...
