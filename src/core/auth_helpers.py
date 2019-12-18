from flask import request
from flask import abort

from jwt.exceptions import decode, DecodeError, InvalidSignatureError

from src.core.database import is_auth_token_valid


__all__ = ["authorize_request"]


def authorize_request():
    # Was an Authorization header sent?
    if "Authorization" in request.headers:
        bearer = request.headers["Authorization"]
    else:
        abort(400)

    # No token was given or the provided token is not in the proper format
    try:
        identity = bearer.split("Bearer")[1].strip()
    except IndexError:
        abort(422)

    # The given username and token combo is not valid
    try:
        token = decode(identity, verify=True, algorithms=["HS256"])
        if not is_auth_token_valid(token["user"], token["token"]):
            raise KeyError
    except (KeyError, DecodeError, InvalidSignatureError):
        abort(401)

