from marshmallow import Schema, fields, validate


__all__ = ["Key", "Permissions", "Token"]


class Permissions(Schema):
    desc = fields.String()
    date_created = fields.DateTime(dump_only=True)
    has_archive = fields.Boolean()
    has_notifications = fields.Boolean()
    has_hosts = fields.Boolean()
    has_keys = fields.Boolean()
    has_prompts = fields.Boolean()
    has_settings = fields.Boolean()
    has_emails = fields.Boolean()


class Token(Schema):
    token = fields.String(validate=validate.Length(equal=64))


class Key(Token, Permissions):
    ...
