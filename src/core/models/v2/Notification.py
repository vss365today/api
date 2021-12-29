from marshmallow import Schema, fields


__all__ = ["NotificationDate"]


class NotificationDate(Schema):
    date = fields.Date(required=True)
    which = fields.Integer(missing=-1)
