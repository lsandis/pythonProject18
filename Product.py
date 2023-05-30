import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import json
import pyodbc

total_price_label = None  # Declare total_price_label as a global variable

# Database connection details
server = 'localhost,1433'
database = 'my_database'
username = 'sa'
password = 'Valuetech@123'

# Set the connection string using the values above
conn_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"

products = []
tree = None  # Declare tree as a global variable

PRODUCTS_FILE = "products.json"  # File path to store the product data

def load_products_from_db():
    global products  # Update the global products list
    try:
        conn = pyodbc.connect(conn_string)
        cursor = conn.cursor()

        # Retrieve product data from the database including the ID column
        cursor.execute("SELECT ID, Name, Quantity, Price, SupplierID, ExpirationDate FROM Products")
        products_data = cursor.fetchall()

        products = []
        for row in products_data:
            product = {
                "id": row[0],
                "name": row[1],
                "quantity": row[2],
                "price": row[3],
                "supplier_id": row[4],
                "expiration_date": row[5]
            }
            products.append(product)

        cursor.close()
        conn.close()

        return products
    except pyodbc.Error as e:
        messagebox.showerror("Database Error", f"Failed to load products from the database: {e}")
        return []


def save_product_to_db(name, quantity, price, supplier_id, expiration_date):
    try:
        conn = pyodbc.connect(conn_string)
        cursor = conn.cursor()

        # Insert the product data into the database
        cursor.execute("INSERT INTO Products (Name, Quantity, Price, SupplierID, ExpirationDate) VALUES (?, ?, ?, ?, ?)",
            name, quantity, price, supplier_id, expiration_date)
        conn.commit()

        cursor.close()
        conn.close()

        messagebox.showinfo("Product Added", "Product has been added successfully.")

        refresh_product_list()  # Call refresh_product_list() after saving the product
        calculate_total_price()
    except pyodbc.Error as e:
        messagebox.showerror("Database Error", f"Failed to save product to the database: {e}")

def delete_product_from_db(product_id):
    try:
        conn = pyodbc.connect(conn_string)
        cursor = conn.cursor()

        # Delete the product from the database
        cursor.execute("DELETE FROM Products WHERE ID=?", product_id)
        conn.commit()

        cursor.close()
        conn.close()

        messagebox.showinfo("Product Deleted", "Product has been deleted successfully.")
    except pyodbc.Error as e:
        messagebox.showerror("Database Error", f"Failed to delete product from the database: {e}")

def add_product():
    def save_product():
        name = name_entry.get()
        quantity = int(quantity_entry.get())
        price = float(price_entry.get())
        supplier_id = supplier_id_entry.get()
        expiration_date = expiration_date_entry.get()

        save_product_to_db(name, quantity, price, supplier_id, expiration_date)
        refresh_product_list()
        calculate_total_price()
        add_product_window.destroy()

    add_product_window = tk.Toplevel()
    add_product_window.title("Add Product")

    name_label = tk.Label(add_product_window, text="Product Name:")
    name_label.pack()
    name_entry = tk.Entry(add_product_window)
    name_entry.pack()

    quantity_label = tk.Label(add_product_window, text="Quantity:")
    quantity_label.pack()
    quantity_entry = tk.Entry(add_product_window)
    quantity_entry.pack()

    price_label = tk.Label(add_product_window, text="Price:")
    price_label.pack()
    price_entry = tk.Entry(add_product_window)
    price_entry.pack()

    supplier_id_label = tk.Label(add_product_window, text="Supplier ID:")
    supplier_id_label.pack()
    supplier_id_entry = tk.Entry(add_product_window)
    supplier_id_entry.pack()

    expiration_date_label = tk.Label(add_product_window, text="Expiration Date:")
    expiration_date_label.pack()
    expiration_date_entry = tk.Entry(add_product_window)
    expiration_date_entry.pack()

    add_button = tk.Button(add_product_window, text="Add", command=save_product)
    add_button.pack()

    def calculate_product_sum(event):
        try:
            quantity = int(quantity_entry.get())
            price = float(price_entry.get())
            sum_label.config(text="Sum: €{:.2f}".format(quantity * price))
        except ValueError:
            sum_label.config(text="Sum: N/A")

    quantity_entry.bind("<KeyRelease>", calculate_product_sum)
    price_entry.bind("<KeyRelease>", calculate_product_sum)

    sum_label = tk.Label(add_product_window, text="Sum: N/A")
    sum_label.pack()

def refresh_product_list():
    global tree

    if tree is not None:
        tree.delete(*tree.get_children())

        products = load_products_from_db()  # Fetch the latest product data from the database

        for product in products:
            # Retrieve the necessary information from the product dictionary
            product_id = product["id"]
            name = product["name"]
            quantity = product["quantity"]
            price = product["price"]
            supplier_id = product["supplier_id"]
            expiration_date = product["expiration_date"]
            total_price = quantity * price  # Calculate the total price

            formatted_price = "€{:.2f}".format(price)
            formatted_total_price = "€{:.2f}".format(total_price)
            tree.insert("", tk.END, values=(product_id, name, quantity, formatted_price, supplier_id, expiration_date, formatted_total_price))

