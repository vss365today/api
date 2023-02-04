from datetime import date
from typing import Any

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

        * **Permission Required**: `has_hosts`
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
    @hosts.arguments(models.NewHandle, location="json", as_kwargs=True)
    @hosts.response(204, Generic.Empty)
    @hosts.alt_response(403, schema=Generic.HttpError)
    @hosts.alt_response(404, schema=Generic.HttpError)
    def patch(self, **kwargs: str):
        """Update a Host's handle.

        Sometimes, a Host's Twitter handle changes. While Twitter
        auto-redirects URLs to the new handle, we should update our
        records to reflect the new handle to reduce confusion and retain accuracy.

        * **Permission Required**: `has_hosts`
        """
        if not db.hosts.update(**kwargs):
            return abort(404)

    @authorize_route_v2
    @hosts.arguments(models.Handle, location="path", as_kwargs=True)
    @hosts.response(204, Generic.Empty)
    @hosts.alt_response(403, schema=Generic.HttpError)
    @hosts.alt_response(404, schema=Generic.HttpError)
    def delete(self, **kwargs: str):
        """Delete a Host.

        This will only succeed if the Host does not have any
        assigned Hosting Dates to prevent orphaned or incomplete records.

        * **Permission Required**: `has_hosts`
        """
        if not db.hosts.delete(kwargs["handle"]):
            abort(404)


@hosts.route("/<string:handle>/<string:date>")
class HostIndividualDate(MethodView):
    @authorize_route_v2
    @hosts.arguments(models.HostingDate, location="path", as_kwargs=True)
    @hosts.response(201, Generic.Empty)
    @hosts.alt_response(403, schema=Generic.HttpError)
    @hosts.alt_response(404, schema=Generic.HttpError)
    @hosts.alt_response(422, schema=Generic.HttpError)
    def post(self, **kwargs: Any):
        """Create a Hosting Date for a Host.

        This will fail if the Hosting Date has already been assigned. While historically
        multiple Hosts may have been assigned the same day/period, the modern-day prompt
        charter does not permit that, so neither do we.

        * **Permission Required**: `has_hosts`
        """
        if not db.hosts.create_date(**kwargs):
            abort(404)

    @authorize_route_v2
    @hosts.arguments(models.HostingDate, location="path", as_kwargs=True)
    @hosts.response(204, Generic.Empty)
    @hosts.alt_response(403, schema=Generic.HttpError)
    @hosts.alt_response(404, schema=Generic.HttpError)
    @hosts.alt_response(422, schema=Generic.HttpError)
    def delete(self, **kwargs: Any):
        """Delete a Hosting Date for a Host.

        This will only succeed if there are not Prompts recorded
        during the given Hosting period to prevent orphaned or
        incomplete records.

        * **Permission Required**: `has_hosts`
        """
        if not db.hosts.delete_date(kwargs["handle"], kwargs["date"]):
            abort(404)


@hosts.route("/date/<string:date>")
class HostDate(MethodView):
    @authorize_route_v2
    @hosts.arguments(models.Date, location="path", as_kwargs=True)
    @hosts.response(200, models.Basic(many=True))
    @hosts.alt_response(403, schema=Generic.HttpError)
    @hosts.alt_response(404, schema=Generic.HttpError)
    @hosts.alt_response(422, schema=Generic.HttpError)
    def get(self, **kwargs: date):
        """Get the Host(s) for the given Hosting Date.

        While the majority of the time this will only return a single item
        in the list, historically, there have been days where multiple Hosts
        gave out a prompt on the same day, meaning care should be taken to
        handle multiple Hosts for a single Hosting date.

        * **Permission Required**: `has_hosts`
        """
        if not (hosts := db.hosts.get_by_date(kwargs["date"])):
            abort(404)
        return hosts


@hosts.route("/current")
class HostCurrent(MethodView):
    @hosts.response(200, models.Basic)
    @hosts.alt_response(404, schema=Generic.HttpError)
    def get(self):
        """Get the current Host.

        This endpoint automatically resolves the current Hosting period
        and provides the current Host for the day. This endpoint conforms
        to the modern-day prompt charter and only provides a single Host, as
        there cannot be more than one Host a day anymore.
        """
        if host := db.hosts.current():
            return host
        abort(404)
