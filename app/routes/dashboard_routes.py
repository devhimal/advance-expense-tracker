from flask import Blueprint, render_template, request, current_app
from flask_login import login_required, current_user
from app.models import Expense, Income, Budget
from app import db
from datetime import date, timedelta, datetime
import matplotlib.pyplot as plt
import io, base64
import pandas as pd
from config import Config

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

def _get_time_filtered(df, period):
    """
    Filters a DataFrame based on a specified time period.

    Args:
        df (pd.DataFrame): The DataFrame to filter.
        period (str): The time period to filter by (daily, weekly, monthly, yearly, all).

    Returns:
        pd.DataFrame: The filtered DataFrame.
    """
    today = date.today()
    if period == "daily":
        start = today
    elif period == "weekly":
        start = today - timedelta(days=today.weekday())  # monday
    elif period == "monthly":
        start = today.replace(day=1)
    elif period == "yearly":
        start = today.replace(month=1, day=1)
    else:
        start = date.min
    return df[df["date"] >= pd.to_datetime(start)]

def _plot_category_pie(exp_df):
    """
    Generates a pie chart of expenses by category.

    Args:
        exp_df (pd.DataFrame): The DataFrame of expenses.

    Returns:
        str: A base64 encoded string of the pie chart image.
    """
    if exp_df.empty:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
    else:
        grouped = exp_df.groupby("category")["amount"].sum()
        fig, ax = plt.subplots()
        ax.pie(grouped.values, labels=grouped.index, autopct="%1.1f%%")
        ax.axis("equal")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode("ascii")
    plt.close(fig)
    return f"data:image/png;base64,{data}"

def _plot_income_source_pie(inc_df):
    """
    Generates a pie chart of income by source.

    Args:
        inc_df (pd.DataFrame): The DataFrame of incomes.

    Returns:
        str: A base64 encoded string of the pie chart image.
    """
    if inc_df.empty:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
    else:
        grouped = inc_df.groupby("source")["amount"].sum()
        fig, ax = plt.subplots()
        ax.pie(grouped.values, labels=grouped.index, autopct="%1.1f%%")
        ax.axis("equal")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode("ascii")
    plt.close(fig)
    return f"data:image/png;base64,{data}"

def _plot_trends(exp_df, inc_df):
    """
    Generates a line chart showing income and expense trends over time.

    Args:
        exp_df (pd.DataFrame): The DataFrame of expenses.
        inc_df (pd.DataFrame): The DataFrame of incomes.

    Returns:
        str: A base64 encoded string of the line chart image.
    """
    fig, ax = plt.subplots()
    if not exp_df.empty:
        exp_ts = exp_df.set_index("date").resample("D")["amount"].sum().cumsum()
        ax.plot(exp_ts.index, exp_ts.values, label="Expenses")
    if not inc_df.empty:
        inc_ts = inc_df.set_index("date").resample("D")["amount"].sum().cumsum()
        ax.plot(inc_ts.index, inc_ts.values, label="Incomes")
    if exp_df.empty and inc_df.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center")

    ax.legend()
    ax.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode("ascii")
    plt.close(fig)
    return f"data:image/png;base64,{data}"

def _plot_expense_trends_bar(exp_df, period):
    """
    Generates a bar chart of expense trends over time.

    Args:
        exp_df (pd.DataFrame): The DataFrame of expenses.
        period (str): The time period to group by (weekly, monthly, daily).

    Returns:
        str: A base64 encoded string of the bar chart image.
    """
    fig, ax = plt.subplots()
    if not exp_df.empty:
        if period == 'weekly':
            exp_df.set_index('date').resample('W')['amount'].sum().plot(kind='bar', ax=ax)
        elif period == 'monthly':
            exp_df.set_index('date').resample('M')['amount'].sum().plot(kind='bar', ax=ax)
        else:
            exp_df.set_index('date').resample('D')['amount'].sum().plot(kind='bar', ax=ax)

    if exp_df.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center")

    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode("ascii")
    plt.close(fig)
    return f"data:image/png;base64,{data}"

def _plot_over_budget_bar(over_budget_categories):
    """
    Generates a bar chart for categories that are over budget.

    Args:
        over_budget_categories (dict): A dictionary of over-budget categories and their exceeded amounts.

    Returns:
        str: A base64 encoded string of the bar chart image.
    """
    fig, ax = plt.subplots()
    if over_budget_categories:
        categories = list(over_budget_categories.keys())
        amounts = list(over_budget_categories.values())
        ax.bar(categories, amounts, color='red')
        ax.set_ylabel('Amount Over Budget')
        ax.set_title('Categories Over Budget')
    else:
        ax.text(0.5, 0.5, "No categories over budget", ha="center", va="center")

    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode("ascii")
    plt.close(fig)
    return f"data:image/png;base64,{data}"

