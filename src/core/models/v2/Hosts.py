from marshmallow import Schema, fields


__all__ = ["Basic", "Delete"]


class Basic(Schema):
    uid = fields.String()
    handle = fields.String()


class Delete(Schema):
    handle = fields.String(required=True)
