import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
from datetime import datetime, timedelta


class RepairApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Tech Spot Mobile Repair System")
        self.geometry("1200x800")

        self.create_db()

        # Display shop name
        self.shop_name_label = tk.Label(
            self, text="Tech Spot", font=('Helvetica', 40, 'bold'))
        self.shop_name_label.pack(pady=10)

        # Create main frames
        self.create_repair_frame()
        self.create_summary_frame()
        self.create_chart_frame()

    def create_db(self):
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
                                      command=lambda: self.calculate_summary('daily'), font=font)
        self.daily_button.grid(row=0, column=0, padx=10, pady=10)

        self.weekly_button = tk.Button(self.summary_frame, text="Weekly Summary",
                                       command=lambda: self.calculate_summary('weekly'), font=font)
        self.weekly_button.grid(row=0, column=1, padx=10, pady=10)

        self.monthly_button = tk.Button(
            self.summary_frame, text="Monthly Summary", command=lambda: self.calculate_summary('monthly'), font=font)
        self.monthly_button.grid(row=0, column=2, padx=10, pady=10)

        self.load_repairs_button = tk.Button(
            self.summary_frame, text="Load Repairs", command=self.load_repairs, font=font)
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

    def add_repair(self):
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        description = self.description_entry.get()
        cost = self.cost_entry.get()
        income = self.income_entry.get()

        if not description or not cost or not income:
            messagebox.showerror(
                "Input Error", "Please enter description, cost, and income.")
            return

        self.cursor.execute('INSERT INTO repairs (date, description, cost, income) VALUES (?, ?, ?, ?)',
                            (date, description, float(cost), float(income)))
        self.conn.commit()

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

        self.cursor.execute('SELECT * FROM repairs')
        for row in self.cursor.fetchall():
            self.repair_tree.insert('', tk.END, values=row)

    def calculate_summary(self, period):
        if period == 'daily':
            start_date = datetime.now().strftime('%Y-%m-%d')
        elif period == 'weekly':
            start_date = (datetime.now() - timedelta(days=7)
                          ).strftime('%Y-%m-%d')
        elif period == 'monthly':
            start_date = (datetime.now() - timedelta(days=30)
                          ).strftime('%Y-%m-%d')

        self.cursor.execute(
            'SELECT date, SUM(cost), SUM(income) FROM repairs WHERE date >= ? GROUP BY date', (start_date,))
        data = self.cursor.fetchall()

        summary_text = f"{period.capitalize()} Summary:\n"
        total_cost = 0
        total_income = 0

        for row in data:
            summary_text += f"Date: {row[0]
                                     }, Cost: {row[1]}, Income: {row[2]}\n"
            total_cost += row[1]
            total_income += row[2]

        summary_text += f"\nTotal Cost: {total_cost}\nTotal Income: {
            total_income}\nNet Profit: {total_income - total_cost}"

        popup = tk.Toplevel(self)
        popup.title(f"{period.capitalize()} Summary")
        popup.geometry("600x400")

        summary_label = tk.Label(popup, text=summary_text, font=(
            'Helvetica', 12), justify='left')
        summary_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def update_charts(self):
        self.plot_chart('daily', self.daily_chart, 'lightblue')
        self.plot_chart('weekly', self.weekly_chart, 'lightgreen')
        self.plot_chart('monthly', self.monthly_chart, 'lightcoral')

    def plot_chart(self, period, frame, color):
        if period == 'daily':
            start_date = datetime.now().strftime('%Y-%m-%d')
        elif period == 'weekly':
            start_date = (datetime.now() - timedelta(days=7)
                          ).strftime('%Y-%m-%d')
        elif period == 'monthly':
            start_date = (datetime.now() - timedelta(days=30)
                          ).strftime('%Y-%m-%d')

        self.cursor.execute(
            'SELECT description, SUM(cost), SUM(income) FROM repairs WHERE date >= ? GROUP BY description', (start_date,))
        data = self.cursor.fetchall()

        descriptions = [row[0] for row in data]
        costs = [row[1] for row in data]
        incomes = [row[2] for row in data]

        # Aggregate data to avoid too many small bars
        if len(descriptions) > 8:
            descriptions = descriptions[:7] + ["Other"]
            costs = costs[:7] + [sum(costs[7:])]
            incomes = incomes[:7] + [sum(incomes[7:])]

        figure = Figure(figsize=(8, 6), dpi=100)
        ax = figure.add_subplot(111)
        ax.bar(descriptions, costs, color=color)
        ax.set_title(f"{period.capitalize()} Repair Costs")
        ax.set_xlabel("Descriptions")
        ax.set_ylabel("Costs")
        ax.tick_params(axis='x', rotation=45)

        for widget in frame.winfo_children():
            if isinstance(widget, FigureCanvasTkAgg):
                widget.get_tk_widget().destroy()

        canvas = FigureCanvasTkAgg(figure, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        figure_income = Figure(figsize=(8, 6), dpi=100)
        ax_income = figure_income.add_subplot(111)
        ax_income.bar(descriptions, incomes, color=color)
        ax_income.set_title(f"{period.capitalize()} Repair Incomes")
        ax_income.set_xlabel("Descriptions")
        ax_income.set_ylabel("Incomes")
        ax_income.tick_params(axis='x', rotation=45)

        for widget in frame.winfo_children():
            if isinstance(widget, FigureCanvasTkAgg):
                widget.get_tk_widget().destroy()

        canvas_income = FigureCanvasTkAgg(figure_income, frame)
        canvas_income.draw()
        canvas_income.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def day_end(self):
        self.calculate_summary('daily')


if __name__ == "__main__":
    app = RepairApp()
    app.mainloop()
