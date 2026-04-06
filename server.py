import os
from dotenv import load_dotenv
load_dotenv()

# Set FLASK_DEBUG dynamically from FLASK_ENV before Flask CLI reads it
if "FLASK_DEBUG" not in os.environ:
    os.environ["FLASK_DEBUG"] = "1" if os.environ.get("FLASK_ENV") == "development" else "0"

from app import create_app

app = create_app()

if __name__ == "__main__":
    print(f"Starting server in {app.config.get('ENV', 'unknown')} environment...")
    app.run(
        host=app.config.get("HOST", "127.0.0.1"),
        port=app.config.get("PORT", 5003),
        debug=app.config.get("DEBUG", False),
    )