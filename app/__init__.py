from flask import Flask
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key_here'  # Replace with a real secret key

    # Import and register blueprints
    from app.routes import app_bp
    app.register_blueprint(app_bp, url_prefix='')

    # Add context processor to make 'now' available to all templates
    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}

    return app