from src.core.config import load_app_config


def init_extensions(app):
    # Load app extensions
    app.config.update(load_app_config())
