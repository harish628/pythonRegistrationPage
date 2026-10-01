import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

# Read values from a local .env file (if present) into environment variables.
load_dotenv()

db = SQLAlchemy()


def get_database_uri():
    """Build the MySQL connection string from environment variables."""
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    name = os.getenv("DB_NAME", "registration_db")
    user = os.getenv("DB_USER", "registration_user")
    password = os.getenv("DB_PASSWORD", "")

    # quote_plus keeps special characters in the password from breaking the URI.
    return (
        f"mysql+pymysql://{quote_plus(user)}:{quote_plus(password)}"
        f"@{host}:{port}/{name}?charset=utf8mb4"
    )
