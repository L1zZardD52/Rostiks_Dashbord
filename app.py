from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "expenses.json"

CATEGORIES = [
    "ЗП", "Обслуживание оборудования", "Маркетинг",
    "Транспорт", "Коммунальные услуги", "Закупка сырья", "Прочее"
]

def load_expenses():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_expenses(expenses):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(expenses, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    expenses = load_expenses()
    total = sum(e["amount"] for e in expenses)
    by_category = {}
    for e in expenses:
        cat = e["category"]
        by_category[cat] = by_category.get(cat, 0) + e["amount"]
    recent = sorted(expenses, key=lambda x: x["date"], reverse=True)[:5]
    return render_template("index.html",
        expenses=expenses,
        total=total,
        by_category=by_category,
        recent=recent,
        categories=CATEGORIES
    )

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        expenses = load_expenses()
        new_expense = {
            "id": int(datetime.now().timestamp() * 1000),
            "title": request.form["title"],
            "amount": float(request.form["amount"]),
            "category": request.form["category"],
            "date": request.form["date"],
            "description": request.form.get("description", "")
        }
        expenses.append(new_expense)
        save_expenses(expenses)
        return redirect(url_for("index"))
    return render_template("add.html", categories=CATEGORIES,
                           today=datetime.now().strftime("%Y-%m-%d"))

@app.route("/list")
def expense_list():
    expenses = load_expenses()
    category_filter = request.args.get("category", "")
    if category_filter:
        expenses = [e for e in expenses if e["category"] == category_filter]
    expenses = sorted(expenses, key=lambda x: x["date"], reverse=True)
    return render_template("list.html", expenses=expenses,
                           categories=CATEGORIES, selected=category_filter)

@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete(expense_id):
    expenses = load_expenses()
    expenses = [e for e in expenses if e["id"] != expense_id]
    save_expenses(expenses)
    return redirect(url_for("expense_list"))

@app.route("/charts")
def charts():
    expenses = load_expenses()

    # По датам — суммируем по дню
    by_date = {}
    for e in expenses:
        d = e["date"]
        by_date[d] = by_date.get(d, 0) + e["amount"]
    by_date_sorted = sorted(by_date.items())

    # По категориям
    by_category = {}
    for e in expenses:
        cat = e["category"]
        by_category[cat] = by_category.get(cat, 0) + e["amount"]

    total = sum(e["amount"] for e in expenses)

    return render_template("charts.html",
        expenses=expenses,
        by_date=by_date_sorted,
        by_category=by_category,
        total=total,
        categories=CATEGORIES
    )

@app.route("/api/chart-data")
def chart_data():
    expenses = load_expenses()
    by_category = {}
    for e in expenses:
        cat = e["category"]
        by_category[cat] = by_category.get(cat, 0) + e["amount"]
    return jsonify(by_category)

if __name__ == "__main__":
    app.run(debug=True)
