"""Flask application factory."""
from __future__ import annotations

import logging

from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.ml.provider_factory import init_provider


def create_app(config_object: Config | None = None) -> Flask:
    app = Flask(__name__)
    cfg = config_object or Config()
    app.config.from_object(cfg)

    logging.basicConfig(level=logging.INFO if not cfg.DEBUG else logging.DEBUG)

    CORS(
        app,
        resources={r"/api/*": {"origins": cfg.CORS_ORIGINS}},
        supports_credentials=True,
    )

    init_provider(cfg)

    from app.routes.health import bp as health_bp
    from app.routes.model import bp as model_bp
    from app.routes.children import bp as children_bp
    from app.routes.predictions import bp as predictions_bp
    from app.routes.assessments import bp as assessments_bp
    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.reports import bp as reports_bp
    from app.routes.users import bp as users_bp
    from app.routes.profile import bp as profile_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(model_bp)
    app.register_blueprint(children_bp)
    app.register_blueprint(predictions_bp)
    app.register_blueprint(assessments_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(profile_bp)

    return app
