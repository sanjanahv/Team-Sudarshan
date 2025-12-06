import sqlite3
import datetime
import random
import os
import time

# --- CONFIGURATION ---
DB_NAME = "supermarket.db"
LOW_STOCK_THRESHOLD = 15

# --- DATABASE SETUP ---
def get_db_connection():
    return sqlite3.connect(DB_NAME)

def setup_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT
        )
    ''')
    
    # Create Inventory Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unique_code TEXT UNIQUE,
            name TEXT,
            category TEXT,
            price REAL,
            quantity INTEGER,
            entry_date TEXT,
            expiry_date TEXT
        )
    ''')
    
    # Seed Admin and Employee if they don't exist
    cursor.execute('SELECT * FROM users WHERE username = "admin"')
    if not cursor.fetchone():
        cursor.execute('INSERT INTO users VALUES (?, ?, ?)', ('admin', '123', 'manager'))
        cursor.execute('INSERT INTO users VALUES (?, ?, ?)', ('emp', '123', 'employee'))
        print("[System] Default users created: admin/123, emp/123")
        
        # Seed 100 Random Items
        categories = ['DAIRY', 'BAKERY', 'FRUIT', 'VEG', 'MEAT', 'DRINK']
        names = ['Milk', 'Bread', 'Apple', 'Tomato', 'Chicken', 'Cola', 'Cheese', 'Yogurt']
        
        today = datetime.date.today()
        print("[System] Seeding 100 items... Please wait.")
        for i in range(100):
            cat = random.choice(categories)
            name = f"{random.choice(names)}_{i}"
            entry = today - datetime.timedelta(days=random.randint(1, 100))
            expiry = today + datetime.timedelta(days=random.randint(-10, 60)) # Some expired, some fresh
            qty = random.randint(5, 50)
            price = round(random.uniform(1.50, 20.00), 2)
            
            # Logic: Unique Code = CAT + DateAdded + DaysToExpiry + RandomID
            days_diff = (expiry - entry).days
            code = f"{cat[:3]}-{entry.strftime('%Y%m%d')}-{days_diff}-{random.randint(1000,9999)}"
            
            cursor.execute('''
                INSERT INTO inventory (unique_code, name, category, price, quantity, entry_date, expiry_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (code, name, cat, price, qty, entry, expiry))

    conn.commit()
    conn.close()

# --- HELPER FUNCTIONS ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_date_object(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

# --- MANAGER MODULE ---
def check_alerts():
    """Checks for expired items and low stock."""
    conn = get_db_connection()
    cursor = conn.cursor()
    today = datetime.date.today().strftime('%Y-%m-%d')
    
    # Check Low Stock
    cursor.execute('SELECT name, quantity FROM inventory WHERE quantity < ?', (LOW_STOCK_THRESHOLD,))
    low_stock = cursor.fetchall()
    
    # Check Expired
    cursor.execute('SELECT name, expiry_date FROM inventory WHERE expiry_date < ?', (today,))
    expired = cursor.fetchall()
    
    conn.close()
    
    if low_stock or expired:
        print("\n" + "!"*10 + " ALERTS " + "!"*10)
        if low_stock:
            print(f"⚠️  LOW STOCK ALERT (Below {LOW_STOCK_THRESHOLD}):")
            for item in low_stock:
                print(f"   - {item[0]} (Qty: {item[1]})")
        
        if expired:
            print(f"⚠️  EXPIRATION ALERT (Already Expired):")
            for item in expired:
                print(f"   - {item[0]} (Expired: {item[1]})")
        print("!"*30 + "\n")
        input("Press Enter to acknowledge alerts...")

def manager_menu():
    while True:
        clear_screen()
        print("=== MANAGER DASHBOARD ===")
        print("1. View Full Inventory")
        print("2. Add New Item")
        print("3. Check Status/Alerts")
        print("4. Logout")
        
        choice = input("Select Option: ")
        
        if choice == '1':
            view_inventory()
        elif choice == '2':
            add_item()
        elif choice == '3':
            check_alerts()
        elif choice == '4':
            break

def view_inventory():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT unique_code, name, price, quantity, expiry_date FROM inventory')
    items = cursor.fetchall()
    conn.close()
    
    print("\n--- CURRENT INVENTORY ---")
    print(f"{'CODE':<30} {'NAME':<15} {'PRICE':<8} {'QTY':<5} {'EXPIRY'}")
    print("-" * 75)
    for i in items:
        print(f"{i[0]:<30} {i[1]:<15} ${i[2]:<7.2f} {i[3]:<5} {i[4]}")
    input("\nPress Enter to return...")

def add_item():
    print("\n--- ADD NEW ITEM ---")
    name = input("Item Name: ")
    category = input("Category: ").upper()
    try:
        price = float(input("Price: "))
        qty = int(input("Quantity: "))
        entry_str = input("Entry Date (YYYY-MM-DD): ")
        expiry_str = input("Expiry Date (YYYY-MM-DD): ")
        
        # Generate Code Logic
        entry_date = get_date_object(entry_str)
        expiry_date = get_date_object(expiry_str)
        days_diff = (expiry_date - entry_date).days
        unique_code = f"{category[:3]}-{entry_date.strftime('%Y%m%d')}-{days_diff}-{random.randint(1000,9999)}"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO inventory (unique_code, name, category, price, quantity, entry_date, expiry_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (unique_code, name, category, price, qty, entry_str, expiry_str))
        conn.commit()
        conn.close()
        print(f"Success! Item added with Code: {unique_code}")
        time.sleep(2)
    except ValueError:
        print("Invalid input format. Try again.")
        time.sleep(1)

# --- EMPLOYEE MODULE ---
def employee_menu():
    cart = []
    
    while True:
        clear_screen()
        print("=== EMPLOYEE BILLING TERMINAL ===")
        print(f"Items in Cart: {len(cart)}")
        print("1. Scan Item (Enter Code)")
        print("2. View Cart")
        print("3. Checkout & Generate Bill")
        print("4. Logout")
        
        choice = input("Option: ")
        
        if choice == '1':
            scan_item(cart)
        elif choice == '2':
            view_cart(cart)
        elif choice == '3':
            if cart:
                checkout(cart)
                cart = [] # Clear cart after checkout
            else:
                print("Cart is empty!")
                time.sleep(1)
        elif choice == '4':
            break

def scan_item(cart):
    code = input("Enter Item Unique Code: ")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inventory WHERE unique_code = ?', (code,))
    item = cursor.fetchone()
    conn.close()
    
    if item:
        # Check stock vs cart quantity
        # item structure: 0:id, 1:code, 2:name, 3:cat, 4:price, 5:qty...
        current_cart_qty = sum(1 for x in cart if x['code'] == code)
        
        if item[5] > current_cart_qty:
            cart.append({
                'code': item[1],
                'name': item[2],
                'price': item[4]
            })
            print(f"Added {item[2]} to cart.")
        else:
            print("Stock insufficient!")
    else:
        print("Item not found.")
    time.sleep(1)

def view_cart(cart):
    total = sum(x['price'] for x in cart)
    print("\n--- CART ---")
    for item in cart:
        print(f"{item['name']} - ${item['price']}")
    print(f"TOTAL: ${total:.2f}")
    input("Press Enter...")

def checkout(cart):
    total = sum(x['price'] for x in cart)
    
    # Update Database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for item in cart:
            cursor.execute('UPDATE inventory SET quantity = quantity - 1 WHERE unique_code = ?', (item['code'],))
        conn.commit()
        
        # Generate Text Bill
        filename = f"bill_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w") as f:
            f.write("SUPERMARKET RECEIPT\n")
            f.write("="*30 + "\n")
            for item in cart:
                f.write(f"{item['name']:<20} ${item['price']:.2f}\n")
            f.write("-" * 30 + "\n")
            f.write(f"GRAND TOTAL:        ${total:.2f}\n")
            f.write("="*30 + "\n")
            f.write("Thank you for shopping!\n")
            
        print(f"\nTransaction Complete! Bill saved to '{filename}'")
    except Exception as e:
        print(f"Error processing transaction: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    input("Press Enter to continue...")

# --- MAIN APP ---
def main():
    setup_database()
    
    while True:
        clear_screen()
        print("=== WELCOME TO PYTHON SUPERMARKET ===")
        print("Login Required")
        username = input("Username: ")
        password = input("Password: ")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT role FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            role = user[0]
            print(f"Login Successful. Welcome {role}!")
            time.sleep(1)
            
            if role == 'manager':
                # Auto-check alerts on login
                check_alerts()
                manager_menu()
            else:
                employee_menu()
        else:
            print("Invalid Credentials. Try again.")
            time.sleep(1)

if __name__ == "__main__":
    main()