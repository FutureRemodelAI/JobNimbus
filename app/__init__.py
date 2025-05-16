from flask import Flask

from .config import Config
from .database import db


def create_app(testing=False):
    app = Flask(__name__)

    if testing:
        # Override with testing config
        app.config.from_object("app.config.TestingConfig")
    else:
        app.config.from_object(Config)

    # Initialize SQLAlchemy
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Import and register your routes blueprint
    from .routes import main

    app.register_blueprint(main)

    return app
