from marshmallow import Schema, fields


__all__ = ["File"]


class File(Schema):
    file_name = fields.String(dump_only=True)