def calculate_total_price():
    total_prices = []
    for product in products:
        quantity = int(product["quantity"])
        price = float(product["price"])
        try:
            total_price = quantity * price
            total_prices.append(total_price)
        except ValueError:
            pass

    total_price_label.config(text="Total Price: €{:.2f}".format(sum(total_prices)))


def generate_report():
    try:
        conn = pyodbc.connect(conn_string)
        cursor = conn.cursor()

        # Retrieve all products from the database
        cursor.execute("SELECT * FROM Products")
        products_data = cursor.fetchall()

        report_text = "Product Report:\n\n"
        for product in products_data:
            name = product[1]
            quantity = product[2]
            price = product[3]
            supplier_id = product[4]
            expiration_date = product[5]

            report_text += f"Name: {name}\n"
            report_text += f"Quantity: {quantity}\n"
            report_text += f"Price: {price}\n"
            report_text += f"Supplier ID: {supplier_id}\n"
            report_text += f"Expiration Date: {expiration_date}\n\n"

        # Display the report in a message box
        messagebox.showinfo("Product Report", report_text)

        cursor.close()
        conn.close()



    except pyodbc.Error as e:
        messagebox.showerror("Database Error", f"Failed to generate report: {e}")


def delete_product():
    def confirm_delete():
        selected_item = delete_tree.selection()
        if selected_item:
            item_id = selected_item[0]
            item_data = delete_tree.item(item_id)['values']
            product_id = item_data[0]  # ID is the first column in the treeview

            for product in products:
                if product["id"] == product_id:
                    products.remove(product)
                    delete_product_from_db(product_id)
                    break

            refresh_product_list()
            calculate_total_price()
        else:
            messagebox.showwarning("No Product Selected", "Please select a product to delete.")

        delete_product_window.destroy()

    delete_product_window = tk.Toplevel()
    delete_product_window.title("Delete Product")

    delete_label = tk.Label(delete_product_window, text="Select a product to delete:")
    delete_label.pack()

    delete_tree = ttk.Treeview(delete_product_window,
                               columns=("id", "name", "quantity", "price", "supplier_id", "expiration_date"),
                               show="headings")
    delete_tree.heading("id", text="ID")
    delete_tree.heading("name", text="Product Name")
    delete_tree.heading("quantity", text="Quantity")
    delete_tree.heading("price", text="Price")
    delete_tree.heading("supplier_id", text="Supplier ID")
    delete_tree.heading("expiration_date", text="Expiration Date")
    delete_tree.pack(pady=10)

    scrollbar = ttk.Scrollbar(delete_product_window, orient="vertical", command=delete_tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    delete_tree.configure(yscrollcommand=scrollbar.set)

    products = load_products_from_db()

    for product in products:
        product_id = product["id"]
        name = product["name"]
        quantity = product["quantity"]
        price = product["price"]
        supplier_id = product["supplier_id"]
        expiration_date = product["expiration_date"]

        delete_tree.insert("", tk.END, values=(product_id, name, quantity, price, supplier_id, expiration_date))

    delete_button = tk.Button(delete_product_window, text="Delete", command=confirm_delete)
    delete_button.pack()

    delete_product_window.mainloop()


def login():
    username = username_entry.get()
    password = password_entry.get()

    if username == "admin" and password == "password":
        messagebox.showinfo("Login Successful", "Welcome, Admin!")
        root.destroy()
        open_main_window()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

def open_main_window():
    global tree
    global total_price_label

    main_window = tk.Tk()
    main_window.title("Grocery store x")
    main_window.geometry("500x300")

    button_frame = tk.Frame(main_window)
    button_frame.pack(side=tk.LEFT, padx=10)

    add_button = tk.Button(button_frame, text="Add Product", command=add_product)
    add_button.pack(pady=10)

    delete_button = tk.Button(button_frame, text="Delete Product", command=delete_product)
    delete_button.pack(pady=10)

    report_button = tk.Button(button_frame, text="Report", command=generate_report)
    report_button.pack(pady=10)

    # Create a treeview to display the products
    tree = ttk.Treeview(main_window,
                        columns=("id", "name", "quantity", "price", "supplier_id", "expiration_date", "total_price"),
                        show="headings")
    tree.heading("id", text="ID")
    tree.heading("name", text="Product Name")
    tree.heading("quantity", text="Quantity")
    tree.heading("price", text="Price")
    tree.heading("supplier_id", text="Supplier ID")
    tree.heading("expiration_date", text="Expiration Date")
    tree.heading("total_price", text="Total Price")  # Add a heading for the sum column

    tree.pack(pady=10)

    scrollbar = ttk.Scrollbar(main_window, orient="vertical", command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=scrollbar.set)

    global products
    products = load_products_from_db()

    refresh_product_list()

    # Assign total_price_label to the correct label widget
    total_price_label = tk.Label(main_window, text="Total Price: €0.00")
    total_price_label.pack()

    calculate_total_price()

    main_window.mainloop()



root = tk.Tk()
root.title("Grocery Store Management System")
root.geometry("300x400")

username_label = tk.Label(root, text="Username:")
username_label.pack()
username_entry = tk.Entry(root)
username_entry.pack()

password_label = tk.Label(root, text="Password:")
password_label.pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

login_button = tk.Button(root, text="Login", command=login)
login_button.pack()

root.mainloop()








