import logging
from app import create_app

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, threaded=True)