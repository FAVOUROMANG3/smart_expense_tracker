
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