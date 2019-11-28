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
    """Search for all prompts from a specific writer."""
    writer: str = handle.strip()
    prompts: list = database.get_prompts_by_writer(writer)
    response: dict = __build_search_response(prompts)
    response["query"] = writer
    return response


@search.route("/", methods=["GET"])
@use_args({
    "prompt": fields.Str(
        location="query",
        missing=None,
        validate=lambda x: len(x) > 1
    ),
    "writer": fields.Str(
        location="query",
        missing=None,
        validate=lambda x: len(x) > 1
    )
})
def get(args: dict):
    if args["prompt"] is not None:
        return search_by_prompt(args["prompt"])
    elif args["writer"] is not None:
        return search_by_writer(args["writer"])
    return make_error_response(
        "At least one search parameter must be provided!",
        422
    )
