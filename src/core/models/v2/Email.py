from marshmallow import Schema, fields


__all__ = ["AllAddresses", "EmailAddress"]


class AllAddresses(Schema):
    email = fields.Email()
    date_added = fields.DateTime()


class EmailAddress(Schema):
    address = fields.Email(required=True)
