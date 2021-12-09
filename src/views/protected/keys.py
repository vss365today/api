from flask.views import MethodView
from flask_smorest import abort

from src.blueprints import keys
from src.core.database.models import ApiKey, ApiKeyAudit
from src.core.models.v2 import Generic
from src.core.models.v2 import Keys as models


@keys.route("/")
class Keys(MethodView):
    @keys.response(200, models.KeyFull(many=True))
    @keys.alt_response(403, schema=Generic.HttpError)
    def get(self):
        """List all keys."""
        return "get all"

    @keys.arguments(models.SingleKey)
    @keys.response(201, models.KeyToken)
    @keys.alt_response(403, schema=Generic.HttpError)
    @keys.alt_response(422, schema=Generic.HttpError)
    def post(self):
        """Create a new key."""
        return "new key"


@keys.route("/<string:key>")
class KeyByCode(MethodView):
    @keys.arguments(models.KeyToken)
    @keys.response(200, models.SingleKey)
    @keys.alt_response(403, schema=Generic.HttpError)
    @keys.alt_response(404, Generic.HttpError)
    def get(self):
        """Get single key."""
        return "get single key"

    @keys.arguments(models.KeyToken)
    @keys.response(204, Generic.Empty)
    @keys.alt_response(403, schema=Generic.HttpError)
    @keys.alt_response(422, Generic.HttpError)
    def patch(self):
        """Update single key."""
        return "update single key"

    @keys.response(204, Generic.Empty)
    @keys.alt_response(403, schema=Generic.HttpError)
    @keys.alt_response(404, Generic.HttpError)
    def delete(self):
        """Delete single key."""
        return "delete single key"
