from flask import jsonify

from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import search
from src.core import database


@search.route("/", methods=["GET"])
@use_args({
    "word": fields.Str(
        location="query",
        required=True,
        validate=lambda x: len(x) > 1
    )
})
def get(args: dict):
    # Collect just the info needed to display the results
    word = args["word"].strip()
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
