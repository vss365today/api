from marshmallow import Schema, fields

__all__ = ["Months"]


class Months(Schema):
    year = fields.Integer(required=True, load_only=True)
    months = fields.List(fields.Integer, dump_only=True)
