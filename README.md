# advance-expense-tracker

A web application for tracking personal expenses and income. This application allows users to manage their finances by providing a clear overview of their spending and earnings.

## Features

- **User Authentication**: Secure registration and login system for users.
- **Dashboard**: A comprehensive dashboard that displays a summary of total income, total expenses, and the current balance.
- **Expense Management**: Users can add, edit, and delete their expenses. Expenses are categorized for better tracking.
- **Income Management**: Users can add, edit, and delete their income sources.
- **Budgeting**: Set monthly budgets for different categories (e.g., Food, Transport, Study, Entertainment, Others) and track spending against them.
- **Transaction History**: View a detailed history of all transactions (both income and expenses) with options to filter by category and search by description.
- **Data Export**: Export transaction data to CSV, Excel, or PDF formats.

## Technologies Used

- **Backend**:
  - Python
  - Flask
  - Flask-SQLAlchemy (for database ORM)
  - Flask-Migrate (for database migrations)
  - Flask-Login (for user session management)
  - Flask-WTF (for forms)
  - Gunicorn (as a production web server)
- **Database**:
  - SQLite (default)
- **Frontend**:
  - HTML
  - CSS
  - Jinja2 (template engine)

## Setup and Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/devhimal/advance-expense-tracker.git
    cd advance-expense-tracker

    ```

2. **Create and activate a virtual environment**:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install the dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Create a `.env` file**:
    Create a `.env` file in the root directory and add the following environment variables:

    ```
    SECRET_KEY='a_very_secret_key'
    DATABASE_URL='sqlite:///instance/app.db'
    ```

5. **Run database migrations**:

    ```bash
    flask db upgrade
    ```

6. **Run the application**:

    - **For development**:

      ```bash
      python run.py
      ```

    - **For production**:

      ```bash
      gunicorn run:app
      ```

    The application will be available at `http://127.0.0.1:5000` (for development) or `http://127.0.0.1:8000` (for Gunicorn).

## Project Structure

```
/advance-expense-tracker
├── app/
│   ├── __init__.py         # Initializes the Flask application and extensions
│   ├── forms/              # WTForms definitions
│   ├── models/             # SQLAlchemy database models
│   ├── routes/             # Application routes (blueprints)
│   ├── static/             # Static files (CSS, JS, images)
│   └── templates/          # Jinja2 HTML templates
├── instance/
│   └── app.db              # SQLite database file
├── migrations/             # Flask-Migrate migration scripts
├── tests/                  # Test suite
├── .env                    # Environment variables
├── .gitignore              # Git ignore file
├── config.py               # Configuration settings
├── procfile                # For deployment (e.g., Heroku)
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point

