from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Budget

budget_bp = Blueprint("budget", __name__)

@budget_bp.route("/budget", methods=["GET", "POST"])
@login_required
def budget():
    budget = current_user.budget
    if not budget:
        with current_app.app_context():
            budget = Budget(user_id=current_user.id)
            db.session.add(budget)
            db.session.commit()

    if request.method == "POST":
        try:
            budget.food = float(request.form.get("food"))
            budget.transport = float(request.form.get("transport"))
            budget.study = float(request.form.get("study"))
            budget.entertainment = float(request.form.get("entertainment"))
            budget.others = float(request.form.get("others"))
            db.session.commit()
            flash("Budget updated successfully", "success")
            return redirect(url_for("budget.budget"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating budget: {e}", "danger")

    return render_template("budget.html", budget=budget)