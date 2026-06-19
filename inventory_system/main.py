import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# Database
conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()

# Main table
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE,
    name TEXT UNIQUE,
    quantity INTEGER,
    unit_price REAL,
    total_price REAL,
    entry_date TEXT
)
""")

# Deleted products table
cursor.execute("""
CREATE TABLE IF NOT EXISTS deleted_products (
    id INTEGER,
    code TEXT,
    name TEXT,
    quantity INTEGER,
    unit_price REAL,
    total_price REAL,
    deleted_date TEXT
)
""")

conn.commit()


# Auto calculate total
def calculate_total(event=None):
    try:
        qty = int(qty_entry.get())
        price = float(price_entry.get())
        total = qty * price

        total_entry.config(state="normal")
        total_entry.delete(0, tk.END)
        total_entry.insert(0, str(total))
        total_entry.config(state="readonly")
    except:
        total_entry.config(state="normal")
        total_entry.delete(0, tk.END)
        total_entry.config(state="readonly")


# Add Product
def add_product():
    code = code_entry.get().strip()
    name = name_entry.get().strip()
    qty = qty_entry.get().strip()
    price = price_entry.get().strip()
    total = total_entry.get().strip()
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    if not code or not name or not qty or not price:
        messagebox.showerror("Error", "Fill all fields")
        return

    # Check duplicates
    cursor.execute(
        "SELECT * FROM products WHERE code=? OR name=?",
        (code, name)
    )

    if cursor.fetchone():
        messagebox.showerror(
            "Duplicate Error",
            "Product Code or Product Name already exists!"
        )
        return

    cursor.execute("""
        INSERT INTO products
        (code, name, quantity, unit_price, total_price, entry_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (code, name, qty, price, total, date))

    conn.commit()
    clear_fields()
    show_products()

# show_products
def show_products():
    for item in tree.get_children():
        tree.delete(item)

    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()

    total_products = len(rows)
    total_units = 0
    total_stock_value = 0
    current_id = 1

    for row in rows:
        display_row = (
            current_id,
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6]
        )

        tree.insert("", tk.END, values=display_row)

        try:
            total_units += int(row[3] if row[3] else 0)
        except:
            pass

        try:
            total_stock_value += float(row[5] if row[5] else 0)
        except:
            pass

        current_id += 1

    summary_label.config(
        text=f"Total Products: {total_products} | Total Units: {total_units} | Total Stock Value: ₹{total_stock_value:.2f}"
    )

    root.update_idletasks()


# Search Product
def search_product():
    keyword = search_entry.get().strip()

    for item in tree.get_children():
        tree.delete(item)

    cursor.execute(
        "SELECT * FROM products WHERE code LIKE ? OR name LIKE ?",
        ('%' + keyword + '%', '%' + keyword + '%')
    )

    rows = cursor.fetchall()
    current_id = 1

    for row in rows:
        display_row = (
            current_id,
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6]
        )

        tree.insert("", tk.END, values=display_row)
        current_id += 1


