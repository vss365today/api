from marshmallow import Schema, fields, validate


__all__ = ["Results", "Query"]


class Results(Schema):
    class _prompt(Schema):
        date = fields.DateTime("iso")
        handle = fields.String()
        word = fields.String()

    query = fields.String()
    prompts = fields.List(fields.Nested(_prompt))
    total = fields.Integer(strict=True)


class Query(Schema):
    query = fields.String(required=True, validate=validate.Length(min=2, max=20))
