from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    from game_state.routes import game_state_bp
    from user_auth.routes import user_auth_bp

    app.register_blueprint(game_state_bp)
    app.register_blueprint(user_auth_bp)

    return app
