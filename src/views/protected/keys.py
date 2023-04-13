from flask.views import MethodView
from flask_smorest import abort

from src.core.database.v2 import keys as db
from src.core.models.v2 import Generic
from src.core.models.v2 import Keys as models
from src.views import keys


@keys.route("/")
class Keys(MethodView):
    @keys.response(200, models.Key(many=True))
    @keys.alt_response(403, schema=Generic.HttpError)
    def get(self):
        """List all available keys."""
        return db.get_all()

    @keys.arguments(models.Permissions, location="json", as_kwargs=True)
    @keys.response(201, models.Token)
    @keys.alt_response(403, schema=Generic.HttpError)
    @keys.alt_response(422, schema=Generic.HttpError)
    def post(self, **kwargs: str | bool):
        """Create a new key.

        The token cannot be defined. Upon successful creation,
        a token with the requested permissions will be provided.
        """
        if token := db.create(kwargs):
            return token
        abort(422, message="Unable to create new API key.")


@keys.route("/<string:token>")
class KeyByToken(MethodView):
    @keys.arguments(models.Token, location="path", as_kwargs=True)
    @keys.response(200, models.Permissions)
    @keys.alt_response(403, schema=Generic.HttpError)
    @keys.alt_response(404, schema=Generic.HttpError)
    def get(self, **kwargs: str):
        """Get a key's permissions."""
        if (key := db.get(kwargs["token"])) is not None:
            return key
        abort(404, message="Unable to get permissions for provided API key.")

    @keys.arguments(models.Token, location="path", as_kwargs=True)
    @keys.arguments(models.Permissions, location="json", as_kwargs=True)
    @keys.response(204, Generic.Empty)
    @keys.alt_response(403, schema=Generic.HttpError)
    @keys.alt_response(422, schema=Generic.HttpError)
    def patch(self, **kwargs: str | bool):
        """Update a key's permissions."""
        db.update(kwargs)

    @keys.arguments(models.Token, location="path", as_kwargs=True)
    @keys.response(204, Generic.Empty)
    @keys.alt_response(404, schema=Generic.HttpError)
    def delete(self, **kwargs: str):
        """Delete a key.

        Once a key is deleted, it cannot be used anymore,
        nor can it be restored. All attempts to use a deleted key
        will result in an authorization error.
        """
        if not db.delete(kwargs["token"]):
            abort(404, message="Unable to delete provided API key.")
