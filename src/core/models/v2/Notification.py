from marshmallow import Schema, fields


__all__ = ["Date", "Which"]


class Date(Schema):
    date = fields.Date(required=True)


class Which(Schema):
    which = fields.Integer(missing=-1)
