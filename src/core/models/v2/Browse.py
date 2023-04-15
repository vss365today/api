from marshmallow import Schema, fields

from src.core.models.v2.Hosts import Basic
from src.core.models.v2.Prompts import Prompt


__all__ = ["BrowseResult", "ByYear", "ByYearMonth", "GetMonths", "GetYears"]


class BrowseResult(Schema):
    hosts = fields.List(fields.Nested(Basic))
    prompts = fields.List(fields.Nested(Prompt), dump_default=[])
    total = fields.Integer(strict=True)


class ByYear(Schema):
    year = fields.Integer(required=True, strict=True)


class ByYearMonth(ByYear):
    month = fields.Integer(required=True, strict=True)


class GetMonths(Schema):
    year = fields.Integer(required=True, load_only=True)
    months = fields.List(fields.Integer(strict=True), dump_only=True)


class GetYears(Schema):
    years = fields.List(fields.Integer(strict=True))
