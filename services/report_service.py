from datetime import date
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from models import Expense, Category

def get_monthly_expense_summary(
        db : Session,
        user_id: int,
        year: int,
        month: int
) -> list[dict]:
    """
    Returns category-wise expense totals for a given month.
    """

    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    stmt = (
        select(
            Category.name.label("category"),
            func.sum(Expense.amount).label("total")
        )
        .join(Expense, Expense.category_id == Category.id)
        .where(
            Expense.owner_id == user_id,
            Expense.date >= start_date,
            Expense.date < end_date
        )
        .group_by(Category.name)
        .order_by(func.sum(Expense.amount).desc())
    )

    result = db.execute(stmt).all()

    return [
        {"category": row.category, "total": float(row.total)}
        for row in result
    ]

def build_monthly_report_html(
        summary: list[dict],
        year: int,
        month: int
) -> str:
    if not summary:
        return "<p>No expenses found for this month.</p>"

    rows = ""
    total_amount = 0

    for item in summary:
        rows += f"""
        <tr>
            <td>{item['category']}</td>
            <td>₹ {item['total']}</td>
        </tr>
        """

        total_amount += item["total"]

    return f"""
    <h2>📊 Monthly Expense Report ({month}/{year})</h2>
    <table border="1" cellpadding="8" cellspacing="0">
        <tr>
            <th>Category</th>
            <th>Total</th>
        </tr>
        {rows}
        <tr>
            <td><strong>Total</strong></td>
            <td><strong>₹ {total_amount}</strong></td>
        </tr>
    </table>
    """