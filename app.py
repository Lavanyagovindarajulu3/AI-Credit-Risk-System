
import os
from flask import Flask
from dotenv import load_dotenv
from app.routes import main

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError(
        "SECRET_KEY is missing. Set it in your local .env file."
    )

app.register_blueprint(main)

if __name__ == "__main__":
    app.run(debug=True)


