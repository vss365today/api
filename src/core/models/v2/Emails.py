from marshmallow import Schema, fields


__all__ = ["All", "Address"]


class Address(Schema):
    address = fields.List(fields.Email(), required=True)


class All(Schema):
    address = fields.Email()
    date_added = fields.DateTime()
