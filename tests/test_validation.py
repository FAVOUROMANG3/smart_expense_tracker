import tempfile
import unittest
from pathlib import Path

from src.database.database import Database
from src.models.transaction import Transaction


class TestValidation(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "test_expenses.db"
        self.db = Database(db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def make_transaction(
        self,
        transaction_type="expense",
        amount=100.0,
        category="Food",
        description="Lunch",
        transaction_date="2026-10-10",
    ):
        return Transaction(
            transaction_type=transaction_type,
            amount=amount,
            category=category,
            description=description,
            transaction_date=transaction_date,
        )

    def test_negative_amount_is_rejected(self):
        with self.assertRaises(ValueError):
            self.make_transaction(amount=-50)

    def test_zero_amount_is_rejected(self):
        with self.assertRaises(ValueError):
            self.make_transaction(amount=0)

    def test_invalid_transaction_type_is_rejected(self):
        with self.assertRaises(ValueError):
            self.make_transaction(
            transaction_type="transfer"
        )


    def test_empty_category_is_rejected_by_validation(self):
        # The database schema alone permits empty strings.
        # This test documents the desired validation behavior.
        with self.assertRaises(ValueError):
           self.make_transaction(category="")

    def test_empty_date_is_rejected_by_validation(self):
        with self.assertRaises(ValueError):
            self.make_transaction(transaction_date="")

    def test_invalid_transaction_type_filter(self):
        with self.assertRaises(ValueError):
            self.db.get_transactions(transaction_type="transfer")

    def test_invalid_budget_month_is_rejected(self):
        with self.assertRaises(ValueError):
            self.db.set_budget("October 2026", "Food", 500)

    def test_negative_budget_is_rejected(self):
        with self.assertRaises(ValueError):
            self.db.set_budget("2026-10", "Food", -100)

    def test_zero_budget_is_rejected(self):
        with self.assertRaises(ValueError):
            self.db.set_budget("2026-10", "Food", 0)

    def test_empty_budget_category_is_rejected(self):
        with self.assertRaises(ValueError):
            self.db.set_budget("2026-10", "", 500)


if __name__ == "__main__":
    unittest.main()