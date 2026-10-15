
import sqlite3
from pathlib import Path
from typing import Optional

from src.models.transaction import Transaction


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "expenses.db"


class Database:
    def __init__(self, db_path=DEFAULT_DB_PATH):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.create_table()
        self.create_budget_table()

    def connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    # CREATE: Create the transactions table
    def create_table(self):
        with self.connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_type TEXT NOT NULL
                        CHECK(transaction_type IN ('income', 'expense')),
                    amount REAL NOT NULL CHECK(amount > 0),
                    category TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    transaction_date TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

    # INSERT: Add a transaction
    def add_transaction(self, transaction: Transaction) -> int:
        with self.connect() as connection:
            cursor = connection.execute("""
                INSERT INTO transactions
                (transaction_type, amount, category, description,
                 transaction_date)
                VALUES (?, ?, ?, ?, ?)
            """, (
                transaction.transaction_type,
                transaction.amount,
                transaction.category,
                transaction.description,
                transaction.transaction_date
            ))
            return cursor.lastrowid

    # SELECT: Get all transactions, with optional filters
    def get_transactions(self, transaction_type=None, category=None, search=None):
        query = "SELECT * FROM transactions WHERE 1=1"
        parameters = []

        if transaction_type and transaction_type != "All":
            if transaction_type not in ("income", "expense"):
                raise ValueError("Invalid transaction type.")
            query += " AND transaction_type = ?"
            parameters.append(transaction_type)

        if category and category != "All":
            query += " AND category = ?"
            parameters.append(category)

        if search and search.strip():
            query += """
                AND (category LIKE ? OR description LIKE ?)
            """
            term = f"%{search.strip()}%"
            parameters.extend([term, term])

        query += " ORDER BY transaction_date DESC, id DESC"

        with self.connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
            
            return [dict(row) for row in rows]

    # UPDATE: Edit an existing transaction
    def update_transaction(self, transaction_id, transaction):
        with self.connect() as connection:
            cursor = connection.execute("""
                UPDATE transactions
                SET transaction_type = ?,
                    amount = ?,
                    category = ?,
                    description = ?,
                    transaction_date = ?
                WHERE id = ?
            """, (
                transaction.transaction_type,
                transaction.amount,
                transaction.category,
                transaction.description,
                transaction.transaction_date,
                transaction_id
            ))
            return cursor.rowcount > 0

    def delete_transaction(self, transaction_id):
        with self.connect() as connection:
            cursor = connection.execute(
                "DELETE FROM transactions WHERE id = ?",
                (transaction_id,)
            )
            return cursor.rowcount > 0

    
    # Create the monthly budgets table
    def create_budget_table(self):
        with self.connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    month TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL CHECK(amount > 0),
                    UNIQUE(month, category)
                )
            """)

    # Save or update a monthly category budget
    def set_budget(self, month, category, amount):
        from datetime import datetime
        from math import isfinite

        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            raise ValueError("Month must use YYYY-MM format.")

        if not category or not category.strip():
            raise ValueError("Category cannot be empty.")

        try:
            amount = float(amount)
        except (ValueError, TypeError):
            raise ValueError("Budget must be a valid number.")

        if not isfinite(amount) or amount <= 0:
            raise ValueError("Budget must be greater than zero.")

        with self.connect() as connection:
            connection.execute("""
                INSERT INTO budgets (month, category, amount)
                VALUES (?, ?, ?)
                ON CONFLICT(month, category)
                DO UPDATE SET amount = excluded.amount
            """, (month, category.strip(), amount))

    # Get budgets for a month
    def get_budgets(self, month):
        with self.connect() as connection:
            rows = connection.execute("""
                SELECT category, amount
                FROM budgets
                WHERE month = ?
                ORDER BY category
            """, (month,)).fetchall()
            return [dict(row) for row in rows]

    # Calculate monthly income, expenses and balance
    def get_monthly_summary(self, month):
        with self.connect() as connection:
            row = connection.execute("""
                SELECT
                    COALESCE(SUM(
                        CASE WHEN transaction_type = 'income'
                        THEN amount ELSE 0 END
                    ), 0) AS total_income,
                    COALESCE(SUM(
                        CASE WHEN transaction_type = 'expense'
                        THEN amount ELSE 0 END
                    ), 0) AS total_expenses
                FROM transactions
                WHERE substr(transaction_date, 1, 7) = ?
            """, (month,)).fetchone()

        income = float(row["total_income"])
        expenses = float(row["total_expenses"])

        return {
            "month": month,
            "total_income": income,
            "total_expenses": expenses,
            "balance": income - expenses
        }

    # Calculate expense totals for each category in a month
    def get_category_summary(self, month):
        with self.connect() as connection:
            rows = connection.execute("""
                SELECT category, SUM(amount) AS total
                FROM transactions
                WHERE transaction_type = 'expense'
                  AND substr(transaction_date, 1, 7) = ?
                GROUP BY category
                ORDER BY total DESC
            """, (month,)).fetchall()

        return [dict(row) for row in rows]

    # Compare monthly category budgets with actual spending
    def get_budget_comparison(self, month):
        budgets = self.get_budgets(month)
        actuals = {
            item["category"]: item["total"]
            for item in self.get_category_summary(month)
        }

        results = []
        for budget in budgets:
            category = budget["category"]
            planned = float(budget["amount"])
            actual = float(actuals.get(category, 0))
            results.append({
                "category": category,
                "budget": planned,
                "actual": actual,
                "remaining": planned - actual,
                "status": (
                    "Over budget" if actual > planned
                    else "Within budget"
                )
            })

        return results
        