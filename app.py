import os
from recipehub import create_app

app = create_app()

if __name__ == "__main__":
    print("Starting the Flask application...")
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True
    )
