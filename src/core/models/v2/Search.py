from marshmallow import Schema, fields, validate


__all__ = ["ByHost", "ByQuery"]


class ByHost(Schema):
    query = fields.String(required=True)


class ByQuery(Schema):
    class _prompt(Schema):
        date = fields.DateTime("iso")
        handle = fields.String()
        word = fields.String()

    query = fields.String(
        required=True,
        validate=validate.Length(min=2, max=20),
    )
    prompts = fields.List(fields.Nested(_prompt), dump_only=True)
    total = fields.Integer(strict=True, dump_only=True)
