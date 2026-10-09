
from src.database.database import Database
from src.models.transaction import Transaction


def main():
    database = Database()

    # INSERT: Add a transaction
    transaction = Transaction(
        transaction_type="expense",
        amount=5000,
        category="Food",
        description="Lunch",
        transaction_date="2026-10-10"
    )

    transaction_id = database.add_transaction(transaction)
    print("Added transaction:", transaction_id)

    # SELECT: View the transaction
    saved = database.get_transaction(transaction_id)
    print("Saved transaction:", saved)

    # UPDATE: Change the transaction
    updated_transaction = Transaction(
        transaction_type="expense",
        amount=6500,
        category="Food",
        description="Lunch and drinks",
        transaction_date="2026-10-10"
    )

    updated = database.update_transaction(
        transaction_id, updated_transaction
    )
    print("Updated successfully:", updated)

    # SELECT: View all transactions
    print("\nAll transactions:")
    for item in database.get_transactions():
        print(item)

    # SELECT with filtering
    print("\nFood transactions:")
    for item in database.get_transactions(category="Food"):
        print(item)

    # DELETE: Remove the test transaction
    deleted = database.delete_transaction(transaction_id)
    print("\nDeleted successfully:", deleted)


if __name__ == "__main__":
    main()
