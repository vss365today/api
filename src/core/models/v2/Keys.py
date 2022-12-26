from marshmallow import Schema, fields


__all__ = ["Key", "Permissions", "Token"]


class Permissions(Schema):
    desc = fields.String()
    date_created = fields.DateTime(dump_only=True)
    has_archive = fields.Boolean()
    has_broadcast = fields.Boolean()
    has_host = fields.Boolean()
    has_keys = fields.Boolean()
    has_prompt = fields.Boolean()
    has_settings = fields.Boolean()
    has_subscription = fields.Boolean()


class Token(Schema):
    token = fields.String(max=64)


class Key(Token, Permissions):
    ...
