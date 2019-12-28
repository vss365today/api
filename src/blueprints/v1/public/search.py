from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import search
from src.core import database
from src.core.helpers import make_error_response


def __build_search_response(prompts: list) -> dict:
    """Collect just the info needed to display the results."""
    results: list = [
        {
            "date": prompt.date,
            "word": prompt.word,
            "writer": prompt.writer_handle
        }
        for prompt in prompts
    ]
    return {
        "prompts": results,
        "total": len(results)
    }


def search_by_prompt(prompt: str) -> dict:
    """Search for prompts by prompt word."""
    word: str = prompt.strip()
    prompts: list = database.search_for_prompt(word)
    response: dict = __build_search_response(prompts)
    response["query"] = word
    return response


def search_by_writer(handle: str) -> dict:
    """Search for all prompts from a specific Host."""
    host: str = handle.strip()
    prompts: list = database.get_prompts_by_writer(host)
    response: dict = __build_search_response(prompts)
    response["query"] = host
    return response


@search.route("/", methods=["GET"])
@use_args({
    "prompt": fields.Str(
        location="query",
        validate=lambda x: len(x) > 1
    ),
    "host": fields.Str(
        location="query",
        validate=lambda x: len(x) > 1
    )
})
def get(args: dict):
    # TODO Error message if both are provided
    if "prompt" in args:
        return search_by_prompt(args["prompt"])
    elif "host" in args:
        return search_by_writer(args["host"])
    return make_error_response(
        "At least one search parameter must be provided!",
        422
    )
