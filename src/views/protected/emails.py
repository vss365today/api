from os import getenv

from flask.views import MethodView
from flask_smorest import abort
from requests import codes

from src.blueprints import emails
from src.configuration import get_config
from src.core.database.v2 import emails as db
from src.core.email import mailgun
from src.core.models.v2 import Emails as models, Generic


@emails.route("/")
class Email(MethodView):
    @emails.response(200, models.All(many=True))
    @emails.alt_response(403, schema=Generic.HttpError)
    def get(self):
        """List all email address in the mailing list.

        This list can potentially be very large, and no filtering
        or pagination is supported. Consumers should take care to
        use the results of this list carefully and should filter
        it as needed before presenting to any customer.
        """
        return db.get_all()

    @emails.arguments(models.Address, as_kwargs=True)
    @emails.response(201, Generic.Empty)
    @emails.alt_response(403, schema=Generic.HttpError)
    @emails.alt_response(422, schema=Generic.HttpError)
    @emails.alt_response(500, schema=Generic.HttpError)
    def post(self, **kwargs: list[str]):
        """Add an email address to the mailing list.

        If email sending is disabled or an address has already been added,
        a successful response will be given without attempting to record
        the address.

        If an address cannot be successfully added to both the database and
        Mailgun mailing list, it will not be recorded at all and an error
        response will be given.
        """
        # If email sending is not enabled, just pretend it worked
        if not get_config("ENABLE_EMAIL_SENDING"):
            return None

        # Because the MG address validation endpoint costs money with each hit,
        # block it off unless we are running in production
        if getenv("FLASK_ENV") == "production":
            for addr in kwargs["address"]:
                if not mailgun.verify(addr):
                    abort(500)

        # Attempt to add the address to the database first
        for addr in kwargs["address"]:
            if not db.create(addr):
                abort(500)

        # Next, attempt to add the address to the Mailgun mailing list
        mg_result = mailgun.create(kwargs["address"])

        # The address was not successfully recorded in Mailgun.
        # We do not want to keep them in our database and make the lists consistent
        if mg_result.status_code != codes.ok:
            for addr in kwargs["address"]:
                db.delete(addr)
            abort(500)

    @emails.arguments(models.Address, as_kwargs=True)
    @emails.response(204, Generic.Empty)
    @emails.alt_response(403, schema=Generic.HttpError)
    @emails.alt_response(422, schema=Generic.HttpError)
    def delete(self, **kwargs: list[str]):
        """Remove an email address from the mailing list.

        If an email sending is disabled or an email has already been removed,
        a successful response will be given without attempting to remove
        the email address.
        """
        if get_config("ENABLE_EMAIL_SENDING"):
            for addr in kwargs["address"]:
                mailgun.delete(addr)
                db.delete(addr)
