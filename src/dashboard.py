
import customtkinter as ctk
from tkinter import messagebox
from datetime import date, datetime

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class DashboardWindow(ctk.CTkToplevel):
    """Displays monthly financial summaries and charts."""

    def __init__(self, parent, database):
        super().__init__(parent)

        self.database = database

        self.title("Financial Dashboard")
        self.geometry("1000x760")
        self.minsize(800, 600)

        self.month_var = ctk.StringVar(
            value=date.today().strftime("%Y-%m")
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_summary_cards()
        self._build_charts()
        self.refresh_dashboard()

    def _build_header(self):
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, padx=18, pady=15, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="Financial Dashboard",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=12, sticky="w")

        ctk.CTkLabel(
            header, text="Month (YYYY-MM)"
        ).grid(row=0, column=1, padx=8, pady=12, sticky="e")

        ctk.CTkEntry(
            header, textvariable=self.month_var, width=130
        ).grid(row=0, column=2, padx=8, pady=12)

        ctk.CTkButton(
            header, text="Refresh",
            command=self.refresh_dashboard, width=100
        ).grid(row=0, column=3, padx=12, pady=12)

    def _build_summary_cards(self):
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.grid(row=1, column=0, padx=18, pady=5, sticky="ew")
        cards.grid_columnconfigure((0, 1, 2), weight=1)

        self.income_label = self._create_card(
            cards, 0, "Total Income"
        )
        self.expense_label = self._create_card(
            cards, 1, "Total Expenses"
        )
        self.balance_label = self._create_card(
            cards, 2, "Balance"
        )

    def _create_card(self, parent, column, title):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(
            row=0, column=column, padx=6, pady=6, sticky="ew"
        )

        ctk.CTkLabel(
            card, text=title,
            font=ctk.CTkFont(size=14)
        ).pack(padx=12, pady=(15, 5))

        value_label = ctk.CTkLabel(
            card,
            text="0.00",
            font=ctk.CTkFont(size=23, weight="bold")
        )
        value_label.pack(padx=12, pady=(0, 15))

        return value_label

    def _build_charts(self):
        chart_frame = ctk.CTkFrame(self)
        chart_frame.grid(
            row=2, column=0, padx=18, pady=12, sticky="nsew"
        )
        chart_frame.grid_columnconfigure((0, 1), weight=1)
        chart_frame.grid_rowconfigure(0, weight=1)

        self.figure = Figure(figsize=(10, 5), dpi=100)
        self.category_axis = self.figure.add_subplot(121)
        self.comparison_axis = self.figure.add_subplot(122)

        self.figure.subplots_adjust(
            left=0.08, right=0.97,
            top=0.88, bottom=0.15, wspace=0.35
        )

        self.canvas = FigureCanvasTkAgg(
            self.figure, master=chart_frame
        )
        self.canvas.get_tk_widget().grid(
            row=0, column=0, columnspan=2,
            padx=8, pady=8, sticky="nsew"
        )

    def refresh_dashboard(self):
        month = self.month_var.get().strip()

        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            messagebox.showerror(
                "Invalid Month",
                "Enter a valid month such as 2026-10.",
                parent=self
            )
            return

        try:
            summary = self.database.get_monthly_summary(month)
            categories = self.database.get_category_summary(month)

            income = summary["total_income"]
            expenses = summary["total_expenses"]
            balance = summary["balance"]

            self.income_label.configure(text=f"{income:,.2f}")
            self.expense_label.configure(text=f"{expenses:,.2f}")
            self.balance_label.configure(text=f"{balance:,.2f}")

            self._draw_category_chart(categories)
            self._draw_comparison_chart(income, expenses)
            self.canvas.draw_idle()

        except Exception as error:
            messagebox.showerror(
                "Dashboard Error", str(error), parent=self
            )

    def _draw_category_chart(self, categories):
        self.category_axis.clear()
        self.category_axis.set_title("Expenses by Category")

        labels = [item["category"] for item in categories]
        values = [float(item["total"]) for item in categories]

        if not values or sum(values) <= 0:
            self.category_axis.text(
                0.5, 0.5, "No expenses this month",
                ha="center", va="center",
                transform=self.category_axis.transAxes
            )
            self.category_axis.set_axis_off()
            return

        self.category_axis.set_axis_on()
        self.category_axis.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90
        )
        self.category_axis.axis("equal")

    def _draw_comparison_chart(self, income, expenses):
        self.comparison_axis.clear()
        self.comparison_axis.set_title("Income vs Expenses")
        self.comparison_axis.set_ylabel("Amount")

        self.comparison_axis.bar(
            ["Income", "Expenses"],
            [income, expenses]
        )
        self.comparison_axis.ticklabel_format(
            axis="y", style="plain"
        )
        self.comparison_axis.grid(
            axis="y", linestyle="--", alpha=0.3
        )
