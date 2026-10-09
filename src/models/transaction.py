
from dataclasses import dataclass
from datetime import date
from math import isfinite
from typing import Optional


@dataclass
class Transaction:
    transaction_type: str
    amount: float
    category: str
    transaction_date: str
    description: str = ""
    id: Optional[int] = None

    def __post_init__(self):
        self.transaction_type = self.transaction_type.strip().lower()
        self.category = self.category.strip()
        self.description = self.description.strip()

        if self.transaction_type not in ("income", "expense"):
            raise ValueError("Type must be income or expense.")

        if isinstance(self.amount, bool):
            raise ValueError("Amount must be a valid positive number.")

        try:
            self.amount = float(self.amount)
        except (ValueError, TypeError):
            raise ValueError("Amount must be a valid number.")

        if not isfinite(self.amount) or self.amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        if not self.category:
            raise ValueError("Category cannot be empty.")

        try:
            date.fromisoformat(self.transaction_date)
        except (ValueError, TypeError):
            raise ValueError("Date must use YYYY-MM-DD format.")

        if not self.transaction_date:
            raise ValueError("Date cannot be empty.")

