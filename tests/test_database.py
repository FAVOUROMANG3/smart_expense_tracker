
import tempfile
import unittest
from pathlib import Path

from src.database.database import Database
from src.models.transaction import Transaction


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "test_expenses.db"
        self.db = Database(db_path)

    def tearDown(self):
    # Close database connections before deleting the temporary folder.
        if hasattr(self, "db") and hasattr(self.db, "close"):
            self.db.close()

        if hasattr(self, "temp_dir"):
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

    def test_add_and_retrieve_transaction(self):
        transaction = self.make_transaction()
        transaction_id = self.db.add_transaction(transaction)

        results = self.db.get_transactions()

        self.assertGreater(transaction_id, 0)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["category"], "Food")
        self.assertEqual(results[0]["amount"], 100.0)

    def test_filter_by_transaction_type(self):
        self.db.add_transaction(self.make_transaction())
        self.db.add_transaction(
            self.make_transaction(
                transaction_type="income",
                category="Salary",
                description="Monthly salary",
            )
        )

        results = self.db.get_transactions(
            transaction_type="income"
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["category"], "Salary")

    def test_filter_by_category(self):
        self.db.add_transaction(self.make_transaction())
        self.db.add_transaction(
            self.make_transaction(category="Transport")
        )

        results = self.db.get_transactions(category="Food")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["category"], "Food")

    def test_search_by_description(self):
        self.db.add_transaction(
            self.make_transaction(description="Lunch at cafe")
        )
        self.db.add_transaction(
            self.make_transaction(description="Bus fare")
        )

        results = self.db.get_transactions(search="cafe")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["description"], "Lunch at cafe")

    def test_invalid_transaction_type_filter(self):
        with self.assertRaises(ValueError):
            self.db.get_transactions(transaction_type="transfer")

    def test_update_transaction(self):
        transaction_id = self.db.add_transaction(
            self.make_transaction()
        )
        updated = self.make_transaction(
            amount=250.0,
            category="Bills",
            description="Electricity",
        )

        result = self.db.update_transaction(
            transaction_id, updated
        )

        self.assertTrue(result)
        saved = self.db.get_transactions()[0]
        self.assertEqual(saved["amount"], 250.0)
        self.assertEqual(saved["category"], "Bills")

    def test_update_missing_transaction_returns_false(self):
        result = self.db.update_transaction(
            99999, self.make_transaction()
        )
        self.assertFalse(result)

    def test_delete_transaction(self):
        transaction_id = self.db.add_transaction(
            self.make_transaction()
        )

        result = self.db.delete_transaction(transaction_id)

        self.assertTrue(result)
        self.assertEqual(self.db.get_transactions(), [])

    def test_delete_missing_transaction_returns_false(self):
        self.assertFalse(self.db.delete_transaction(99999))

    def test_invalid_amount_rejected_by_database(self):
    # The Transaction model rejects invalid amounts
    # before they can be inserted into the database.
        with self.assertRaises(ValueError):
            self.make_transaction(amount=-50)

    # Confirm that no transaction was a dded.
        self.assertEqual(self.db.get_transactions(), [])

    def test_monthly_summary(self):
        self.db.add_transaction(
            self.make_transaction(
                transaction_type="income",
                amount=1000,
                category="Salary",
                transaction_date="2026-10-01",
            )
        )
        self.db.add_transaction(
            self.make_transaction(
                amount=250,
                transaction_date="2026-10-05",
            )
        )
        self.db.add_transaction(
            self.make_transaction(
                amount=100,
                transaction_date="2026-09-20",
            )
        )

        summary = self.db.get_monthly_summary("2026-10")

        self.assertEqual(summary["total_income"], 1000)
        self.assertEqual(summary["total_expenses"], 250)
        self.assertEqual(summary["balance"], 750)

    def test_category_summary(self):
        self.db.add_transaction(
            self.make_transaction(amount=100, category="Food")
        )
        self.db.add_transaction(
            self.make_transaction(amount=50, category="Food")
        )
        self.db.add_transaction(
            self.make_transaction(amount=80, category="Transport")
        )

        results = {
            row["category"]: row["total"]
            for row in self.db.get_category_summary("2026-10")
        }

        self.assertEqual(results["Food"], 150)
        self.assertEqual(results["Transport"], 80)

    def test_set_and_update_budget(self):
        self.db.set_budget("2026-10", "Food", 500)
        self.db.set_budget("2026-10", "Food", 700)

        budgets = self.db.get_budgets("2026-10")

        self.assertEqual(len(budgets), 1)
        self.assertEqual(budgets[0]["amount"], 700)

    def test_invalid_budget_rejected(self):
        with self.assertRaises(ValueError):
            self.db.set_budget("October 2026", "Food", 500)

        with self.assertRaises(ValueError):
            self.db.set_budget("2026-10", "Food", -10)

    def test_budget_comparison(self):
        self.db.set_budget("2026-10", "Food", 200)
        self.db.add_transaction(
            self.make_transaction(amount=250, category="Food")
        )

        results = self.db.get_budget_comparison("2026-10")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["budget"], 200)
        self.assertEqual(results[0]["actual"], 250)
        self.assertEqual(results[0]["remaining"], -50)
        self.assertEqual(results[0]["status"], "Over budget")

    def test_database_persistence(self):
        self.db.add_transaction(self.make_transaction())

        # Reopen the same database file using a new Database instance.
        reopened = Database(self.db.db_path)

        self.assertEqual(len(reopened.get_transactions()), 1)


if __name__ == "__main__":
    unittest.main()
