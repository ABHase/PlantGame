from flask import Flask, render_template
from flask_login import LoginManager
from .socket_config import socketio  # Import socketio
from .extensions import db  # Import db from extensions.py
from .config import config
import os

# Initialize extensions
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    from .user_auth.models import User  # Import the User model here to avoid circular imports
    return db.session.get(User, int(user_id))

def create_app():
    print("Creating app...")
    app = Flask(__name__)
    config_name = os.environ.get('FLASK_CONFIG') or 'default'
    app.config.from_object(config[config_name])
    
    print("Initializing db...")
    db.init_app(app)  # Bind it to the Flask app here
    
    print("Initializing login manager...")
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    with app.app_context():
        from .user_auth.models import User  # Import the User model here
        from .user_auth.models import UpgradeModel  # Import the UpgradeModel model here
        from .models.biome_model import BiomeModel
        from .models.plant_model import PlantModel
        from .user_auth.models import PlantTimeModel
        from .user_auth.models import GlobalState
        print("Creating all db tables...")
        db.create_all()

        # Check if admin user already exists
        existing_admin = User.query.filter_by(username='admin').first()
        if existing_admin is None:
            # Add an admin user
            admin = User(username='admin', password='admin')
            db.session.add(admin)
            db.session.commit()
            print("Admin user added.")
        else:
            print("Admin user already exists.")

    print("Registering blueprints...")
    from .game_state.routes import game_state_bp
    from .user_auth.routes import user_auth_bp
    
    app.register_blueprint(game_state_bp, url_prefix='/game_state')
    app.register_blueprint(user_auth_bp, url_prefix='/user_auth')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/game')
    def game():
        return render_template('game.html')

    print("Initializing socketio...")
    socketio.init_app(app)
    
    print("App created.")
    return app

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=app.config['DEBUG'], use_reloader=False)
