import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os


class RepairApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Tech Spot Mobile Repair System")
        self.geometry("1200x800")

        try:
            self.create_db()
        except sqlite3.Error as e:
            messagebox.showerror(
                "Database Error", f"Failed to create database: {e}")
            self.destroy()
            return

        # Display shop name
        self.shop_name_label = tk.Label(
            self, text="Tech Spot", font=('Helvetica', 40, 'bold'))
        self.shop_name_label.pack(pady=10)

        # Create main frames
        self.create_repair_frame()
        self.create_summary_frame()
        self.create_chart_frame()

    def create_db(self):
        try:
            self.conn = sqlite3.connect('repairs.db')
            self.cursor = self.conn.cursor()

            # Create repairs table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS repairs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    description TEXT NOT NULL,
                    cost REAL NOT NULL,
                    income REAL NOT NULL
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Database error: {e}")

    def create_repair_frame(self):
        self.repair_frame = ttk.LabelFrame(self, text="Add Repair")
        self.repair_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        font = ('Helvetica', 12)

        ttk.Label(self.repair_frame, text="Description:",
                  font=font).grid(row=0, column=0, padx=5, pady=5)
        self.description_entry = ttk.Entry(
            self.repair_frame, font=font, width=40)
        self.description_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.repair_frame, text="Cost:", font=font).grid(
            row=1, column=0, padx=5, pady=5)
        self.cost_entry = ttk.Entry(self.repair_frame, font=font, width=20)
        self.cost_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.repair_frame, text="Income:", font=font).grid(
            row=2, column=0, padx=5, pady=5)
        self.income_entry = ttk.Entry(self.repair_frame, font=font, width=20)
        self.income_entry.grid(row=2, column=1, padx=5, pady=5)

        self.add_repair_button = tk.Button(
            self.repair_frame, text="Add Repair", command=self.add_repair, font=font)
        self.add_repair_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.clear_entries_button = tk.Button(
            self.repair_frame, text="Clear Entries", command=self.clear_entries, font=font)
        self.clear_entries_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.repair_tree = ttk.Treeview(self.repair_frame, columns=(
            "id", "date", "description", "cost", "income"), show="headings", height=10)
        self.repair_tree.heading("id", text="ID")
        self.repair_tree.heading("date", text="Date")
        self.repair_tree.heading("description", text="Description")
        self.repair_tree.heading("cost", text="Cost")
        self.repair_tree.heading("income", text="Income")
        self.repair_tree.grid(row=5, column=0, columnspan=2, sticky='nsew')

        self.repair_frame.grid_rowconfigure(5, weight=1)
        self.repair_frame.grid_columnconfigure(1, weight=1)

        self.load_repairs()

    def create_summary_frame(self):
        self.summary_frame = ttk.LabelFrame(self, text="Summary")
        self.summary_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        font = ('Helvetica', 12)

        self.daily_button = tk.Button(self.summary_frame, text="Daily Summary",
                                      command=lambda: self.calculate_summary('daily'), font=font, width=20)
        self.daily_button.grid(row=0, column=0, padx=10, pady=10)

        self.weekly_button = tk.Button(self.summary_frame, text="Weekly Summary",
                                       command=lambda: self.calculate_summary('weekly'), font=font, width=20)
        self.weekly_button.grid(row=0, column=1, padx=10, pady=10)

        self.monthly_button = tk.Button(
            self.summary_frame, text="Monthly Summary", command=lambda: self.calculate_summary('monthly'), font=font, width=20)
        self.monthly_button.grid(row=0, column=2, padx=10, pady=10)

        self.load_repairs_button = tk.Button(
            self.summary_frame, text="Load Repairs", command=self.load_repairs, font=font, width=20)
        self.load_repairs_button.grid(row=0, column=3, padx=10, pady=10)

    def create_chart_frame(self):
        self.chart_frame = ttk.LabelFrame(self, text="Charts")
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.daily_chart = ttk.LabelFrame(self.chart_frame, text="Daily Chart")
        self.daily_chart.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.weekly_chart = ttk.LabelFrame(
            self.chart_frame, text="Weekly Chart")
        self.weekly_chart.grid(row=0, column=1, padx=10,
                               pady=10, sticky='nsew')

        self.monthly_chart = ttk.LabelFrame(
            self.chart_frame, text="Monthly Chart")
        self.monthly_chart.grid(
            row=0, column=2, padx=10, pady=10, sticky='nsew')

        self.chart_frame.grid_rowconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(1, weight=1)
        self.chart_frame.grid_columnconfigure(2, weight=1)

        self.update_charts()

        self.create_report_buttons()

    def create_report_buttons(self):
        font = ('Helvetica', 12)

        self.daily_report_button = tk.Button(
            self.daily_chart, text="Generate Daily Report", command=lambda: self.generate_report('daily'), font=font, bg='lightblue', width=20, height=2)
        self.daily_report_button.pack(padx=10, pady=10)

        self.weekly_report_button = tk.Button(
            self.weekly_chart, text="Generate Weekly Report", command=lambda: self.generate_report('weekly'), font=font, bg='lightgreen', width=20, height=2)
        self.weekly_report_button.pack(padx=10, pady=10)

        self.monthly_report_button = tk.Button(
            self.monthly_chart, text="Generate Monthly Report", command=lambda: self.generate_report('monthly'), font=font, bg='lightcoral', width=20, height=2)
        self.monthly_report_button.pack(padx=10, pady=10)

    def add_repair(self):
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        description = self.description_entry.get()
        cost = self.cost_entry.get()
        income = self.income_entry.get()

        if not description or not cost or not income:
            messagebox.showerror(
                "Input Error", "Please enter description, cost, and income.")
            return

        try:
            cost = float(cost)
            income = float(income)
        except ValueError:
            messagebox.showerror(
                "Input Error", "Cost and income must be numeric values.")
            return

        try:
            self.cursor.execute('INSERT INTO repairs (date, description, cost, income) VALUES (?, ?, ?, ?)',
                                (date, description, cost, income))
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror(
                "Database Error", f"Failed to add repair: {e}")
            return

        self.clear_entries()
        self.load_repairs()
        self.update_charts()

    def clear_entries(self):
        self.description_entry.delete(0, tk.END)
        self.cost_entry.delete(0, tk.END)
        self.income_entry.delete(0, tk.END)

    def load_repairs(self):
        for item in self.repair_tree.get_children():
            self.repair_tree.delete(item)

        try:
            self.cursor.execute('SELECT * FROM repairs')
            for row in self.cursor.fetchall():
                self.repair_tree.insert('', tk.END, values=row)
        except sqlite3.Error as e:
            messagebox.showerror(
                "Database Error", f"Failed to load repairs: {e}")

    def calculate_summary(self, period):
        if period == 'daily':
            start_date = datetime.now().strftime('%Y-%m-%d')
        elif period == 'weekly':
            start_date = (datetime.now() - timedelta(days=7)
                          ).strftime('%Y-%m-%d')
        elif period == 'monthly':
            start_date = (datetime.now() - timedelta(days=30)
                          ).strftime('%Y-%m-%d')
        else:
            messagebox.showerror("Input Error", "Invalid period specified.")
            return

        try:
            self.cursor.execute(
                'SELECT date, SUM(cost), SUM(income) FROM repairs WHERE date >= ? GROUP BY date ORDER BY date', (start_date,))
            data = self.cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror(
                "Database Error", f"Failed to calculate summary: {e}")
            return

        if not data:
            messagebox.showinfo(
                f"{period.capitalize()} Summary", "No data available for the selected period.")
            return

        summary_text = f"{period.capitalize()} Summary:\n\n"
        total_cost = 0
        total_income = 0

        for row in data:
            summary_text += f"Date: {row[0]}\n"
            summary_text += f"Cost: ${row[1]:,.2f}\n"
            summary_text += f"Income: ${row[2]:,.2f}\n"
            net_profit = row[2] - row[1]
            summary_text += f"Net Profit: ${net_profit:,.2f}\n"
            total_cost += row[1]
            total_income += row[2]

        net_profit = total_income - total_cost
        summary_text += f"\nTotal Cost: ${total_cost:,.2f}\n"
        summary_text += f"Total Income: ${total_income:,.2f}\n"
        summary_text += f"Net Profit: ${net_profit:,.2f}\n"

        messagebox.showinfo("Summary", summary_text)

    def generate_report(self, period):
        report_file = f'{period}_report.pdf'

        try:
            c = canvas.Canvas(report_file, pagesize=letter)
            width, height = letter

            c.setFont('Helvetica-Bold', 16)
            c.drawString(100, height - 50, f'{period.capitalize()} Report')

            c.setFont('Helvetica', 12)
            c.drawString(100, height - 100, 'Date, Cost, Income, Net Profit')

            self.cursor.execute(
                'SELECT date, SUM(cost), SUM(income) FROM repairs WHERE date >= ? GROUP BY date ORDER BY date',
                (self.get_start_date(period),))
            rows = self.cursor.fetchall()

            y_position = height - 130
            for row in rows:
                net_profit = row[2] - row[1]
                c.drawString(100, y_position, f'{row[0]}, ${row[1]:,.2f}, ${
                             row[2]:,.2f}, ${net_profit:,.2f}')
                y_position -= 20

            c.save()
            messagebox.showinfo("Report Generated",
                                f"Report saved as {report_file}")
        except Exception as e:
            messagebox.showerror(
                "File Error", f"Failed to generate report: {e}")

    def get_start_date(self, period):
        if period == 'daily':
            return datetime.now().strftime('%Y-%m-%d')
        elif period == 'weekly':
            return (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        elif period == 'monthly':
            return (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        else:
            messagebox.showerror("Input Error", "Invalid period specified.")
            return None

    def update_charts(self):
        # This method is kept for completeness but will not be used as charts are removed
        pass


if __name__ == "__main__":
    app = RepairApp()
    app.mainloop()
