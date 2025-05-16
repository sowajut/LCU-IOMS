from flask import Flask, render_template, request, redirect, session, url_for
from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)
if __name__ == "__main__":
    app.run(debug=True)
app.secret_key = 'your_secret_key_here'  # This can be any random string

# Step 1: Set database path
DB_PATH = os.path.join('database', 'database.db')

# Step 2: Function to create the database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create inventory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            department TEXT,
            quantity INTEGER,
            condition TEXT,
            location TEXT
        )
    ''')

    # Create maintenance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maintenance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            department TEXT,
            issue TEXT,
            status TEXT
        )
    ''')

        # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    conn.commit()
    conn.close()

# Step 3: Initialize the database
init_db()
@app.route("/inventory", methods=["GET", "POST"])
def inventory():
    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Handle form submission (POST)
    if request.method == "POST":
        item_name = request.form["item_name"]
        department = request.form["department"]
        quantity = request.form["quantity"]
        condition = request.form["condition"]
        location = request.form["location"]

        cursor.execute("""
            INSERT INTO inventory (item_name, department, quantity, condition, location)
            VALUES (?, ?, ?, ?, ?)
        """, (item_name, department, quantity, condition, location))
        conn.commit()

    # Handle search (GET)
    search_term = request.args.get("search")
    if search_term:
        cursor.execute("SELECT * FROM inventory WHERE department LIKE ?", ('%' + search_term + '%',))
    else:
        cursor.execute("SELECT * FROM inventory")

    inventory = cursor.fetchall()
    conn.close()

    print("Inventory fetched:", inventory)  # Debug print

    return render_template("inventory.html", inventory=inventory)
@app.route("/delete_inventory/<int:item_id>")
def delete_inventory(item_id):
    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

    return redirect("/inventory")
@app.route("/edit_inventory/<int:item_id>", methods=["GET", "POST"])
def edit_inventory(item_id):
    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if request.method == "POST":
        item_name = request.form["item_name"]
        department = request.form["department"]
        quantity = request.form["quantity"]
        condition = request.form["condition"]
        location = request.form["location"]

        cursor.execute("""
            UPDATE inventory SET 
            item_name=?, department=?, quantity=?, condition=?, location=? 
            WHERE id=?
        """, (item_name, department, quantity, condition, location, item_id))
        conn.commit()
        conn.close()
        return redirect("/inventory")

    # GET request – show existing data in form
    cursor.execute("SELECT * FROM inventory WHERE id=?", (item_id,))
    item = cursor.fetchone()
    conn.close()
    return render_template("edit_inventory.html", item=item)
@app.route("/")
def home():
    return '''
    <h2>Welcome to Lead City Inventory System</h2>
    <p><a href="/inventory">Go to Inventory Page</a></p>
    '''
@app.route("/maintenance", methods=["GET", "POST"])
def maintenance():
    if "username" not in session:
     return redirect("/login")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if request.method == "POST":
        item_name = request.form["item_name"]
        department = request.form["department"]
        issue = request.form["issue"]
        status = request.form["status"]

        cursor.execute("INSERT INTO maintenance (item_name, department, issue, status) VALUES (?, ?, ?, ?)",
                       (item_name, department, issue, status))
        conn.commit()

    # Handle search
    search_term = request.args.get("search")
    if search_term:
        cursor.execute("SELECT * FROM maintenance WHERE department LIKE ?", ('%' + search_term + '%',))
    else:
        cursor.execute("SELECT * FROM maintenance")

    maintenance = cursor.fetchall()
    conn.close()

    return render_template("maintenance.html", maintenance=maintenance)
@app.route("/delete_maintenance/<int:request_id>")
def delete_maintenance(request_id):
    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM maintenance WHERE id = ?", (request_id,))
    conn.commit()
    conn.close()
    return redirect("/maintenance")
@app.route("/update_status/<int:id>", methods=["POST"])
def update_status(id):
    if "username" not in session:
        return redirect("/login")

    new_status = request.form["status"]
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE maintenance SET status=? WHERE id=?", (new_status, id))
    conn.commit()
    conn.close()
    return redirect("/maintenance")
@app.route("/edit_maintenance/<int:request_id>", methods=["GET", "POST"])
def edit_maintenance(request_id):
    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if request.method == "POST":
        item_name = request.form["item_name"]
        department = request.form["department"]
        issue = request.form["issue"]
        status = request.form["status"]

        cursor.execute('''
            UPDATE maintenance
            SET item_name = ?, department = ?, issue = ?, status = ?
            WHERE id = ?
        ''', (item_name, department, issue, status, request_id))

        conn.commit()
        conn.close()
        return redirect("/maintenance")

    cursor.execute("SELECT * FROM maintenance WHERE id = ?", (request_id,))
    request_data = cursor.fetchone()
    conn.close()

    return render_template("edit_maintenance.html", request_data=request_data)
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect("/login")
        except:
            return "Username already exists!"
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["username"] = username
            return redirect("/dashboard")
        else:
            return "Invalid login!"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/login")
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/login")
    return render_template("dashboard.html")
@app.route("/reports")
def reports():
    if "username" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Report 1: Inventory summary by department
    cursor.execute("SELECT department, COUNT(*) FROM inventory GROUP BY department")
    inventory_summary = cursor.fetchall()

    # Report 2: Maintenance status summary
    cursor.execute("SELECT status, COUNT(*) FROM maintenance GROUP BY status")
    maintenance_summary = cursor.fetchall()

    conn.close()

    return render_template("reports.html", inventory_summary=inventory_summary, maintenance_summary=maintenance_summary)

