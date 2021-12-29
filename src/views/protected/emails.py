from flask.views import MethodView
from flask_smorest import abort
from requests import codes

from src.blueprints import emails
from src.configuration import get_config
from src.core.database.v2 import emails as db
from src.core.email import mailgun
from src.core.models.v2 import Generic, Email as models


@emails.route("/")
class Email(MethodView):
    @emails.response(200, models.AllAddresses(many=True))
    @emails.alt_response(403, schema=Generic.HttpError)
    def get(self):
        """List all email address in the mailing list."""
        return db.get_all()

    @emails.arguments(models.EmailAddress, as_kwargs=True)
    @emails.response(201, Generic.Empty)
    @emails.alt_response(403, schema=Generic.HttpError)
    @emails.alt_response(422, schema=Generic.HttpError)
    def post(self, **kwargs: str):
        """Add an email address to the mailing list.

        If an email sending is disabled or an email has aleady been added,
        a successful response will be given without attempting to record
        the email address.
        """
        # If email sending is not enabled, just pretend it worked
        if not get_config("ENABLE_EMAIL_SENDING"):
            return

        # Because the MG address validation endpoint costs money with each hit,
        # block it off unless we are running in production
        if get_config("ENV") == "production":
            if not mailgun.validate(kwargs["address"]):
                abort(422)

        # Attempt to add the email to the address first
        if not db.create(kwargs["address"]):
            abort(422)

        # Attempt Add the email to the Mailgun mailing list
        mg_result = mailgun.create(kwargs["address"])

        # The address was not successfully recorded
        if mg_result.status_code != codes.ok:
            abort(422)

    @emails.arguments(models.EmailAddress, as_kwargs=True)
    @emails.response(204, Generic.Empty)
    @emails.alt_response(403, schema=Generic.HttpError)
    @emails.alt_response(422, schema=Generic.HttpError)
    def delete(self, **kwargs: str):
        """Remove an email address from the mailing list.

        If an email sending is disabled or an email has aleady been removed,
        a successful response will be given without attempting to remove
        the email address.
        """
        if get_config("ENABLE_EMAIL_SENDING"):
            mailgun.delete(kwargs["address"])
            db.delete(kwargs["address"])
