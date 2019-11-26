from flask import Blueprint

from webargs import fields
from webargs.flaskparser import use_args


bp = Blueprint("prompt", __name__, url_prefix="/prompt")


@bp.route("/", methods=["GET"])
@use_args({
    "date": fields.Date("%Y-%m-%d")
})
def get(args: dict):
    args["method"] = "GET"
    return args


@bp.route("/", methods=["POST"])
@use_args({
    "date": fields.Date(
        "%Y-%m-%d",
        location="json",
        required=True
    )
})
def post(args: dict):
    args["method"] = "POST"
    return args


@bp.route("/", methods=["PUT"])
@use_args({
    "date": fields.Date(
        "%Y-%m-%d",
        location="json",
        required=True
    )
})
def put(args: dict):
    args["method"] = "PUT"
    return args
