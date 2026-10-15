
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import date

from src.database.database import Database
from src.models.transaction import Transaction


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class ExpenseApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Smart Expense & Budget Manager")
        self.geometry("1050x700")
        self.minsize(850, 600)

        self.database = Database()

        self.type_var = ctk.StringVar(value="expense")
        self.amount_var = ctk.StringVar()
        self.category_var = ctk.StringVar(value="Food")
        self.date_var = ctk.StringVar(value=date.today().isoformat())
        self.description_var = ctk.StringVar()

        self.build_gui()
        self.load_transactions()

    def build_gui(self):
        # Main page
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, corner_radius=12)
        header.grid(
            row=0, column=0, padx=20, pady=(20, 10), sticky="ew"
        )

        ctk.CTkLabel(
            header,
            text="Smart Expense & Budget Manager",
            font=ctk.CTkFont(size=25, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 4))

        ctk.CTkLabel(
            header,
            text="Record your income and expenses in one place.",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", padx=20, pady=(0, 15))

        # Transaction entry form
        form = ctk.CTkFrame(self, corner_radius=12)
        form.grid(
            row=1, column=0, padx=20, pady=10, sticky="ew"
        )
        form.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(
            form, text="Add a Transaction",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(
            row=0, column=0, columnspan=4,
            padx=15, pady=(15, 10), sticky="w"
        )

        ctk.CTkLabel(form, text="Transaction type").grid(
            row=1, column=0, padx=15, pady=7, sticky="w"
        )
        ctk.CTkComboBox(
            form,
            variable=self.type_var,
            values=["expense", "income"],
            state="readonly",
            width=220
        ).grid(row=1, column=1, padx=15, pady=7, sticky="ew")

        ctk.CTkLabel(form, text="Amount").grid(
            row=1, column=2, padx=15, pady=7, sticky="w"
        )
        ctk.CTkEntry(
            form,
            textvariable=self.amount_var,
            placeholder_text="Enter amount",
            width=220
        ).grid(row=1, column=3, padx=15, pady=7, sticky="ew")

        ctk.CTkLabel(form, text="Category").grid(
            row=2, column=0, padx=15, pady=7, sticky="w"
        )
        ctk.CTkComboBox(
            form,
            variable=self.category_var,
            values=[
                "Food", "Transport", "Bills",
                "Business", "Salary", "Other"
            ],
            state="readonly",
            width=220
        ).grid(row=2, column=1, padx=15, pady=7, sticky="ew")

        ctk.CTkLabel(form, text="Date (YYYY-MM-DD)").grid(
            row=2, column=2, padx=15, pady=7, sticky="w"
        )
        ctk.CTkEntry(
            form,
            textvariable=self.date_var,
            placeholder_text="YYYY-MM-DD"
        ).grid(row=2, column=3, padx=15, pady=7, sticky="ew")

        ctk.CTkLabel(form, text="Description").grid(
            row=3, column=0, padx=15, pady=7, sticky="w"
        )
        ctk.CTkEntry(
            form,
            textvariable=self.description_var,
            placeholder_text="e.g. Lunch or monthly salary"
        ).grid(
            row=3, column=1, columnspan=3,
            padx=15, pady=7, sticky="ew"
        )

        buttons = ctk.CTkFrame(form, fg_color="transparent")
        buttons.grid(
            row=4, column=0, columnspan=4,
            padx=15, pady=(10, 15), sticky="w"
        )

        ctk.CTkButton(
            buttons,
            text="Add Transaction",
            command=self.add_transaction
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            buttons,
            text="Clear Form",
            command=self.clear_form,
            fg_color="gray",
            hover_color="dim gray"
        ).pack(side="left")

        # Transaction list
        table_frame = ctk.CTkFrame(self, corner_radius=12)
        table_frame.grid(
            row=2, column=0, padx=20, pady=(5, 20), sticky="nsew"
        )
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(1, weight=1)

        table_header = ctk.CTkFrame(
            table_frame, fg_color="transparent"
        )
        table_header.grid(
            row=0, column=0, padx=15, pady=12, sticky="ew"
        )
        table_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            table_header,
            text="Saved Transactions",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            table_header,
            text="Refresh",
            width=100,
            command=self.load_transactions
        ).grid(row=0, column=1, sticky="e")

        # ttk.Treeview is used for the data table.
        # The surrounding application and form use CustomTkinter.
        style = ttk.Style()
        style.configure(
            "Treeview",
            rowheight=30,
            font=("Arial", 10)
        )
        style.configure(
            "Treeview.Heading",
            font=("Arial", 10, "bold")
        )

        columns = (
            "id", "date", "type",
            "category", "amount", "description"
        )
        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=9
        )

        headings = {
            "id": ("ID", 50),
            "date": ("Date", 110),
            "type": ("Type", 90),
            "category": ("Category", 110),
            "amount": ("Amount", 120),
            "description": ("Description", 300)
        }

        for column, (heading, width) in headings.items():
            self.table.heading(column, text=heading)
            self.table.column(
                column, width=width, minwidth=50, anchor="center"
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview
        )
        self.table.configure(yscrollcommand=scrollbar.set)

        self.table.grid(
            row=1, column=0, padx=(15, 0), pady=(0, 15), sticky="nsew"
        )
        scrollbar.grid(
            row=1, column=1, padx=(0, 15), pady=(0, 15), sticky="ns"
        )

    def add_transaction(self):
        try:
            transaction = Transaction(
                transaction_type=self.type_var.get(),
                amount=self.amount_var.get(),
                category=self.category_var.get(),
                transaction_date=self.date_var.get().strip(),
                description=self.description_var.get()
            )

            self.database.add_transaction(transaction)
            self.load_transactions()
            self.clear_form()

            messagebox.showinfo(
                "Success", "Transaction added successfully."
            )

        except (ValueError, TypeError) as error:
            messagebox.showerror("Invalid Input", str(error))
        except Exception as error:
            messagebox.showerror(
                "Database Error",
                f"Could not save the transaction:\n{error}"
            )

    def load_transactions(self):
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            transactions = self.database.get_transactions()

            for transaction in transactions:
                self.table.insert(
                    "",
                    "end",
                    values=(
                        transaction["id"],
                        transaction["transaction_date"],
                        transaction["transaction_type"].title(),
                        transaction["category"],
                        f'{transaction["amount"]:,.2f}',
                        transaction["description"]
                    )
                )
        except Exception as error:
            messagebox.showerror(
                "Error",
                f"Could not load transactions:\n{error}"
            )

    def clear_form(self):
        self.type_var.set("expense")
        self.amount_var.set("")
        self.category_var.set("Food")
        self.date_var.set(date.today().isoformat())
        self.description_var.set("")


if __name__ == "__main__":
    app = ExpenseApp()
    app.mainloop()
