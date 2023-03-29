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


class _HostDate(Schema):
    _id = fields.Integer()
    host_id = fields.Integer()
    date = fields.Date("iso")


class Host(Basic):
    dates = fields.List(fields.Pluck(_HostDate, "date"))


class HostingDate(Handle, Date):
    ...


class NewHandle(Schema):
    new_handle = fields.String(required=True)