# Delete Product
def delete_product():
    selected = tree.selection()

    if selected:
        item = tree.item(selected[0])
        values = item["values"]

        old_id = values[1]
        code = values[2]
        name = values[3]
        qty = values[4]
        unit_price = values[5]
        total_price = values[6]
        deleted_date = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Save delete history
        cursor.execute("""
            INSERT INTO deleted_products
            (id, code, name, quantity, unit_price, total_price, deleted_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            old_id, code, name, qty,
            unit_price, total_price, deleted_date
        ))

        # Delete from products
        cursor.execute(
            "DELETE FROM products WHERE id=?",
            (old_id,)
        )

        conn.commit()
        show_products()


# Show Deleted Products
def show_deleted_products():
    for item in tree.get_children():
        tree.delete(item)

    cursor.execute("SELECT * FROM deleted_products")
    rows = cursor.fetchall()

    current_id = 1
    deleted_total = 0

    for row in rows:
        display_row = (
            current_id,
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6]
        )

        tree.insert("", tk.END, values=display_row)

        deleted_total += float(row[5])
        current_id += 1

    summary_label.config(
        text=f"Deleted Products: {len(rows)} | Deleted Stock Value: ₹{deleted_total:.2f}"
    )


# Clear fields
def clear_fields():
    code_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    qty_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)

    total_entry.config(state="normal")
    total_entry.delete(0, tk.END)
    total_entry.config(state="readonly")


# Main Window
root = tk.Tk()
root.title("Factory Inventory ERP System")
root.geometry("1450x800")
root.config(bg="#1e293b")

# Header
header = tk.Label(
    root,
    text="FACTORY INVENTORY MANAGEMENT SYSTEM",
    bg="#0f172a",
    fg="white",
    font=("Arial", 24, "bold"),
    pady=18
)
header.pack(fill="x")

# Input Frame
frame = tk.Frame(root, bg="#334155", pady=15)
frame.pack(fill="x", padx=15, pady=10)

labels = ["Product Code", "Product Name", "Quantity", "Unit Price", "Total"]

for i, text in enumerate(labels):
    tk.Label(
        frame,
        text=text,
        bg="#334155",
        fg="white",
        font=("Arial", 12, "bold")
    ).grid(row=0, column=i * 2, padx=5)

code_entry = tk.Entry(frame, width=15)
code_entry.grid(row=0, column=1)

name_entry = tk.Entry(frame, width=20)
name_entry.grid(row=0, column=3)

qty_entry = tk.Entry(frame, width=10)
qty_entry.grid(row=0, column=5)
qty_entry.bind("<KeyRelease>", calculate_total)

price_entry = tk.Entry(frame, width=10)
price_entry.grid(row=0, column=7)
price_entry.bind("<KeyRelease>", calculate_total)

total_entry = tk.Entry(frame, width=12, state="readonly")
total_entry.grid(row=0, column=9)

tk.Button(
    frame,
    text="Add Product",
    bg="#16a34a",
    fg="white",
    font=("Arial", 12, "bold"),
    command=add_product
).grid(row=0, column=10, padx=10)

# Search Frame
search_frame = tk.Frame(root, bg="#475569", pady=10)
search_frame.pack(fill="x", padx=15)

tk.Label(
    search_frame,
    text="Search Product",
    bg="#475569",
    fg="white",
    font=("Arial", 12, "bold")
).pack(side="left", padx=10)

search_entry = tk.Entry(search_frame, width=25)
search_entry.pack(side="left")

tk.Button(
    search_frame,
    text="Search",
    bg="#2563eb",
    fg="white",
    command=search_product
).pack(side="left", padx=5)

tk.Button(
    search_frame,
    text="Show All",
    bg="#f59e0b",
    fg="white",
    command=show_products
).pack(side="left", padx=5)

tk.Button(
    search_frame,
    text="Delete Selected",
    bg="#dc2626",
    fg="white",
    command=delete_product
).pack(side="left", padx=5)

tk.Button(
    search_frame,
    text="Deleted History",
    bg="#7c3aed",
    fg="white",
    command=show_deleted_products
).pack(side="left", padx=5)

# Table
columns = (
    "Current ID",
    "Old ID",
    "Code",
    "Name",
    "Qty",
    "Unit Price",
    "Total Price",
    "Date"
)

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background="white",
    foreground="black",
    rowheight=35,
    font=("Arial", 11)
)

style.configure(
    "Treeview.Heading",
    background="#0f172a",
    foreground="white",
    font=("Arial", 12, "bold")
)

tree_frame = tk.Frame(root, bg="#0f172a")
tree_frame.pack(fill="both", padx=15, pady=(10, 0))

tree = ttk.Treeview(
    tree_frame,
    columns=columns,
    show="headings",
    height=18
)

tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree_scroll_y.pack(side="right", fill="y")
tree.configure(yscrollcommand=tree_scroll_y.set)
tree.pack(side="left", fill="both", expand=True)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=170, anchor="center")

# Fixed Bottom Bar
bottom_frame = tk.Frame(root, bg="#111827", height=60)
bottom_frame.pack(fill="x", side="bottom")
bottom_frame.pack_propagate(False)

summary_label = tk.Label(
    bottom_frame,
    text="",
    bg="#111827",
    fg="#22c55e",
    font=("Arial", 14, "bold")
)
summary_label.pack(fill="both", expand=True)

show_products()

root.mainloop()