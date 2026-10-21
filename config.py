import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY")

    # MySQL Configuration
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB = os.getenv("MYSQL_DB", "credit_risk")
    

    # Upload Folder
    UPLOAD_FOLDER = "static/uploads"

    # Report Folder
    REPORT_FOLDER = "reports"

    # ML Model Path
    MODEL_PATH = "model/credit_model.pkl"