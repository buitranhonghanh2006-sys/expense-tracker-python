#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import ExpenseDatabase
from datetime import datetime, timedelta
import csv
import os

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản Lý Chi Tiêu - Expense Tracker")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Initialize database
        self.db = ExpenseDatabase()
        
        # Configure style
        self.setup_style()
        
        # Create GUI
        self.create_widgets()
        
        # Load initial data
        self.refresh_data()
    
    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0')
        style.configure('Header.TLabel', background='#f0f0f0', font=('Helvetica', 14, 'bold'))
        style.configure('TButton', font=('Helvetica', 10))
    
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="💰 QUẢN LÝ CHI TIÊU CUNG NGÂN HÀNG", 
                               style='Header.TLabel')
        title_label.pack(pady=10)
        
        # Input Frame
        input_frame = ttk.LabelFrame(main_frame, text="Nhập Chi Tiêu Mới", padding=15)
        input_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Date
        ttk.Label(input_frame, text="Ngày (YYYY-MM-DD):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=20)
        self.date_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Category
        ttk.Label(input_frame, text="Danh Mục:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, 
                                      values=["Ăn uống", "Giao thông", "Giáo dục", "Giải trí", 
                                             "Sức khỏe", "Mua sắm", "Tiền điện nước", "Khác"],
                                      state='readonly', width=15)
        category_combo.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        category_combo.set("Ăn uống")
        
        # Amount
        ttk.Label(input_frame, text="Số Tiền (VNĐ):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.amount_entry = ttk.Entry(input_frame, width=20)
        self.amount_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Description
        ttk.Label(input_frame, text="Ghi Chú:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.description_entry = ttk.Entry(input_frame, width=20)
        self.description_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Thêm Chi Tiêu", command=self.add_expense).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cập Nhật", command=self.update_expense).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Xóa", command=self.delete_expense).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Làm Mới", command=self.refresh_data).pack(side=tk.LEFT, padx=5)
        
        # Data Display Frame
        display_frame = ttk.LabelFrame(main_frame, text="Danh Sách Chi Tiêu", padding=10)
        display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # Treeview with scrollbar
        tree_frame = ttk.Frame(display_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(tree_frame, columns=('ID', 'Ngày', 'Danh Mục', 'Số Tiền', 'Ghi Chú'),
                                height=15, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('ID', anchor=tk.CENTER, width=50)
        self.tree.column('Ngày', anchor=tk.CENTER, width=100)
        self.tree.column('Danh Mục', anchor=tk.W, width=120)
        self.tree.column('Số Tiền', anchor=tk.E, width=120)
        self.tree.column('Ghi Chú', anchor=tk.W, width=250)
        
        self.tree.heading('#0', text='', anchor=tk.W)
        self.tree.heading('ID', text='ID', anchor=tk.CENTER)
        self.tree.heading('Ngày', text='Ngày', anchor=tk.CENTER)
        self.tree.heading('Danh Mục', text='Danh Mục', anchor=tk.W)
        self.tree.heading('Số Tiền', text='Số Tiền', anchor=tk.E)
        self.tree.heading('Ghi Chú', text='Ghi Chú', anchor=tk.W)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # Statistics Frame
        stats_frame = ttk.LabelFrame(main_frame, text="Thống Kê", padding=10)
        stats_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.stats_label = ttk.Label(stats_frame, text="", font=('Helvetica', 11))
        self.stats_label.pack(anchor=tk.W)
        
        # Export Frame
        export_frame = ttk.Frame(main_frame)
        export_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Button(export_frame, text="📊 Xuất CSV", command=self.export_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="📈 Xem Biểu Đồ", command=self.show_statistics).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="🔍 Tìm Kiếm", command=self.show_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="❌ Thoát", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
    
    def add_expense(self):
        try:
            date = self.date_entry.get()
            category = self.category_var.get()
            amount = float(self.amount_entry.get())
            description = self.description_entry.get()
            
            if not date or not category or amount <= 0:
                messagebox.showerror("Lỗi", "Vui lòng nhập đủ thông tin và số tiền > 0")
                return
            
            self.db.add_expense(date, category, amount, description)
            messagebox.showinfo("Thành Công", "Thêm chi tiêu thành công!")
            
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
            self.amount_entry.delete(0, tk.END)
            self.description_entry.delete(0, tk.END)
            
            self.refresh_data()
        except ValueError:
            messagebox.showerror("Lỗi", "Số tiền phải là một số!")
    
    def update_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Lỗi", "Vui lòng chọn chi tiêu để cập nhật!")
            return
        
        try:
            expense_id = int(self.tree.item(selected[0])['values'][0])
            date = self.date_entry.get()
            category = self.category_var.get()
            amount = float(self.amount_entry.get())
            description = self.description_entry.get()
            
            self.db.update_expense(expense_id, date, category, amount, description)
            messagebox.showinfo("Thành Công", "Cập nhật chi tiêu thành công!")
            self.refresh_data()
        except ValueError:
            messagebox.showerror("Lỗi", "Dữ liệu không hợp lệ!")
    
    def delete_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Lỗi", "Vui lòng chọn chi tiêu để xóa!")
            return
        
        if messagebox.askyesno("Xác Nhận", "Bạn có chắc muốn xóa chi tiêu này?"):
            expense_id = int(self.tree.item(selected[0])['values'][0])
            self.db.delete_expense(expense_id)
            messagebox.showinfo("Thành Công", "Xóa chi tiêu thành công!")
            self.refresh_data()
    
    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])['values']
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, values[1])
            self.category_var.set(values[2])
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, str(values[3]))
            self.description_entry.delete(0, tk.END)
            self.description_entry.insert(0, values[4])
    
    def refresh_data(self):
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load data
        expenses = self.db.get_all_expenses()
        total = 0
        for expense in expenses:
            self.tree.insert('', tk.END, values=expense)
            total += expense[3]
        
        # Update stats
        today_expenses = self.db.get_expenses_by_date(datetime.now().strftime("%Y-%m-%d"))
        today_total = sum([e[3] for e in today_expenses])
        
        month_start = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        month_expenses = self.db.get_expenses_by_date_range(month_start, datetime.now().strftime("%Y-%m-%d"))
        month_total = sum([e[3] for e in month_expenses])
        
        stats_text = f"📊 Tổng Chi Tiêu: {total:,.0f} VNĐ | Hôm Nay: {today_total:,.0f} VNĐ | Tháng Này: {month_total:,.0f} VNĐ"
        self.stats_label.config(text=stats_text)
    
    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                                 filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        
        try:
            expenses = self.db.get_all_expenses()
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Ngày', 'Danh Mục', 'Số Tiền', 'Ghi Chú'])
                writer.writerows(expenses)
            messagebox.showinfo("Thành Công", f"Xuất dữ liệu thành công tại: {file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi xuất: {str(e)}")
    
    def show_statistics(self):
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Thống Kê Chi Tiêu")
        stats_window.geometry("600x400")
        
        frame = ttk.Frame(stats_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Thống Kê Chi Tiêu Theo Danh Mục", 
                 font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        stats = self.db.get_category_summary()
        text_widget = tk.Text(frame, height=15, width=70)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        if stats:
            text_widget.insert(tk.END, "Danh Mục\t\t\tSố Tiền\t\tTỷ Lệ\n")
            text_widget.insert(tk.END, "="*60 + "\n")
            total = sum([s[1] for s in stats])
            for category, amount in stats:
                percentage = (amount / total * 100) if total > 0 else 0
                text_widget.insert(tk.END, f"{category:<20}\t{amount:>12,.0f}\t{percentage:>6.1f}%\n")
            text_widget.insert(tk.END, "-"*60 + "\n")
            text_widget.insert(tk.END, f"{‘TỔNG’: <20}\t{total:>12,.0f}\t{100:>6.1f}%\n")
        else:
            text_widget.insert(tk.END, "Chưa có dữ liệu!")
        
        text_widget.config(state=tk.DISABLED)
    
    def show_search(self):
        search_window = tk.Toplevel(self.root)
        search_window.title("Tìm Kiếm Chi Tiêu")
        search_window.geometry("500x400")
        
        frame = ttk.Frame(search_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Tìm Kiếm Theo Danh Mục:").pack(anchor=tk.W, pady=5)
        search_var = tk.StringVar()
        search_combo = ttk.Combobox(frame, textvariable=search_var,
                                   values=["Ăn uống", "Giao thông", "Giáo dục", "Giải trí", 
                                          "Sức khỏe", "Mua sắm", "Tiền điện nước", "Khác"],
                                   state='readonly', width=30)
        search_combo.pack(anchor=tk.W, pady=5)
        
        result_text = tk.Text(frame, height=15, width=60)
        result_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        def search():
            result_text.config(state=tk.NORMAL)
            result_text.delete(1.0, tk.END)
            
            category = search_var.get()
            if not category:
                messagebox.showerror("Lỗi", "Vui lòng chọn danh mục!")
                return
            
            expenses = self.db.get_expenses_by_category(category)
            if expenses:
                result_text.insert(tk.END, f"Kết quả tìm kiếm cho '{category}':\n")
                result_text.insert(tk.END, "="*50 + "\n")
                total = 0
                for expense in expenses:
                    result_text.insert(tk.END, f"Ngày: {expense[1]}\n")
                    result_text.insert(tk.END, f"Số Tiền: {expense[3]:,.0f} VNĐ\n")
                    result_text.insert(tk.END, f"Ghi Chú: {expense[4]}\n")
                    result_text.insert(tk.END, "-"*50 + "\n")
                    total += expense[3]
                result_text.insert(tk.END, f"\nTổng Cộng: {total:,.0f} VNĐ")
            else:
                result_text.insert(tk.END, f"Không tìm thấy chi tiêu nào cho danh mục '{category}'")
            
            result_text.config(state=tk.DISABLED)
        
        ttk.Button(frame, text="Tìm Kiếm", command=search).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()