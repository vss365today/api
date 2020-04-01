from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import account
from src.core.database import admin_user_get
from src.core.helpers import make_response, make_error_response


@account.route("/", methods=["POST"])
@use_args({
    "user": fields.Str(required=True),
    "password": fields.Str(required=True)
}, location="json")
def post(args: dict):
    """Do a user 'sign in'.

    What that means in reality is do a semi-sign in/
    make sure they are authorized to access protected endpoints.
    """
    user = admin_user_get(
        args["user"].strip(),
        args["password"].strip()
    )
    if user is not None:
        return make_response(dict(user), 200)
    return make_error_response("The username or password is incorrect!", 401)
