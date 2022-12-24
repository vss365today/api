from flask.views import MethodView
from flask_smorest import abort

from src.blueprints import hosts
from src.configuration import get_config
from src.core.models.v2 import Generic, Hosts as models
