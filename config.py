
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY")

    # TiDB / MySQL Configuration
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "4000"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB = os.getenv("MYSQL_DB", "credit_risk")

    # TLS certificate for secure TiDB connection
    MYSQL_SSL_CA = os.getenv("MYSQL_SSL_CA")

    # Upload Folder
    UPLOAD_FOLDER = "static/uploads"

    # Report Folder
    REPORT_FOLDER = "reports"

    # ML Model Path
    MODEL_PATH = "model/credit_model.pkl"
