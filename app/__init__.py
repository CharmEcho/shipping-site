from flask import Flask
from .models import User
from .extensions import db, migrate, jwt, bcrypt, cors, login_manager
from datetime import datetime


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")  # ✅ load ALL config here

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    login_manager.init_app(app)


    # Register blueprints
    from .routes import main_routes
    app.register_blueprint(main_routes)

    @app.context_processor
    def inject_now():
        return {"now": datetime.utcnow()}

    # Login loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = "main_routes.login"
    login_manager.login_message_category = "info"

    return app
