from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
import io
import csv
import openpyxl
from io import BytesIO
from weasyprint import HTML
from flask_login import login_required, current_user
from app import db
from app.models import Expense, Income
from datetime import datetime
from config import Config

expense_bp = Blueprint("expense", __name__)

@expense_bp.route("/add-expense", methods=["GET", "POST"])
@login_required
def add_expense():
    """Adds a new expense to the database."""
    if request.method == "POST":
        try:
            amount = float(request.form.get("amount") or 0)
            category = request.form.get("category") or "Uncategorized"
            date_str = request.form.get("date")
            desc = request.form.get("description")
            dt = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.today().date()
            e = Expense(user_id=current_user.id, amount=amount, category=category, date=dt, description=desc)
            db.session.add(e)
            db.session.commit()
            flash("Expense added", "success")
            return redirect(url_for("dashboard.index"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding expense: {e}", "danger")
            return redirect(url_for("expense.add_expense"))
    return render_template("add_expense.html", categories=Config.EXPENSE_CATEGORIES)

@expense_bp.route("/add-income", methods=["GET", "POST"])
@login_required
def add_income():
    """Adds a new income to the database."""
    if request.method == "POST":
        try:
            amount = float(request.form.get("amount") or 0)
            source = request.form.get("source") or "Source"
            date_str = request.form.get("date")
            desc = request.form.get("description")
            dt = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.today().date()
            inc = Income(user_id=current_user.id, amount=amount, source=source, date=dt, description=desc)
            db.session.add(inc)
            db.session.commit()
            flash("Income added", "success")
            return redirect(url_for("dashboard.index"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding income: {e}", "danger")
            return redirect(url_for("expense.add_income"))
    return render_template("add_income.html", sources=Config.INCOME_SOURCES)

@expense_bp.route("/history")
@login_required
def history():
    """Displays the transaction history with filtering and search."""
    category = request.args.get('category')
    search = request.args.get('search')
    
    expenses_query = Expense.query.filter_by(user_id=current_user.id)
    incomes_query = Income.query.filter_by(user_id=current_user.id)

    if category:
        expenses_query = expenses_query.filter_by(category=category)
    
    if search:
        expenses_query = expenses_query.filter(Expense.description.ilike(f'%{search}%'))
        incomes_query = incomes_query.filter(Income.description.ilike(f'%{search}%'))

    expenses = expenses_query.order_by(Expense.date.desc()).all()
    incomes = incomes_query.order_by(Income.date.desc()).all()
    
    categories = db.session.query(Expense.category).distinct().all()
    categories = [c[0] for c in categories]

    return render_template("history.html", expenses=expenses, incomes=incomes, categories=categories, expense_categories=Config.EXPENSE_CATEGORIES, income_sources=Config.INCOME_SOURCES)

@expense_bp.route("/edit-expense/<int:expense_id>", methods=["GET", "POST"])
@login_required
def edit_expense(expense_id):
    """Edits an existing expense."""
    expense = Expense.query.get_or_404(expense_id)
    if expense.user_id != current_user.id:
        flash("You are not authorized to edit this expense", "danger")
        return redirect(url_for("expense.history"))
    if request.method == "POST":
        try:
            expense.amount = float(request.form.get("amount") or 0)
            expense.category = request.form.get("category") or "Uncategorized"
            date_str = request.form.get("date")
            expense.date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.today().date()
            expense.description = request.form.get("description")
            db.session.commit()
            flash("Expense updated", "success")
            return redirect(url_for("expense.history"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating expense: {e}", "danger")
            return redirect(url_for("expense.edit_expense", expense_id=expense_id))
    return render_template("edit_expense.html", expense=expense)

@expense_bp.route("/delete-expense/<int:expense_id>", methods=["POST"])
@login_required
def delete_expense(expense_id):
    """Deletes an expense."""
    expense = Expense.query.get_or_404(expense_id)
    if expense.user_id != current_user.id:
        flash("You are not authorized to delete this expense", "danger")
        return redirect(url_for("expense.history"))
    try:
        db.session.delete(expense)
        db.session.commit()
        flash("Expense deleted", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting expense: {e}", "danger")
    return redirect(url_for("expense.history"))

@expense_bp.route("/edit-income/<int:income_id>", methods=["GET", "POST"])
@login_required
def edit_income(income_id):
    """Edits an existing income."""
    income = Income.query.get_or_404(income_id)
    if income.user_id != current_user.id:
        flash("You are not authorized to edit this income", "danger")
        return redirect(url_for("expense.history"))
    if request.method == "POST":
        try:
            income.amount = float(request.form.get("amount") or 0)
            income.source = request.form.get("source") or "Source"
            date_str = request.form.get("date")
            income.date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.today().date()
            income.description = request.form.get("description")
            db.session.commit()
            flash("Income updated", "success")
            return redirect(url_for("expense.history"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating income: {e}", "danger")
            return redirect(url_for("expense.edit_income", income_id=income_id))
    return render_template("edit_income.html", income=income)

@expense_bp.route("/delete-income/<int:income_id>", methods=["POST"])
@login_required
def delete_income(income_id):
    """Deletes an income."""
    income = Income.query.get_or_404(income_id)
    if income.user_id != current_user.id:
        flash("You are not authorized to delete this income", "danger")
        return redirect(url_for("expense.history"))
    try:
        db.session.delete(income)
        db.session.commit()
        flash("Income deleted", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting income: {e}", "danger")
    return redirect(url_for("expense.history"))

@expense_bp.route("/export-csv")
@login_required
def export_csv():
    """Exports all transactions to a CSV file."""
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    incomes = Income.query.filter_by(user_id=current_user.id).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['Type', 'Date', 'Category/Source', 'Amount', 'Description'])

    for income in incomes:
        writer.writerow(['Income', income.date, income.source, income.amount, income.description])
    
    for expense in expenses:
        writer.writerow(['Expense', expense.date, expense.category, expense.amount, expense.description])

    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=transactions.csv"})

@expense_bp.route("/export-excel")
@login_required
def export_excel():
    """Exports all transactions to an Excel file."""
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    incomes = Income.query.filter_by(user_id=current_user.id).all()

    workbook = openpyxl.Workbook()
    
    # Income sheet
    income_sheet = workbook.active
    income_sheet.title = "Incomes"
    income_sheet.append(['Date', 'Source', 'Amount', 'Description'])
    for income in incomes:
        income_sheet.append([income.date, income.source, income.amount, income.description])

    # Expense sheet
    expense_sheet = workbook.create_sheet(title="Expenses")
    expense_sheet.append(['Date', 'Category', 'Amount', 'Description'])
    for expense in expenses:
        expense_sheet.append([expense.date, expense.category, expense.amount, expense.description])

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return Response(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition":"attachment;filename=transactions.xlsx"})

@expense_bp.route("/export-pdf")
@login_required
def export_pdf():
    """Exports all transactions to a PDF file."""
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    incomes = Income.query.filter_by(user_id=current_user.id).all()

    html = render_template("export_pdf.html", expenses=expenses, incomes=incomes)
    pdf = HTML(string=html).write_pdf()

    return Response(pdf, mimetype="application/pdf", headers={"Content-Disposition":"attachment;filename=transactions.pdf"})