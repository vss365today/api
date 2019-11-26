from flask import Blueprint

from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import search

@search.route("/", methods=["GET"])
def get():
    args = {"method": "GET"}
    return args
