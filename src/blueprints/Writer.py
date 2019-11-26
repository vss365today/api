from flask import Blueprint

from webargs import fields
from webargs.flaskparser import use_args


bp = Blueprint("writer", __name__, url_prefix="/writer")


@bp.route("/", methods=["GET"])
def get():
    args = {"method": "GET"}
    return args
