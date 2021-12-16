from flask.views import MethodView
from flask_smorest import abort

from src.blueprints import keys
from src.core.database.v2 import keys as db
from src.core.models.v2 import Generic
from src.core.models.v2 import Keys as models


@keys.route("/")
class Keys(MethodView):
    @keys.response(200, models.KeyFull(many=True))
    @keys.alt_response(403, schema=Generic.HttpError)
    def get(self):
        """List all keys."""
        return db.get_all()

    @keys.arguments(models.SingleKey)
    @keys.response(201, models.KeyToken)
    @keys.alt_response(403, schema=Generic.HttpError)
    @keys.alt_response(422, schema=Generic.HttpError)
    def post(self):
        """Create a new key."""
        return "new key"


@keys.route("/<string:token>")
class KeyByCode(MethodView):
    @keys.arguments(models.KeyToken, as_kwargs=True)
    @keys.response(200, models.SingleKey)
    @keys.alt_response(403, schema=Generic.HttpError)
    @keys.alt_response(404, schema=Generic.HttpError)
    def get(self, **kwargs: str):
        """Get single key."""
        if (key := db.get(kwargs["token"])) is not None:
            return key
        abort(404)

    @keys.arguments(models.KeyToken, as_kwargs=True)
    @keys.response(204, Generic.Empty)
    @keys.alt_response(403, schema=Generic.HttpError)
    @keys.alt_response(422, schema=Generic.HttpError)
    def patch(self, **kwargs: str):
        """Update single key."""
        return "update single key"

    @keys.arguments(models.KeyToken, as_kwargs=True)
    @keys.response(204, Generic.Empty)
    @keys.alt_response(403, schema=Generic.HttpError)
    @keys.alt_response(404, schema=Generic.HttpError)
    def delete(self, **kwargs: str):
        """Delete single key."""
        if not db.delete(kwargs["token"]):
            abort(404)
