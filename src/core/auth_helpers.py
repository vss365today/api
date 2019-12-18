from flask import request
import jwt

from src.core.database import is_auth_token_valid


__all__ = ["authorize_request"]


def authorize_request():
    # No Authorization header was even sent
    if "Authorization" in request.headers:
        bearer = request.headers["Authorization"]
    else:
        raise KeyError("An authorization token was not provided!")

    # No JWT was provided
    try:
        identity = bearer.split("Bearer")[1].strip()
    except IndexError:
        raise ValueError("The provided authorization token is not in the proper format!")  # noqa

    # The given username and token combo is not valid
    token = jwt.decode(identity, verify=True, algorithms=["HS256"])
    try:
        if not is_auth_token_valid(token["user"], token["token"]):
            raise KeyError
    except KeyError:
        raise PermissionError("You are not authorzed to access this endpoint!")
