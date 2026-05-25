from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "clave_secreta_pos"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("pos.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        stock INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("pos.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect(url_for("dashboard"))

        return "Login incorrecto"

    return """
    <h2>Login POS</h2>
    <form method="POST">
        <input name="username" placeholder="Usuario">
        <input name="password" type="password" placeholder="Contraseña">
        <button>Entrar</button>
    </form>
    """

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("pos.db")
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()

    html = "<h2>Panel POS</h2><a href='/add'>Agregar producto</a><br><br>"

    for p in products:
        html += f"{p[1]} - S/{p[2]} - Stock: {p[3]}<br>"

    return html

# ---------------- ADD PRODUCT ----------------
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        stock = request.form["stock"]

        conn = sqlite3.connect("pos.db")
        c = conn.cursor()
        c.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
                  (name, price, stock))
        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))

    return """
    <h2>Agregar producto</h2>
    <form method="POST">
        <input name="name" placeholder="Nombre">
        <input name="price" placeholder="Precio">
        <input name="stock" placeholder="Stock">
        <button>Guardar</button>
    </form>
    """

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()