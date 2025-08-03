import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from the .env file
load_dotenv()

# Check if a secret key is set, which is required for Flask sessions
if not os.environ.get("FLASK_SECRET_KEY"):
    raise RuntimeError("The FLASK_SECRET_KEY environment variable is not set.")

# Create the Flask app instance using the application factory pattern
app = create_app()

if __name__ == "__main__":
    # Ensure this port matches your REDIRECT_URI
    app.run(port=8888, debug=True)