import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import csv
from datetime import datetime, timedelta

class ExpenseTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker")
        self.geometry("800x600")

        # Predefined categories for validation
        self.categories = ['Food', 'Transport', 'Utilities', 'Entertainment', 'Shopping', 'Health', 'Other']
        self.expenses = []  # In-memory list of expenses
        self.data_file = "expenses.csv"  # Storage file

        # Load existing expenses
        self.load_expenses()

        # Set up GUI components
        self.create_menu()
        self.create_tabs()

        # Update summary when tab changes
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def load_expenses(self):
        """Load expenses from the CSV file."""
        try:
            with open(self.data_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                self.expenses = list(reader)
        except FileNotFoundError:
            # Create file with headers if it doesn't exist
            with open(self.data_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['date', 'category', 'amount', 'description'])
                writer.writeheader()

    def save_expenses(self):
        """Save expenses to the CSV file."""
        with open(self.data_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['date', 'category', 'amount', 'description'])
            writer.writeheader()
            writer.writerows(self.expenses)

    def create_menu(self):
        """Create the menu bar with File and Help options."""
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_tabs(self):
        """Create the tabbed interface."""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        self.add_tab = ttk.Frame(self.notebook)
        self.view_tab = ttk.Frame(self.notebook)
        self.summary_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.add_tab, text="Add Expense")
        self.notebook.add(self.view_tab, text="View Expenses")
        self.notebook.add(self.summary_tab, text="Show Summary")

        self.create_add_tab()
        self.create_view_tab()
        self.create_summary_tab()

    def create_add_tab(self):
        """Set up the Add Expense tab."""
        # Date
        ttk.Label(self.add_tab, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.date_entry = ttk.Entry(self.add_tab)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))  # Default to today

        # Category
        ttk.Label(self.add_tab, text="Category:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.category_combo = ttk.Combobox(self.add_tab, values=self.categories, state='readonly')
        self.category_combo.grid(row=1, column=1, padx=5, pady=5)

        # Amount
        ttk.Label(self.add_tab, text="Amount:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.amount_entry = ttk.Entry(self.add_tab)
        self.amount_entry.grid(row=2, column=1, padx=5, pady=5)

        # Description
        ttk.Label(self.add_tab, text="Description:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.desc_entry = ttk.Entry(self.add_tab)
        self.desc_entry.grid(row=3, column=1, padx=5, pady=5)

        # Add button
        self.add_button = ttk.Button(self.add_tab, text="Add Expense", command=self.add_expense)
        self.add_button.grid(row=4, column=0, columnspan=2, pady=10)

    def add_expense(self):
        """Handle adding a new expense."""
        date = self.date_entry.get().strip()
        category = self.category_combo.get()
        amount = self.amount_entry.get().strip()
        description = self.desc_entry.get().strip()

        # Basic validation
        if not date or not category or not amount or not description:
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number.")
            return

        # Add expense
        expense = {'date': date, 'category': category, 'amount': str(amount), 'description': description}
        self.expenses.append(expense)
        self.save_expenses()
        messagebox.showinfo("Success", "Expense added successfully.")

        # Clear fields
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.category_combo.set('')
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)

    def create_view_tab(self):
        """Set up the View Expenses tab."""
        # Filter type
        ttk.Label(self.view_tab, text="Filter by:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.filter_type = tk.StringVar()
        self.filter_combo = ttk.Combobox(self.view_tab, textvariable=self.filter_type, values=["All", "Month", "Week"], state='readonly')
        self.filter_combo.grid(row=0, column=1, padx=5, pady=5)
        self.filter_combo.bind("<<ComboboxSelected>>", self.update_filter_options)

        # Month filter inputs
        self.month_frame = ttk.Frame(self.view_tab)
        ttk.Label(self.month_frame, text="Year:").grid(row=0, column=0, sticky='w')
        self.year_entry = ttk.Entry(self.month_frame, width=5)
        self.year_entry.grid(row=0, column=1)
        ttk.Label(self.month_frame, text="Month:").grid(row=0, column=2, sticky='w')
        self.month_entry = ttk.Entry(self.month_frame, width=3)
        self.month_entry.grid(row=0, column=3)

        # Week filter inputs
        self.week_frame = ttk.Frame(self.view_tab)
        ttk.Label(self.week_frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, sticky='w')
        self.start_date_entry = ttk.Entry(self.week_frame)
        self.start_date_entry.grid(row=0, column=1)

        # Apply filter button
        self.apply_button = ttk.Button(self.view_tab, text="Apply Filter", command=self.apply_filter)
        self.apply_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Treeview for displaying expenses
        self.tree = ttk.Treeview(self.view_tab, columns=('date', 'category', 'amount', 'description'), show='headings')
        self.tree.heading('date', text='Date')
        self.tree.heading('category', text='Category')
        self.tree.heading('amount', text='Amount')
        self.tree.heading('description', text='Description')
        self.tree.grid(row=3, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)

        # Configure grid to expand Treeview
        self.view_tab.grid_rowconfigure(3, weight=1)
        self.view_tab.grid_columnconfigure(1, weight=1)

        # Initial setup
        self.filter_type.set("All")
        self.update_filter_options()

    def update_filter_options(self, event=None):
        """Show/hide filter input fields based on selected filter type."""
        filter_type = self.filter_type.get()
        if filter_type == "All":
            self.month_frame.grid_remove()
            self.week_frame.grid_remove()
        elif filter_type == "Month":
            self.month_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
            self.week_frame.grid_remove()
        elif filter_type == "Week":
            self.week_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
            self.month_frame.grid_remove()

    def apply_filter(self):
        """Apply the selected filter and update the Treeview."""
        filter_type = self.filter_type.get()
        if filter_type == "All":
            filtered_expenses = self.expenses
        elif filter_type == "Month":
            year = self.year_entry.get().strip()
            month = self.month_entry.get().strip()
            if not year.isdigit() or not month.isdigit():
                messagebox.showerror("Error", "Year and month must be numbers.")
                return
            year = int(year)
            month = int(month)
            if month < 1 or month > 12:
                messagebox.showerror("Error", "Month must be between 1 and 12.")
                return
            filtered_expenses = [
                exp for exp in self.expenses
                if datetime.strptime(exp['date'], "%Y-%m-%d").year == year and
                   datetime.strptime(exp['date'], "%Y-%m-%d").month == month
            ]
        elif filter_type == "Week":
            start_date_str = self.start_date_entry.get().strip()
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                end_date = start_date + timedelta(days=7)
                filtered_expenses = [
                    exp for exp in self.expenses
                    if start_date <= datetime.strptime(exp['date'], "%Y-%m-%d") < end_date
                ]
            except ValueError:
                messagebox.showerror("Error", "Invalid start date format. Use YYYY-MM-DD.")
                return

        # Sort by date
        filtered_expenses.sort(key=lambda x: x['date'])

        # Clear and populate Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        for exp in filtered_expenses:
            self.tree.insert('', 'end', values=(exp['date'], exp['category'], exp['amount'], exp['description']))

    def create_summary_tab(self):
        """Set up the Summary tab."""
        self.summary_label = ttk.Label(self.summary_tab, text="Summary will be shown here.")
        self.summary_label.grid(row=0, column=0, padx=5, pady=5)

    def update_summary(self):
        """Update the summary display."""
        total = sum(float(exp['amount']) for exp in self.expenses) if self.expenses else 0
        category_totals = {
            cat: sum(float(exp['amount']) for exp in self.expenses if exp['category'] == cat)
            for cat in self.categories
        }

        summary_text = f"Total Expenses: ${total:.2f}\n\nBy Category:\n"
        for cat, amount in category_totals.items():
            summary_text += f"{cat}: ${amount:.2f}\n"
        self.summary_label.config(text=summary_text)

    def on_tab_changed(self, event):
        """Update display when tab is changed."""
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        if tab_text == "Show Summary":
            self.update_summary()

    def export_data(self):
        """Export expenses to a user-specified CSV file."""
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            try:
                with open(filename, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=['date', 'category', 'amount', 'description'])
                    writer.writeheader()
                    writer.writerows(self.expenses)
                messagebox.showinfo("Success", "Data exported successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {e}")

    def show_about(self):
        """Show the About dialog."""
        messagebox.showinfo("About", "Expense Tracker\nVersion 1.0\nCreated by [Your Name]")

if __name__ == "__main__":
    app = ExpenseTrackerApp()
    app.mainloop()