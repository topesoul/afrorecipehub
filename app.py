import os
from recipehub import create_app
from recipehub.api import api_bp  # Import the API blueprint

app = create_app()

# Register the API blueprint for real-time points retrieval
app.register_blueprint(api_bp)

if __name__ == "__main__":
    print("Starting the Flask application...")
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True
    )
