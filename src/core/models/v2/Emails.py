from marshmallow import Schema, fields


__all__ = ["All", "Address"]


class Address(Schema):
    address = fields.Email(required=True)


class All(Address):
    date_added = fields.DateTime()
