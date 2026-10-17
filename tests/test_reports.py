import tempfile
import unittest
from pathlib import Path

from src.database.database import Database
from src.models.transaction import Transaction


class TestReports(unittest.TestCase):

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
        description="Test transaction",
        transaction_date="2026-10-10",
    ):
        return Transaction(
            transaction_type=transaction_type,
            amount=amount,
            category=category,
            description=description,
            transaction_date=transaction_date,
        )

    def test_monthly_summary(self):
        self.db.add_transaction(
            self.make_transaction(
                transaction_type="income",
                amount=2000,
                category="Salary",
                transaction_date="2026-10-01",
            )
        )

        self.db.add_transaction(
            self.make_transaction(
                amount=300,
                category="Food",
                transaction_date="2026-10-05",
            )
        )

        self.db.add_transaction(
            self.make_transaction(
                amount=200,
                category="Transport",
                transaction_date="2026-10-08",
            )
        )

        summary = self.db.get_monthly_summary("2026-10")

        self.assertEqual(summary["total_income"], 2000)
        self.assertEqual(summary["total_expenses"], 500)
        self.assertEqual(summary["balance"], 1500)

    def test_monthly_summary_excludes_other_months(self):
        self.db.add_transaction(
            self.make_transaction(
                amount=100,
                transaction_date="2026-09-15",
            )
        )

        self.db.add_transaction(
            self.make_transaction(
                amount=250,
                transaction_date="2026-10-10",
            )
        )

        summary = self.db.get_monthly_summary("2026-10")

        self.assertEqual(summary["total_expenses"], 250)

    def test_category_summary(self):
        self.db.add_transaction(
            self.make_transaction(amount=100, category="Food")
        )

        self.db.add_transaction(
            self.make_transaction(amount=150, category="Food")
        )

        self.db.add_transaction(
            self.make_transaction(
                amount=80,
                category="Transport",
            )
        )

        results = {
            item["category"]: item["total"]
            for item in self.db.get_category_summary("2026-10")
        }

        self.assertEqual(results["Food"], 250)
        self.assertEqual(results["Transport"], 80)

    def test_category_summary_excludes_income(self):
        self.db.add_transaction(
            self.make_transaction(
                transaction_type="income",
                amount=1000,
                category="Salary",
            )
        )

        results = self.db.get_category_summary("2026-10")

        categories = [item["category"] for item in results]

        self.assertNotIn("Salary", categories)

    def test_budget_comparison_within_budget(self):
        self.db.set_budget("2026-10", "Food", 500)

        self.db.add_transaction(
            self.make_transaction(amount=200, category="Food")
        )

        results = self.db.get_budget_comparison("2026-10")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["budget"], 500)
        self.assertEqual(results[0]["actual"], 200)
        self.assertEqual(results[0]["remaining"], 300)
        self.assertEqual(results[0]["status"], "Within budget")

    def test_budget_comparison_over_budget(self):
        self.db.set_budget("2026-10", "Food", 200)

        self.db.add_transaction(
            self.make_transaction(amount=250, category="Food")
        )

        results = self.db.get_budget_comparison("2026-10")

        self.assertEqual(results[0]["budget"], 200)
        self.assertEqual(results[0]["actual"], 250)
        self.assertEqual(results[0]["remaining"], -50)
        self.assertEqual(results[0]["status"], "Over budget")

    def test_budget_comparison_without_spending(self):
        self.db.set_budget("2026-10", "Food", 500)

        results = self.db.get_budget_comparison("2026-10")

        self.assertEqual(results[0]["actual"], 0)
        self.assertEqual(results[0]["remaining"], 500)
        self.assertEqual(results[0]["status"], "Within budget")

    def test_empty_monthly_summary(self):
        summary = self.db.get_monthly_summary("2026-10")

        self.assertEqual(summary["total_income"], 0)
        self.assertEqual(summary["total_expenses"], 0)
        self.assertEqual(summary["balance"], 0)


if __name__ == "__main__":
    unittest.main()