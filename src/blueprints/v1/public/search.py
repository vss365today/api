from flask import jsonify

from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import search
from src.core import database
from src.core.helpers import make_error_response


def search_by_prompt(prompt: str):
    # Collect just the info needed to display the results
    word = prompt.strip()
    prompts = [
        {
            "date": prompt.date,
            "word": prompt.word,
            "writer": prompt.writer_handle
        }
        for prompt in database.search_for_prompt(word)
    ]

    # Return the search results
    return {
        "query": word,
        "prompts": prompts,
        "total": len(prompts)
    }


@search.route("/", methods=["GET"])
@use_args({
    "prompt": fields.Str(
        location="query",
        missing=None
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
        return {}
    else:
        return make_error_response(
            "At least one search parameter must be provided!",
            422
        )
