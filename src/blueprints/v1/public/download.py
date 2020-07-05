from src.blueprints import download

# from src.core.helpers import make_response, make_error_response


@download.route("/", methods=["GET"])
def get():
    pass

    # TODO Run queries that select the data
    # TODO Should return JSON with path to generated spreadsheet
    # TODO
