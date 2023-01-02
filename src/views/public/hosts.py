from datetime import date

from flask.views import MethodView
from flask_smorest import abort

import src.core.database.v2 as db
from src.blueprints import hosts
from src.core.auth_helpers import authorize_route_v2
from src.core.models.v2 import Generic, Hosts as models


@hosts.route("/")
class Host(MethodView):
    @hosts.response(200, models.Basic(many=True))
    def get(self):
        """List all Hosts.

        This list can potentially be very large, and no filtering
        or pagination is supported. Consumers should take care to
        use the results of this list carefully and should filter
        it as needed before presenting to any customer.
        """
        return db.hosts.get_all()

    @authorize_route_v2
    @hosts.arguments(models.Handle, location="json", as_kwargs=True)
    @hosts.response(201, models.Basic)
    @hosts.alt_response(403, schema=Generic.HttpError)
    @hosts.alt_response(422, schema=Generic.HttpError)
    @hosts.alt_response(500, schema=Generic.HttpError)
    def post(self, **kwargs: dict):
        """Create a new Host.

        This will only succeed if the Host does not already exist.

        <strong>Note</strong>: This endpoint can only be used with an API key
        with the appropriate permissions.
        """
        ...


@hosts.route("/<string:handle>")
class HostIndividual(MethodView):
    @hosts.arguments(models.Handle, location="path", as_kwargs=True)
    @hosts.response(200, models.Host)
    @hosts.alt_response(404, schema=Generic.HttpError)
    def get(self, **kwargs: str):
        """Get a Host's info and their Hosting dates."""
        if (host := db.hosts.get(kwargs["handle"])) is None:
            abort(404)
        return host

    @authorize_route_v2
    @hosts.arguments(models.Handle, location="path", as_kwargs=True)
    @hosts.arguments(models.Handle, location="json", as_kwargs=True)
    @hosts.response(204, Generic.Empty)
    @hosts.alt_response(403, schema=Generic.HttpError)
    @hosts.alt_response(404, schema=Generic.HttpError)
    @hosts.alt_response(500, schema=Generic.HttpError)
    def patch(self, **kwargs: dict):
        """Update a Host's handle.

        <strong>Note</strong>: This endpoint can only be used with an API key
        with the appropriate permissions.
        """
        ...

    @authorize_route_v2
    @hosts.arguments(models.Handle, location="path", as_kwargs=True)
    @hosts.response(204, Generic.Empty)
    @hosts.alt_response(403, schema=Generic.HttpError)
    @hosts.alt_response(404, schema=Generic.HttpError)
    @hosts.alt_response(500, schema=Generic.HttpError)
    def delete(self, **kwargs: dict):
        """Delete a Host.

        This will only succeed if the Host does not have any
        associated Prompts to prevent orphaned or incomplete records.

        <strong>Note</strong>: This endpoint can only be used with an API key
        with the appropriate permissions.
        """
        ...


@hosts.route("/<handle>/<date>")
class HostIndividualDate(MethodView):
    @authorize_route_v2
    @hosts.arguments(models.HostingDate, location="path", as_kwargs=True)
    @hosts.response(201, Generic.Empty)
    @hosts.alt_response(403, schema=Generic.HttpError)
    @hosts.alt_response(422, schema=Generic.HttpError)
    @hosts.alt_response(500, schema=Generic.HttpError)
    def post(self, **kwargs: dict):
        """Create a Hosting date for a Host.

        <strong>Note</strong>: This endpoint can only be used with an API key
        with the appropriate permissions.
        """
        ...

    @authorize_route_v2
    @hosts.arguments(models.HostingDate, location="path", as_kwargs=True)
    @hosts.response(204, Generic.Empty)
    @hosts.alt_response(403, schema=Generic.HttpError)
    @hosts.alt_response(404, schema=Generic.HttpError)
    @hosts.alt_response(422, schema=Generic.HttpError)
    @hosts.alt_response(500, schema=Generic.HttpError)
    def delete(self, **kwargs: dict):
        """Delete a Hosting date for a Host.

        This will only succeed if there are not Prompts recorded
        during the given Hosting range to prevent orphaned or
        incomplete records.

        <strong>Note</strong>: This endpoint can only be used with an API key
        with the appropriate permissions.
        """
        ...


@hosts.route("/date/<string:date>")
class HostDate(MethodView):
    @authorize_route_v2
    @hosts.arguments(models.Date, location="path", as_kwargs=True)
    @hosts.response(200, models.Basic(many=True))
    @hosts.alt_response(403, schema=Generic.HttpError)
    @hosts.alt_response(404, schema=Generic.HttpError)
    @hosts.alt_response(422, schema=Generic.HttpError)
    def get(self, **kwargs: date):
        """Get the Host(s) for the given Hosting date.

        <strong>Note</strong>: This endpoint can only be used with an API key
        with the appropriate permissions.
        """
        if not (hosts := db.hosts.by_date(kwargs["date"])):
            abort(404)
        return hosts


@hosts.route("/current")
class HostCurrent(MethodView):
    @hosts.response(200, models.Basic)
    @hosts.alt_response(404, schema=Generic.HttpError)
    def get(self):
        """Get the current Host.

        This endpoint resolves the hosting period start date automatically
        and provides the current Host for the day.
        """
        if host := db.hosts.current():
            return host
        abort(404)
