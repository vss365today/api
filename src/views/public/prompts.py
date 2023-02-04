from flask.views import MethodView
from flask_smorest import abort

import src.core.database.v2 as db
from src.blueprints import prompts
from src.core.auth_helpers import authorize_route_v2
from src.core.models.v2 import Generic, Prompts as models
