from typing import Any

from flask.views import MethodView
from flask_smorest import abort

import src.core.database.v2 as db
from src.blueprints import search_v2
from src.core.models.v2 import Generic
