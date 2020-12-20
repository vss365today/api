from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import search
from src.core import database
from src.core.helpers import make_error_response, make_response


def __build_search_response(prompts: list) -> dict:
    """Collect just the info needed to display the results."""
    results: list = [
        {"date": prompt.date, "word": prompt.word, "writer": prompt.writer_handle}
        for prompt in prompts
    ]
    return {"prompts": results, "total": len(results)}


def search_by_prompt(prompt: str) -> dict:
    """Search for prompts by prompt word."""
    word: str = prompt.strip()
    prompts: list = database.prompt.search(word)
    response: dict = __build_search_response(prompts)
    response["query"] = word
    return response


def search_by_host(handle: str) -> dict:
    """Search for all prompts from a specific Host."""
    host: str = handle.strip()
    prompts: list = database.prompt.get_by_host(host)
    response: dict = __build_search_response(prompts)
    response["query"] = host
    return response


@search.route("/", methods=["GET"])
@use_args(
    {
        "prompt": fields.String(validate=lambda x: len(x) >= 1),
        "host": fields.String(validate=lambda x: len(x) > 1),
    },
    location="query",
)
def get(args: dict):
    """Search for a Prompt by word or Host."""
    # Both parameters were provided, and that is not supporte
    if len(args) > 1:
        return make_error_response(422, "Only one search parameter can be provided!")

    if "prompt" in args:
        return make_response(200, search_by_prompt(args["prompt"]))
    if "host" in args:
        return make_response(200, search_by_host(args["host"]))
    return make_error_response(422, "At least one search parameter must be provided!")
