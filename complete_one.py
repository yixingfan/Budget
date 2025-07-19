import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class BudgetTracker:
    def __init__(self, root):
        self.root = root
        self.data_file = "budget_data.csv"
        self.total_spending = 0.0
        self.total_income = 0.0
        self.spending_history = []
        self.income_history = []
        self.spending_categories = ["Food"]  # Default category
        self.income_categories = ["Salary"]  # Default category
        self.load_data()  # Load existing data
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Budget Tracker")
        self.root.geometry("800x800")  # Increased window size to accommodate the chart

        # Main container frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top frame for labels
        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 20))

        # Display labels
        self.spending_label = tk.Label(top_frame, text=f"Total spending: ${self.total_spending:.2f}", font=("Arial", 12))
        self.spending_label.pack(side=tk.LEFT, padx=10)
        
        self.income_label = tk.Label(top_frame, text=f"Total income: ${self.total_income:.2f}", font=("Arial", 12))
        self.income_label.pack(side=tk.LEFT, padx=10)
        
        balance = self.total_income - self.total_spending
        self.balance_label = tk.Label(top_frame, text=f"Current balance: ${balance:.2f}", font=("Arial", 12, 'bold'))
        self.balance_label.pack(side=tk.LEFT, padx=10)

        # Main title
        tk.Label(main_frame, text="Budget Tracker", font=("Arial", 20)).pack(pady=(0, 20))

        # Create donut chart frame
        self.chart_frame = tk.Frame(main_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Initialize chart
        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.update_chart()

        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)

        
        # Big Income button
        income_btn = tk.Button(
            button_frame,
            text="Income",
            command=self.open_income_window,
            font=("Arial", 12, "bold"),
            width=15,
            height=2,
            padx=10,
            pady=5,
        )
        income_btn.pack(side=tk.LEFT, padx=20, expand=True)

        # Big Spending button
        spending_btn = tk.Button(
            button_frame,
            text="Spending",
            command=self.open_spending_window,
            font=("Arial", 12, "bold"),
            width=15,
            height=2,
            padx=10,
            pady=5,
        )
        spending_btn.pack(side=tk.RIGHT, padx=20, expand=True)

        #tk.Button(button_frame, text="Income", command=self.open_income_window).pack(side=tk.LEFT, padx=20, expand=True)
        #tk.Button(button_frame, text="Spending", command=self.open_spending_window).pack(side=tk.RIGHT, padx=20, expand=True)

    def update_chart(self):
        """Update the donut chart with current income and spending data"""
        # Clear previous chart
        self.ax.clear()
        
        # Only create chart if we have data
        if self.total_income + self.total_spending == 0:
            self.ax.text(0.5, 0.5, "No data available", 
                        ha='center', va='center', fontsize=12)
            self.ax.axis('off')
            self.canvas.draw()
            return

        # Create new chart
        categories = ['Income', 'Spending']
        values = [self.total_income, self.total_spending]
        colors = ['#4CAF50', '#F44336']  # Green for income, red for spending
        
        # Create donut chart
        wedges, texts, autotexts = self.ax.pie(
            values,
            labels=categories,
            colors=colors,
            autopct=lambda p: f'${p * sum(values)/100:,.2f}',
            startangle=90,
            wedgeprops=dict(width=0.4, edgecolor='w'),
            pctdistance=0.85
        )
        
        # Style the percentage labels
        plt.setp(autotexts, size=10, weight="bold", color='white')
        
        # Add title
        self.ax.set_title('Income vs Spending', pad=20, fontsize=12, fontweight='bold')
        
        # Add savings info in center
        savings = self.total_income - self.total_spending
        savings_percent = (savings / self.total_income * 100) if self.total_income > 0 else 0
        center_text = f"Savings: ${savings:,.2f}\n({savings_percent:.1f}%)"
        self.ax.text(0, 0, center_text, ha='center', va='center', fontsize=10, fontweight='bold')
        
        self.canvas.draw()

    def save_data(self):
        """Save all data to CSV using pandas"""
        data = {
            'type': [],
            'category': [],
            'amount': [],
            'timestamp': [],
            'comment': []
        }
        
        for record in self.income_history:
            data['type'].append('income')
            data['category'].append(record['category'])
            data['amount'].append(record['amount'])
            data['timestamp'].append(record['timestamp'])
            data['comment'].append(record.get('comment', ''))
        
        for record in self.spending_history:
            data['type'].append('spending')
            data['category'].append(record['category'])
            data['amount'].append(record['amount'])
            data['timestamp'].append(record['timestamp'])
            data['comment'].append(record.get('comment', ''))
        
        df = pd.DataFrame(data)
        df.to_csv(self.data_file, index=False)

    def load_data(self):
        """Load data from CSV if it exists"""
        if os.path.exists(self.data_file):
            try:
                df = pd.read_csv(self.data_file)
                
                for _, row in df.iterrows():
                    record = {
                        'category': row['category'],
                        'amount': float(row['amount']),
                        'timestamp': row['timestamp'],
                        'comment': row.get('comment', '')
                    }
                    
                    if row['type'] == 'income':
                        self.income_history.append(record)
                        self.total_income += record['amount']
                    else:
                        self.spending_history.append(record)
                        self.total_spending += record['amount']
                
                # Update categories from loaded data
                income_cats = df[df['type'] == 'income']['category'].unique()
                spending_cats = df[df['type'] == 'spending']['category'].unique()
                
                self.income_categories = list(income_cats) if len(income_cats) > 0 else ["Salary"]
                self.spending_categories = list(spending_cats) if len(spending_cats) > 0 else ["Food"]
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {str(e)}")
    
    def update_income(self, amount):
        self.total_income += float(amount)
        self.income_label.config(text=f"Total income: ${self.total_income:.2f}")
        self.update_balance_display()
        self.update_chart()
        
    def update_spending(self, amount):
        self.total_spending += float(amount)
        self.spending_label.config(text=f"Total spending: ${self.total_spending:.2f}")
        self.update_balance_display()
        self.update_chart()
           
    def update_balance_display(self):
        balance = self.total_income - self.total_spending
        self.balance_label.config(text=f"Current balance: ${balance:.2f}")

    def open_income_window(self):
        income_window = tk.Toplevel(self.root)
        income_window.title("Income Manager")
        income_window.geometry("400x450")
        
        # Main container frame
        main_frame = tk.Frame(income_window, padx=10, pady=10)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Category Section
        tk.Label(main_frame, text="Category:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0,5))
        
        category_frame = tk.Frame(main_frame)
        category_frame.grid(row=1, column=0, columnspan=3, sticky='ew')
        
        self.income_category_box = ttk.Combobox(category_frame, values=self.income_categories, state='readonly')
        self.income_category_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        self.income_category_box.current(0)
        
        new_category_entry = tk.Entry(category_frame, width=15)
        new_category_entry.pack(side=tk.LEFT, padx=(0,5))
        
        def manage_category(action):
            if action == 'add':
                new_cat = new_category_entry.get().strip()
                if new_cat and new_cat not in self.income_categories:
                    self.income_categories.append(new_cat)
                    self.income_category_box['values'] = self.income_categories
                    self.income_category_box.set(new_cat)
                    new_category_entry.delete(0, tk.END)
                    self.save_data()
            elif action == 'del':
                if len(self.income_categories) > 1:
                    current = self.income_category_box.get()
                    self.income_categories.remove(current)
                    self.income_category_box['values'] = self.income_categories
                    self.income_category_box.current(0)
                    self.save_data()
        
        btn_frame = tk.Frame(category_frame)
        btn_frame.pack(side=tk.LEFT)
        tk.Button(btn_frame, text="+", width=2, command=lambda: manage_category('add')).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="-", width=2, command=lambda: manage_category('del')).pack(side=tk.LEFT)
        
        # Amount Section
        tk.Label(main_frame, text="Amount ($):", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=(10,5))
        amount_entry = tk.Entry(main_frame, validate='key')
        amount_entry.grid(row=3, column=0, sticky='ew', columnspan=3)
        
        # Comment Section
        tk.Label(main_frame, text="Comment:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=(10,5))
        comment_entry = tk.Entry(main_frame)
        comment_entry.grid(row=5, column=0, sticky='ew', columnspan=3)
        
        # Button Section
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=(15,0))
        
        def save_income():
            try:
                amount = float(amount_entry.get())
                if amount <= 0:
                    raise ValueError
                category = self.income_category_box.get()
                comment = comment_entry.get().strip()
                
                self.update_income(amount)
                self.income_history.append({
                    'category': category,
                    'amount': amount,
                    'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'comment': comment
                })
                
                self.save_data()
                amount_entry.delete(0, tk.END)
                comment_entry.delete(0, tk.END)
                amount_entry.focus()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid positive number")
        
        tk.Button(button_frame, text="Save", command=save_income).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="View History", command=self.show_income_history).pack(side=tk.LEFT, padx=5)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        amount_entry.focus()

    def show_income_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Income History Timeline")
        history_window.geometry("750x400")
        
        if not self.income_history:
            tk.Label(history_window, text="No income history available").pack(pady=20)
            return
            
        container = tk.Frame(history_window)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        header_frame = tk.Frame(container)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="Date/Time", font=('Arial', 9, 'bold'), width=15, anchor='w').pack(side=tk.LEFT)
        tk.Label(header_frame, text="Category", font=('Arial', 9, 'bold'), width=15, anchor='w').pack(side=tk.LEFT)
        tk.Label(header_frame, text="Amount", font=('Arial', 9, 'bold'), width=15, anchor='e').pack(side=tk.LEFT)
        tk.Label(header_frame, text="Comment", font=('Arial', 9, 'bold'), width=20, anchor='w').pack(side=tk.LEFT)
        tk.Label(header_frame, text="Action", font=('Arial', 9, 'bold'), width=10, anchor='center').pack(side=tk.LEFT)
        
        canvas = tk.Canvas(container, borderwidth=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def delete_income_record(index):
            if messagebox.askyesno("Confirm", "Delete this income record?"):
                # Update totals
                self.total_income -= self.income_history[index]['amount']
                # Remove record
                del self.income_history[index]
                # Save changes
                self.save_data()
                # Update main display
                self.income_label.config(text=f"Total income: ${self.total_income:.2f}")
                self.update_balance_display()
                self.update_chart()
                # Refresh history view
                history_window.destroy()
                self.show_income_history()
        
        for idx, record in enumerate(reversed(self.income_history)):
            entry_frame = tk.Frame(scrollable_frame)
            entry_frame.pack(fill=tk.X, pady=2)
            
            tk.Label(entry_frame, text=record['timestamp'], width=15, anchor='w').pack(side=tk.LEFT)
            tk.Label(entry_frame, text=record['category'], width=15, anchor='w').pack(side=tk.LEFT)
            tk.Label(entry_frame, text=f"${record['amount']:.2f}", width=15, anchor='e').pack(side=tk.LEFT)
            tk.Label(entry_frame, text=record.get('comment', ''), width=20, anchor='w').pack(side=tk.LEFT)
            tk.Button(entry_frame, text="Delete", width=8, command=lambda i=idx: delete_income_record(len(self.income_history)-1-i)).pack(side=tk.LEFT, padx=5)
        
        total_frame = tk.Frame(container)
        total_frame.pack(fill=tk.X, pady=(10,0))
        tk.Label(total_frame, text="Total Income:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(20,0))
        tk.Label(total_frame, text=f"${self.total_income:.2f}", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        
        tk.Button(container, text="Close", command=history_window.destroy).pack(pady=(10,0))

    def open_spending_window(self):
        spending_window = tk.Toplevel(self.root)
        spending_window.title("Spending Manager")
        spending_window.geometry("400x450")
        
        # Main container frame
        main_frame = tk.Frame(spending_window, padx=10, pady=10)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Category Section
        tk.Label(main_frame, text="Category:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0,5))
        
        category_frame = tk.Frame(main_frame)
        category_frame.grid(row=1, column=0, columnspan=3, sticky='ew')
        
        self.spending_category_box = ttk.Combobox(category_frame, values=self.spending_categories, state='readonly')
        self.spending_category_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        self.spending_category_box.current(0)
        
        new_category_entry = tk.Entry(category_frame, width=15)
        new_category_entry.pack(side=tk.LEFT, padx=(0,5))
        
        def manage_category(action):
            if action == 'add':
                new_cat = new_category_entry.get().strip()
                if new_cat and new_cat not in self.spending_categories:
                    self.spending_categories.append(new_cat)
                    self.spending_category_box['values'] = self.spending_categories
                    self.spending_category_box.set(new_cat)
                    new_category_entry.delete(0, tk.END)
                    self.save_data()
            elif action == 'del':
                if len(self.spending_categories) > 1:
                    current = self.spending_category_box.get()
                    self.spending_categories.remove(current)
                    self.spending_category_box['values'] = self.spending_categories
                    self.spending_category_box.current(0)
                    self.save_data()
        
        btn_frame = tk.Frame(category_frame)
        btn_frame.pack(side=tk.LEFT)
        tk.Button(btn_frame, text="+", width=2, command=lambda: manage_category('add')).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="-", width=2, command=lambda: manage_category('del')).pack(side=tk.LEFT)
        
        # Amount Section
        tk.Label(main_frame, text="Amount ($):", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=(10,5))
        amount_entry = tk.Entry(main_frame, validate='key')
        amount_entry.grid(row=3, column=0, sticky='ew', columnspan=3)
        
        # Comment Section
        tk.Label(main_frame, text="Comment:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=(10,5))
        comment_entry = tk.Entry(main_frame)
        comment_entry.grid(row=5, column=0, sticky='ew', columnspan=3)
        
        # Button Section
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=(15,0))
        
        def save_spending():
            try:
                amount = float(amount_entry.get())
                if amount <= 0:
                    raise ValueError
                category = self.spending_category_box.get()
                comment = comment_entry.get().strip()
                
                self.update_spending(amount)
                self.spending_history.append({
                    'category': category,
                    'amount': amount,
                    'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'comment': comment
                })
                
                self.save_data()
                amount_entry.delete(0, tk.END)
                comment_entry.delete(0, tk.END)
                amount_entry.focus()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid positive number")
        
        tk.Button(button_frame, text="Save", command=save_spending).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="View History", command=self.show_spending_history).pack(side=tk.LEFT, padx=5)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        amount_entry.focus()

    def show_spending_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Spending History Timeline")
        history_window.geometry("750x400")
        
        if not self.spending_history:
            tk.Label(history_window, text="No spending history available").pack(pady=20)
            return
            
        container = tk.Frame(history_window)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        header_frame = tk.Frame(container)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="Date/Time", font=('Arial', 9, 'bold'), width=15, anchor='w').pack(side=tk.LEFT)
        tk.Label(header_frame, text="Category", font=('Arial', 9, 'bold'), width=15, anchor='w').pack(side=tk.LEFT)
        tk.Label(header_frame, text="Amount", font=('Arial', 9, 'bold'), width=15, anchor='e').pack(side=tk.LEFT)
        tk.Label(header_frame, text="Comment", font=('Arial', 9, 'bold'), width=20, anchor='w').pack(side=tk.LEFT)
        tk.Label(header_frame, text="Action", font=('Arial', 9, 'bold'), width=10, anchor='center').pack(side=tk.LEFT)
        
        canvas = tk.Canvas(container, borderwidth=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def delete_spending_record(index):
            if messagebox.askyesno("Confirm", "Delete this spending record?"):
                # Update totals
                self.total_spending -= self.spending_history[index]['amount']
                # Remove record
                del self.spending_history[index]
                # Save changes
                self.save_data()
                # Update main display
                self.spending_label.config(text=f"Total spending: ${self.total_spending:.2f}")
                self.update_balance_display()
                self.update_chart()
                # Refresh history view
                history_window.destroy()
                self.show_spending_history()
        
        for idx, record in enumerate(reversed(self.spending_history)):
            entry_frame = tk.Frame(scrollable_frame)
            entry_frame.pack(fill=tk.X, pady=2)
            
            tk.Label(entry_frame, text=record['timestamp'], width=15, anchor='w').pack(side=tk.LEFT)
            tk.Label(entry_frame, text=record['category'], width=15, anchor='w').pack(side=tk.LEFT)
            tk.Label(entry_frame, text=f"${record['amount']:.2f}", width=15, anchor='e').pack(side=tk.LEFT)
            tk.Label(entry_frame, text=record.get('comment', ''), width=20, anchor='w').pack(side=tk.LEFT)
            tk.Button(entry_frame, text="Delete", width=8, command=lambda i=idx: delete_spending_record(len(self.spending_history)-1-i)).pack(side=tk.LEFT, padx=5)
        
        total_frame = tk.Frame(container)
        total_frame.pack(fill=tk.X, pady=(10,0))
        tk.Label(total_frame, text="Total Spending:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(20,0))
        tk.Label(total_frame, text=f"${self.total_spending:.2f}", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        
        tk.Button(container, text="Close", command=history_window.destroy).pack(pady=(10,0))

if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetTracker(root)
    root.mainloop()