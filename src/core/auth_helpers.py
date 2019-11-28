from flask_jwt_extended import get_jwt_identity, jwt_required

from src.core.database import is_auth_token_valid


__all__ = ["authorize_request"]


@jwt_required
def authorize_request():
    # No JWT was provided
    token = get_jwt_identity()
    if token is None:
        raise PermissionError("You are not authorzed to access this endpoint!")

    # Get the submitted user from the JWT
    token_parts = token.split(";")
    user = token_parts[0].split("=")[1]
    auth_token = token_parts[1].split("=")[1]

    # The given username and token combo is not valid
    if not is_auth_token_valid(user, auth_token):
        raise PermissionError("You are not authorzed to access this endpoint!")
