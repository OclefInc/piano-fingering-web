from flask import Flask
from config import Config
import sys
import os

# Add the project root to the Python path so imports work correctly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the blueprint after setting the path
from app.routes import app as app_blueprint

app = Flask(__name__,
           template_folder='app/templates')  # Specify template folder
app.config.from_object(Config)

# Set a secret key for flash messages
app.secret_key = 'your-secret-key'  # Replace with a real secret key

# Register the blueprint
app.register_blueprint(app_blueprint)

if __name__ == '__main__':
    app.run(debug=True)