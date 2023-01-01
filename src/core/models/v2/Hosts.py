from marshmallow import Schema, fields


__all__ = ["Basic", "Date", "Handle", "Host", "HostingDate"]


class Basic(Schema):
    uid = fields.String()
    handle = fields.String()
    url = fields.Url()


class Handle(Schema):
    handle = fields.String(required=True)


class Host(Basic):
    dates = fields.List(fields.Date("iso"))


class Date(Schema):
    date = fields.Date("iso", required=True)


class HostingDate(Handle, Date):
    ...
