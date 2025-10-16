
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Secret key for Flask sessions
    SECRET_KEY = os.getenv("SECRET_KEY")

    # Database configuration
    # Use DATABASE_URL from .env, fallback to local SQLite instance
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'instance/app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Predefined Expense Categories
    EXPENSE_CATEGORIES = [
        "Food", "Transport", "Study", "Entertainment",
        "Utilities", "Rent", "Shopping", "Others"
    ]

    # Predefined Income Sources
    INCOME_SOURCES = [
        "Salary", "Freelance", "Investments", "Gifts", "Others"
    ]

