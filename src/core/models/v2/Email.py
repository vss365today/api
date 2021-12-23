from marshmallow import Schema, fields


__all__ = ["EmailAddress"]


class EmailAddress(Schema):
    address = fields.Email(required=True)
