from src.blueprints import archive
from src.core.auth_helpers import authorize_route

# from src.core.helpers import make_response, make_error_response


@archive.route("/", methods=["GET"])
def get():
    pass

    # TODO Run queries that select the data
    # TODO Should return JSON with path to generated spreadsheet
    # TODO


@authorize_route
@archive.route("/", methods=["POST"])
def post():
    pass
