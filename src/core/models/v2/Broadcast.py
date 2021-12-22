from marshmallow import Schema, fields


__all__ = ["BroadcastDate"]


class BroadcastDate(Schema):
    date = fields.Date(required=True)
    which = fields.Integer(missing=-1)
