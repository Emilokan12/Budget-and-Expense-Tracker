import tkinter as tk
from tkinter import messagebox, ttk

import logic

BOLD = ("TkDefaultFont", 10, "bold")
HEADING = ("TkDefaultFont", 11, "bold")
TITLE = ("TkDefaultFont", 12, "bold")


class BudgetApp:
    def __init__(self, root):
        self.root = root
        root.title("BET — Budget & Expense Tracker")
        root.geometry("460x480")
        root.resizable(False, False)

        tk.Label(root, text="Budget & Expense Tracker",
                 font=("TkDefaultFont", 14, "bold")).pack(pady=(14, 4))
        self._separator(root, pady=(4, 0))

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=10)

        self._build_budget_tab()
        self._build_expenses_tab()
        self._build_summary_tab()
        self._build_footer()

    @staticmethod
    def _separator(parent, **pack_opts):
        tk.Frame(parent, height=1, relief="sunken", bd=1).pack(
            fill="x", padx=pack_opts.pop("padx", 16), **pack_opts)

    def _new_tab(self, title, heading):
        frame = tk.Frame(self.notebook, padx=20, pady=20)
        self.notebook.add(frame, text=f"  {title}  ")
        tk.Label(frame, text=heading, font=HEADING).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        frame.columnconfigure(1, weight=1)
        return frame

    @staticmethod
    def _labeled_entry(parent, row, label):
        tk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=5)
        entry = tk.Entry(parent, width=28)
        entry.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        return entry

    @staticmethod
    def _button_row(parent, row, buttons, width=14):
        frame = tk.Frame(parent)
        frame.grid(row=row, column=0, columnspan=2, sticky="w", pady=(14, 0))
        for text, command in buttons:
            tk.Button(frame, text=text, command=command, width=width).pack(
                side="left", padx=(0, 8))

    def _build_budget_tab(self):
        tab = self._new_tab("Budget", "Set / View Budget")
        self.budget_entry = self._labeled_entry(tab, 1, "Budget Amount (₦):")
        self._button_row(tab, 2, [("Set Budget", self.set_budget),
                                  ("View Budget", self.view_budget)])

    def _build_expenses_tab(self):
        tab = self._new_tab("Expenses", "Add Expense")
        self.amount_entry = self._labeled_entry(tab, 1, "Amount (₦):")

        tk.Label(tab, text="Category:").grid(row=2, column=0, sticky="w", pady=5)
        self.category_var = tk.StringVar(value=logic.CATEGORY_PLACEHOLDER)
        ttk.Combobox(tab, textvariable=self.category_var, values=logic.CATEGORIES,
                     state="readonly", width=26).grid(
            row=2, column=1, sticky="ew", padx=(10, 0), pady=5)

        self.desc_entry = self._labeled_entry(tab, 3, "Description:")
        self.date_entry = self._labeled_entry(tab, 4, "Date (YYYY-MM-DD):")
        self._button_row(tab, 5, [("Add Expense", self.add_expense),
                                  ("View All", self.view_expenses)])

    def _build_summary_tab(self):
        tab = self._new_tab("Summary", "Monthly Summary")
        self.month_entry = self._labeled_entry(tab, 1, "Month (YYYY-MM):")
        tk.Label(tab, text="e.g. 2025-11", font=("TkDefaultFont", 8)).grid(
            row=2, column=1, sticky="w", padx=(10, 0))
        self._button_row(tab, 3, [("View Summary", self.show_summary)], width=16)

    def _build_footer(self):
        self._separator(self.root)
        footer = tk.Frame(self.root)
        footer.pack(fill="x", padx=16, pady=(8, 12))
        tk.Button(footer, text="Exit", command=self.root.destroy, width=10).pack(side="right")

    def set_budget(self):
        try:
            value = logic.set_budget(self.budget_entry.get())
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return
        messagebox.showinfo("Budget Set", f"₦{value:,.2f} set as your budget")
        self.budget_entry.delete(0, tk.END)

    def view_budget(self):
        value = logic.get_budget()
        if value is None:
            messagebox.showwarning("No Budget", "No budget set yet")
        else:
            messagebox.showinfo("Your Budget", f"₦{value:,.2f}")

    def add_expense(self):
        try:
            logic.add_expense(self.amount_entry.get(), self.category_var.get(),
                              self.desc_entry.get(), self.date_entry.get())
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return
        messagebox.showinfo("Added", "Expense recorded successfully")
        for entry in (self.amount_entry, self.desc_entry, self.date_entry):
            entry.delete(0, tk.END)
        self.category_var.set(logic.CATEGORY_PLACEHOLDER)

    def view_expenses(self):
        expenses, total, remaining = logic.get_expenses_report()
        if not expenses:
            messagebox.showinfo("Info", "No expenses recorded yet.")
            return

        win = tk.Toplevel(self.root)
        win.title("All Expenses")
        win.geometry("580x420")
        win.resizable(False, False)
        tk.Label(win, text="Expense History", font=TITLE).pack(pady=(12, 6))

        cols = ("Category", "Description", "Amount (₦)", "Date")
        widths = {"Category": 110, "Description": 230, "Amount (₦)": 110, "Date": 120}

        frame = tk.Frame(win)
        frame.pack(fill="both", expand=True, padx=12, pady=(0, 6))
        sb = ttk.Scrollbar(frame, orient="vertical")
        sb.pack(side="right", fill="y")
        tree = ttk.Treeview(frame, columns=cols, show="headings", yscrollcommand=sb.set)
        sb.config(command=tree.yview)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=widths[col], anchor="center")
        tree.pack(fill="both", expand=True)

        for e in expenses:
            tree.insert("", tk.END, values=(e.category, e.description,
                                            f"{e.amount:,.2f}", e.date))

        footer = tk.Frame(win)
        footer.pack(fill="x", padx=12, pady=6)
        tk.Label(footer, text=f"Total Spent: ₦{total:,.2f}", font=BOLD).pack(side="left")
        if remaining is not None:
            tk.Label(footer, text=f"Remaining: ₦{remaining:,.2f}", font=BOLD).pack(side="right")

    def show_summary(self):
        month = self.month_entry.get().strip()
        try:
            rows, total = logic.get_monthly_summary(month)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return
        except LookupError as e:
            messagebox.showinfo("No Data", str(e))
            return

        win = tk.Toplevel(self.root)
        win.title(f"Summary — {month}")
        win.geometry("340x300")
        win.resizable(False, False)
        tk.Label(win, text=f"{month} Summary", font=TITLE).pack(pady=(12, 8))

        for r in rows:
            row_f = tk.Frame(win)
            row_f.pack(fill="x", padx=20, pady=3)
            tk.Label(row_f, text=r.category).pack(side="left")
            tk.Label(row_f, text=f"₦{r.total:,.2f}", font=BOLD).pack(side="right")

        self._separator(win, padx=20, pady=8)
        total_row = tk.Frame(win)
        total_row.pack(fill="x", padx=20)
        tk.Label(total_row, text="Total Spent", font=BOLD).pack(side="left")
        tk.Label(total_row, text=f"₦{total:,.2f}", font=BOLD).pack(side="right")


def main():
    logic.start()
    root = tk.Tk()
    BudgetApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
