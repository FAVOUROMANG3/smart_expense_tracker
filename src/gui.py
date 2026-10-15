import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import date

from src.database.database import Database
from src.models.transaction import Transaction

from src.reporting import export_transactions, export_monthly_report


CATEGORIES = [
    "Food", "Transport", "Bills",
    "Business", "Salary", "Other"
]


class ExpenseApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Smart Expense & Budget Manager")
        self.geometry("1100x760")
        self.minsize(900, 650)

        self.database = Database()
        self.selected_id = None

        self.type_var = ctk.StringVar(value="expense")
        self.amount_var = ctk.StringVar()
        self.category_var = ctk.StringVar(value="Food")
        self.date_var = ctk.StringVar(value=date.today().isoformat())
        self.description_var = ctk.StringVar()

        self.search_var = ctk.StringVar()
        self.filter_type_var = ctk.StringVar(value="All")
        self.filter_category_var = ctk.StringVar(value="All")

        self.build_gui()
        self.load_transactions()

    def build_gui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            self,
            text="Smart Expense & Budget Manager",
            font=ctk.CTkFont(size=25, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(18, 10), sticky="w")

        # Transaction form
        form = ctk.CTkFrame(self)
        form.grid(row=1, column=0, padx=20, pady=8, sticky="ew")
        form.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(
            form, text="Transaction Details",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, columnspan=4,
               padx=12, pady=12, sticky="w")

        ctk.CTkLabel(form, text="Type").grid(
            row=1, column=0, padx=12, pady=6, sticky="w"
        )
        ctk.CTkComboBox(
            form, variable=self.type_var,
            values=["expense", "income"], state="readonly"
        ).grid(row=1, column=1, padx=12, pady=6, sticky="ew")

        ctk.CTkLabel(form, text="Amount").grid(
            row=1, column=2, padx=12, pady=6, sticky="w"
        )
        ctk.CTkEntry(
            form, textvariable=self.amount_var,
            placeholder_text="Enter a positive amount"
        ).grid(row=1, column=3, padx=12, pady=6, sticky="ew")

        ctk.CTkLabel(form, text="Category").grid(
            row=2, column=0, padx=12, pady=6, sticky="w"
        )
        ctk.CTkComboBox(
            form, variable=self.category_var,
            values=CATEGORIES, state="readonly"
        ).grid(row=2, column=1, padx=12, pady=6, sticky="ew")

        ctk.CTkLabel(form, text="Date (YYYY-MM-DD)").grid(
            row=2, column=2, padx=12, pady=6, sticky="w"
        )
        ctk.CTkEntry(
            form, textvariable=self.date_var
        ).grid(row=2, column=3, padx=12, pady=6, sticky="ew")

        ctk.CTkLabel(form, text="Description").grid(
            row=3, column=0, padx=12, pady=6, sticky="w"
        )
        ctk.CTkEntry(
            form, textvariable=self.description_var,
            placeholder_text="What was this transaction for?"
        ).grid(row=3, column=1, columnspan=3,
               padx=12, pady=6, sticky="ew")

        actions = ctk.CTkFrame(form, fg_color="transparent")
        actions.grid(row=4, column=0, columnspan=4,
                     padx=12, pady=12, sticky="w")

        ctk.CTkButton(
            actions, text="Add Transaction",
            command=self.add_transaction
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            actions, text="Update Selected",
            command=self.update_transaction
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            actions, text="Delete Selected",
            fg_color="#B83232", hover_color="#8F2525",
            command=self.delete_transaction
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            actions, text="Clear Form",
            fg_color="gray", hover_color="dim gray",
            command=self.clear_form
        ).pack(side="left", padx=8)

        # Search and filters
        filters = ctk.CTkFrame(self)
        filters.grid(row=2, column=0, padx=20, pady=8, sticky="ew")
        filters.grid_columnconfigure(0, weight=1)

        ctk.CTkEntry(
            filters, textvariable=self.search_var,
            placeholder_text="Search category or description..."
        ).grid(row=0, column=0, padx=8, pady=10, sticky="ew")

        ctk.CTkComboBox(
            filters, variable=self.filter_type_var,
            values=["All", "income", "expense"],
            state="readonly", width=130
        ).grid(row=0, column=1, padx=8, pady=10)

        ctk.CTkComboBox(
            filters, variable=self.filter_category_var,
            values=["All"] + CATEGORIES,
            state="readonly", width=150
        ).grid(row=0, column=2, padx=8, pady=10)

        ctk.CTkButton(
            filters, text="Apply Filters",
            command=self.load_transactions, width=120
        ).grid(row=0, column=3, padx=8, pady=10)

        ctk.CTkButton(
            filters, text="Reset",
            command=self.reset_filters,
            fg_color="gray", hover_color="dim gray", width=80
        ).grid(row=0, column=4, padx=8, pady=10)


        # Results table
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=3, column=0, padx=20, pady=(5, 18),
                         sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            table_frame, text="Saved Transactions",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=12, pady=10, sticky="w")

        columns = (
            "id", "date", "type", "category", "amount", "description"
        )
        self.table = ttk.Treeview(
            table_frame, columns=columns,
            show="headings", selectmode="browse"
        )

        ctk.CTkButton(
            self,
            text="Monthly Summary & Budgets",
            command=self.open_reports
        ).grid(row=5, column=0, padx=20, pady=(0, 8), sticky="ew")

        ctk.CTkButton(
            self,
            text="Export All Transactions to CSV",
            command=self.export_all_transactions
        ).grid(row=6, column=0, padx=20, pady=(0, 15), sticky="ew")

        headings = {
            "id": ("ID", 50),
            "date": ("Date", 110),
            "type": ("Type", 90),
            "category": ("Category", 110),
            "amount": ("Amount", 110),
            "description": ("Description", 300)
        }

        for col, (heading, width) in headings.items():
            self.table.heading(col, text=heading)
            self.table.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.table.yview
        )
        self.table.configure(yscrollcommand=scrollbar.set)

        self.table.grid(row=1, column=0, padx=(12, 0), pady=(0, 12),
                        sticky="nsew")
        scrollbar.grid(row=1, column=1, padx=(0, 12), pady=(0, 12),
                       sticky="ns")

        self.table.bind("<<TreeviewSelect>>", self.select_transaction)

        self.status_label = ctk.CTkLabel(
            self, text="Select a row to edit or delete it."
        )
        self.status_label.grid(row=4, column=0, padx=20, pady=(0, 10),
                               sticky="w")

    def validate_form(self):
        transaction_type = self.type_var.get().strip().lower()
        amount_text = self.amount_var.get().strip()
        category = self.category_var.get().strip()
        date_text = self.date_var.get().strip()
        description = self.description_var.get().strip()

        if not amount_text or not category or not date_text:
            raise ValueError("Please fill in the amount, category and date.")

        if transaction_type not in ("income", "expense"):
            raise ValueError("Choose income or expense.")

        if category not in CATEGORIES:
            raise ValueError("Choose a valid category.")

        if not description:
            raise ValueError("Please enter a description.")

        try:
            amount = float(amount_text)
        except ValueError:
            raise ValueError("Amount must be a valid number, e.g. 2500.")

        if amount <= 0 or amount == float("inf") or amount != amount:
            raise ValueError("Amount must be a positive, finite number.")

        try:
            date.fromisoformat(date_text)
        except ValueError:
            raise ValueError("Date must be a real date in YYYY-MM-DD format.")

        return Transaction(
            transaction_type=transaction_type,
            amount=amount,
            category=category,
            transaction_date=date_text,
            description=description
        )

    def add_transaction(self):
        try:
            transaction = self.validate_form()
            self.database.add_transaction(transaction)
            self.clear_form()
            self.load_transactions()
            messagebox.showinfo("Success", "Transaction added.")
        except (ValueError, TypeError) as error:
            messagebox.showerror("Invalid Input", str(error))
        except Exception as error:
            messagebox.showerror("Database Error", str(error))

    def load_transactions(self):
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            transactions = self.database.get_transactions(
                transaction_type=self.filter_type_var.get(),
                category=self.filter_category_var.get(),
                search=self.search_var.get()
            )

            for transaction in transactions:
                self.table.insert(
                    "", "end",
                    values=(
                        transaction["id"],
                        transaction["transaction_date"],
                        transaction["transaction_type"].title(),
                        transaction["category"],
                        f'{transaction["amount"]:,.2f}',
                        transaction["description"]
                    )
                )

            self.status_label.configure(
                text=f"{len(transactions)} transaction(s) displayed. "
                     "Select a row to edit or delete it."
            )
        except Exception as error:
            messagebox.showerror("Loading Error", str(error))

    def select_transaction(self, _event=None):
        selected = self.table.selection()
        if not selected:
            return

        values = self.table.item(selected[0], "values")
        self.selected_id = int(values[0])

        self.date_var.set(values[1])
        self.type_var.set(values[2].lower())
        self.category_var.set(values[3])
        self.amount_var.set(str(values[4]).replace(",", ""))
        self.description_var.set(values[5])

        self.status_label.configure(
            text=f"Selected transaction ID: {self.selected_id}"
        )

    def update_transaction(self):
        if self.selected_id is None:
            messagebox.showwarning(
                "No Selection", "Select a transaction row first."
            )
            return

        try:
            transaction = self.validate_form()
            updated = self.database.update_transaction(
                self.selected_id, transaction
            )

            if updated:
                self.clear_form()
                self.load_transactions()
                messagebox.showinfo("Success", "Transaction updated.")
            else:
                messagebox.showwarning(
                    "Not Found", "This transaction no longer exists."
                )
        except (ValueError, TypeError) as error:
            messagebox.showerror("Invalid Input", str(error))
        except Exception as error:
            messagebox.showerror("Update Error", str(error))

    def delete_transaction(self):
        if self.selected_id is None:
            messagebox.showwarning(
                "No Selection", "Select a transaction row first."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete transaction ID {self.selected_id}? This cannot be undone."
        )
        if not confirm:
            return

        try:
            deleted = self.database.delete_transaction(self.selected_id)
            if deleted:
                self.clear_form()
                self.load_transactions()
                messagebox.showinfo("Deleted", "Transaction deleted.")
            else:
                messagebox.showwarning(
                    "Not Found", "This transaction no longer exists."
                )
        except Exception as error:
            messagebox.showerror("Delete Error", str(error))

    def clear_form(self):
        self.selected_id = None
        self.type_var.set("expense")
        self.amount_var.set("")
        self.category_var.set("Food")
        self.date_var.set(date.today().isoformat())
        self.description_var.set("")
        for item in self.table.selection():
            self.table.selection_remove(item)
        self.status_label.configure(
            text="Form cleared. Select a row to edit or delete it."
        )

    def reset_filters(self):
        self.search_var.set("")
        self.filter_type_var.set("All")
        self.filter_category_var.set("All")
        self.load_transactions()

    
    def open_reports(self):
        window = ctk.CTkToplevel(self)
        window.title("Monthly Summary & Budget Reports")
        window.geometry("760x700")
        window.transient(self)

        month_var = ctk.StringVar(value=date.today().strftime("%Y-%m"))
        category_var = ctk.StringVar(value="Food")
        budget_var = ctk.StringVar()

        ctk.CTkLabel(
            window,
            text="Monthly Financial Report",
            font=ctk.CTkFont(size=23, weight="bold")
        ).pack(padx=20, pady=(20, 10))

        controls = ctk.CTkFrame(window)
        controls.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            controls, text="Month (YYYY-MM)"
        ).grid(row=0, column=0, padx=10, pady=10)

        ctk.CTkEntry(
            controls, textvariable=month_var, width=150
        ).grid(row=0, column=1, padx=10, pady=10)

        summary_text = ctk.CTkTextbox(
            window, height=170, width=680
        )
        summary_text.pack(fill="x", padx=20, pady=10)

        budget_frame = ctk.CTkFrame(window)
        budget_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            budget_frame, text="Category"
        ).grid(row=0, column=0, padx=10, pady=10)

        ctk.CTkComboBox(
            budget_frame,
            variable=category_var,
            values=CATEGORIES,
            state="readonly",
            width=150
        ).grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(
            budget_frame, text="Monthly budget"
        ).grid(row=0, column=2, padx=10, pady=10)

        ctk.CTkEntry(
            budget_frame,
            textvariable=budget_var,
            placeholder_text="Enter amount",
            width=130
        ).grid(row=0, column=3, padx=10, pady=10)

        budget_text = ctk.CTkTextbox(
            window, height=200, width=680
        )
        budget_text.pack(fill="both", expand=True, padx=20, pady=10)

        def refresh_report():
            month = month_var.get().strip()

            try:
                # Validate YYYY-MM before querying the database.
                from datetime import datetime
                datetime.strptime(month, "%Y-%m")

                summary = self.database.get_monthly_summary(month)
                categories = self.database.get_category_summary(month)
                comparisons = self.database.get_budget_comparison(month)

                summary_text.configure(state="normal")
                summary_text.delete("1.0", "end")
                summary_text.insert(
                    "end",
                    f"MONTH: {month}\n"
                    f"Total income:   {summary['total_income']:,.2f}\n"
                    f"Total expenses: {summary['total_expenses']:,.2f}\n"
                    f"Balance:        {summary['balance']:,.2f}\n\n"
                    "EXPENSES BY CATEGORY\n"
                )

                if categories:
                    for item in categories:
                        summary_text.insert(
                            "end",
                            f"  {item['category']}: {item['total']:,.2f}\n"
                        )
                else:
                    summary_text.insert("end", "  No expenses recorded.\n")

                summary_text.configure(state="disabled")

                budget_text.configure(state="normal")
                budget_text.delete("1.0", "end")
                budget_text.insert("end", "BUDGET VS ACTUAL\n")

                if comparisons:
                    for item in comparisons:
                        budget_text.insert(
                            "end",
                            f"{item['category']}: "
                            f"Budget {item['budget']:,.2f} | "
                            f"Actual {item['actual']:,.2f} | "
                            f"Remaining {item['remaining']:,.2f} | "
                            f"{item['status']}\n"
                        )
                else:
                    budget_text.insert(
                        "end",
                        "No budgets set for this month yet.\n"
                    )

                budget_text.configure(state="disabled")

            except ValueError:
                messagebox.showerror(
                    "Invalid Month",
                    "Enter a valid month in YYYY-MM format, e.g. 2026-10.",
                    parent=window
                )
            except Exception as error:
                messagebox.showerror(
                    "Report Error", str(error), parent=window
                )

        def save_budget():
            try:
                self.database.set_budget(
                    month_var.get().strip(),
                    category_var.get(),
                    budget_var.get()
                )
                refresh_report()
                messagebox.showinfo(
                    "Budget Saved", "Monthly budget saved successfully.",
                    parent=window
                )
            except (ValueError, TypeError) as error:
                messagebox.showerror(
                    "Invalid Budget", str(error), parent=window
                )
            except Exception as error:
                messagebox.showerror(
                    "Budget Error", str(error), parent=window
                )

        def export_report():
            month = month_var.get().strip()
            filename = filedialog.asksaveasfilename(
                parent=window,
                title="Save Monthly Report",
                defaultextension=".csv",
                initialfile=f"monthly_report_{month}.csv",
                filetypes=[("CSV files", "*.csv")]
            )
            if not filename:
                return

            try:
                saved_path = export_monthly_report(
                    self.database, month, filename
                )
                messagebox.showinfo(
                    "Export Complete",
                    f"Report saved to:\n{saved_path}",
                    parent=window
                )
            except Exception as error:
                messagebox.showerror(
                    "Export Error", str(error), parent=window
                )

        ctk.CTkButton(
            controls, text="View Summary",
            command=refresh_report
        ).grid(row=0, column=2, padx=10, pady=10)

        ctk.CTkButton(
            budget_frame, text="Save Budget",
            command=save_budget
        ).grid(row=0, column=4, padx=10, pady=10)

        ctk.CTkButton(
            window, text="Export Monthly Report (CSV)",
            command=export_report
        ).pack(pady=(0, 15))

        refresh_report()

    def export_all_transactions(self):
        filename = filedialog.asksaveasfilename(
            parent=self,
            title="Export Transactions",
            defaultextension=".csv",
            initialfile="transactions.csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if not filename:
            return

        try:
            saved_path = export_transactions(self.database, filename)
            messagebox.showinfo(
                "Export Complete",
                f"Transactions exported to:\n{saved_path}"
            )
        except Exception as error:
            messagebox.showerror("Export Error", str(error))


if __name__ == "__main__":
    app = ExpenseApp()
    app.mainloop()
