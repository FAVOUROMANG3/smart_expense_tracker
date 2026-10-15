
import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPORT_FOLDER = PROJECT_ROOT / "reports"


def export_transactions(database, filename=None):
    EXPORT_FOLDER.mkdir(parents=True, exist_ok=True)

    if filename is None:
        filename = EXPORT_FOLDER / "transactions.csv"

    transactions = database.get_transactions()

    
    columns = [
        "id",
        "transaction_date",
        "transaction_type",
        "category",
        "amount",
        "description",
        "created_at"
    ]


    with open(filename, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(transactions)

    return str(filename)


def export_monthly_report(database, month, filename=None):
    EXPORT_FOLDER.mkdir(parents=True, exist_ok=True)

    if filename is None:
        filename = EXPORT_FOLDER / f"monthly_report_{month}.csv"

    summary = database.get_monthly_summary(month)
    categories = database.get_category_summary(month)
    budgets = database.get_budget_comparison(month)

    with open(filename, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)

        writer.writerow(["Monthly Financial Report", month])
        writer.writerow([])
        writer.writerow(["Metric", "Amount"])
        writer.writerow(["Total income", summary["total_income"]])
        writer.writerow(["Total expenses", summary["total_expenses"]])
        writer.writerow(["Balance", summary["balance"]])

        writer.writerow([])
        writer.writerow(["Expense by category"])
        writer.writerow(["Category", "Actual expenses"])

        for item in categories:
            writer.writerow([item["category"], item["total"]])

        writer.writerow([])
        writer.writerow(["Budget comparison"])
        writer.writerow([
            "Category", "Budget", "Actual", "Remaining", "Status"
        ])

        for item in budgets:
            writer.writerow([
                item["category"], item["budget"], item["actual"],
                item["remaining"], item["status"]
            ])

    return str(filename)