def _plot_top_expenses_bar(top_expenses):
    """
    Generates a bar chart for the top expense categories.

    Args:
        top_expenses (dict): A dictionary of top expense categories and their amounts.

    Returns:
        str: A base64 encoded string of the bar chart image.
    """
    fig, ax = plt.subplots()
    if top_expenses:
        categories = list(top_expenses.keys())
        amounts = list(top_expenses.values())
        ax.bar(categories, amounts, color='skyblue')
        ax.set_ylabel('Amount')
        ax.set_title('Top Expense Categories')
    else:
        ax.text(0.5, 0.5, "No top expenses", ha="center", va="center")

    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode("ascii")
    plt.close(fig)
    return f"data:image/png;base64,{data}"


@dashboard_bp.route("/")
@login_required
def index():
    # get filter period from query param
    period = request.args.get("period", "monthly")  # default monthly
    # fetch data
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    incomes = Income.query.filter_by(user_id=current_user.id).all()

    # convert to pandas for easier grouping by date and category
    exp_df = pd.DataFrame([{"amount": e.amount, "category": e.category, "date": e.date} for e in expenses])
    inc_df = pd.DataFrame([{"amount": i.amount, "source": i.source, "date": i.date} for i in incomes])

    # ensure date column is datetime
    if not exp_df.empty:
        exp_df["date"] = pd.to_datetime(exp_df["date"])
    if not inc_df.empty:
        inc_df["date"] = pd.to_datetime(inc_df["date"])

    filtered_exp = _get_time_filtered(exp_df, period) if not exp_df.empty else exp_df
    filtered_inc = _get_time_filtered(inc_df, period) if not inc_df.empty else inc_df

    total_expense = filtered_exp["amount"].sum() if not filtered_exp.empty else 0
    total_income = filtered_inc["amount"].sum() if not filtered_inc.empty else 0
    balance = total_income - total_expense

    # Top 3 expense categories
    top_3_expenses = None
    if not filtered_exp.empty:
        top_3_expenses = filtered_exp.groupby('category')['amount'].sum().nlargest(3).to_dict()

    # Over budget categories
    budget = current_user.budget
    if not budget:
        with current_app.app_context():
            budget = Budget(user_id=current_user.id)
            db.session.add(budget)
            db.session.commit()

    category_budgets = {
        "Food": budget.food,
        "Transport": budget.transport,
        "Study": budget.study,
        "Entertainment": budget.entertainment,
        "Others": budget.others
    }
    over_budget_categories = {}
    if not filtered_exp.empty:
        category_expenses = filtered_exp.groupby('category')['amount'].sum().to_dict()
        for category, budget_amount in category_budgets.items():
            if category_expenses.get(category, 0) > budget_amount:
                over_budget_categories[category] = category_expenses[category] - budget_amount

    # Prepare data for category-wise budget and spending display
    category_summary = []
    all_categories = set(Config.EXPENSE_CATEGORIES) # Get all possible categories from config
    if not filtered_exp.empty:
        actual_expenses_by_category = filtered_exp.groupby('category')['amount'].sum().to_dict()
    else:
        actual_expenses_by_category = {}

    for cat in all_categories:
        budget_amount = getattr(budget, cat.lower(), 0) # Get budget from budget object, default to 0
        actual_spending = actual_expenses_by_category.get(cat, 0)
        remaining_balance = budget_amount - actual_spending
        category_summary.append({
            'category': cat,
            'budget': budget_amount,
            'spent': actual_spending,
            'balance': remaining_balance
        })


    # category pie chart
    expense_chart_data = _plot_category_pie(filtered_exp)
    income_chart_data = _plot_income_source_pie(filtered_inc)
    trends_chart_data = _plot_trends(filtered_exp, filtered_inc)
    expense_trends_bar_chart_data = _plot_expense_trends_bar(filtered_exp, period)
    over_budget_chart_data = _plot_over_budget_bar(over_budget_categories)
    top_expenses_chart_data = _plot_top_expenses_bar(top_3_expenses)

    # time-series (daily totals) for the selected period
    timeseries = None
    if not filtered_exp.empty:
        ts = filtered_exp.groupby(filtered_exp["date"].dt.date)["amount"].sum().reset_index()
        ts = ts.sort_values("date")
        timeseries = ts.to_dict(orient="records")

    return render_template(
        "dashboard.html",
        period=period,
        total_expense=total_expense,
        total_income=total_income,
        balance=balance,
        top_3_expenses=top_3_expenses,
        over_budget_categories=over_budget_categories,
        expense_chart_data=expense_chart_data,
        income_chart_data=income_chart_data,
        trends_chart_data=trends_chart_data,
        expense_trends_bar_chart_data=expense_trends_bar_chart_data,
        over_budget_chart_data=over_budget_chart_data,
        top_expenses_chart_data=top_expenses_chart_data,
        category_summary=category_summary,
        actual_expenses_by_category=actual_expenses_by_category,
        timeseries=timeseries,
    )