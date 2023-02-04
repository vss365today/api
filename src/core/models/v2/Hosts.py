from marshmallow import Schema, fields


__all__ = ["Basic", "Date", "Handle", "Host", "HostingDate", "NewHandle"]


class Basic(Schema):
    twitter_uid = fields.String()
    handle = fields.String()
    url = fields.Url()


class Date(Schema):
    date = fields.Date("iso", required=True)


class Handle(Schema):
    handle = fields.String(required=True)


class Host(Basic):
    dates = fields.List(fields.Date("iso"))


class HostingDate(Handle, Date):
    ...


class NewHandle(Schema):
    new_handle = fields.String(required=True)
