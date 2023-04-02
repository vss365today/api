from marshmallow import Schema, fields

__all__ = ["Months", "Years"]


class Months(Schema):
    year = fields.Integer(required=True, load_only=True)
    months = fields.List(fields.Integer, dump_only=True)


class Years(Schema):
    years = fields.List(fields.Integer(strict=True))
