from flask import Flask, request, redirect, url_for, session
import psycopg2
import os

app = Flask(__name__)
app.secret_key = "clave_secreta_pos"

# 🔥 RECOMENDADO: usar variable de entorno en Render
DB_URL = os.environ.get(
    "DB_URL",
    "postgresql://postgres:bg4BarSND11nN3hU@db.muzoufplncpyumoaqmet.supabase.co:5432/postgres"
)

def get_db():
    return psycopg2.connect(DB_URL)

# ---------------- INIT DB (NO SE EJECUTA EN RENDER) ----------------
def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name TEXT,
        price NUMERIC,
        stock INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id SERIAL PRIMARY KEY,
        product_id INTEGER,
        quantity INTEGER,
        total NUMERIC,
        date TIMESTAMP DEFAULT NOW()
    )
    """)

    c.execute("SELECT * FROM users WHERE username=%s", ("admin",))
    admin = c.fetchone()

    if not admin:
        c.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            ("admin", "1234")
        )

    conn.commit()
    conn.close()

# ❌ IMPORTANTE: NO LLAMAR ESTO EN RENDER
# init_db()

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )

        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect(url_for("dashboard"))

        return "Login incorrecto"

    return """
    <h2>Login POS</h2>
    <form method="POST">
        <input name="username" placeholder="Usuario"><br><br>
        <input name="password" type="password" placeholder="Contraseña"><br><br>
        <button>Entrar</button>
    </form>
    """

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM products")
    products = c.fetchall()

    conn.close()

    html = f"<h2>Bienvenido {session['user']}</h2>"
    html += "<a href='/add'>Agregar producto</a><br><br>"
    html += "<a href='/ventas'>Ver ventas</a><br><br>"
    html += "<a href='/logout'>Cerrar sesión</a><br><br>"
    html += "<h3>Productos</h3>"

    for p in products:

        color = "black"

        if p[3] <= 5:
            color = "red"

        html += f"""
        <div style="color:{color}">
            ID: {p[0]} |
            {p[1]} |
            Precio: S/{p[2]} |
            Stock: {p[3]}

            <a href='/sell/{p[0]}'>Vender</a>
            <br><br>
        </div>
        """

    return html

# ---------------- ADD ----------------
@app.route("/add", methods=["GET", "POST"])
def add():

    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        stock = request.form["stock"]

        conn = get_db()
        c = conn.cursor()

        c.execute(
            "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s)",
            (name, price, stock)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))

    return """
    <h2>Agregar producto</h2>
    <form method="POST">
        <input name="name" placeholder="Nombre"><br><br>
        <input name="price" placeholder="Precio"><br><br>
        <input name="stock" placeholder="Stock"><br><br>
        <button>Guardar</button>
    </form>
    """

# ---------------- SELL ----------------
@app.route("/sell/<int:id>")
def sell(id):

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM products WHERE id=%s", (id,))
    product = c.fetchone()

    if product:
        stock_actual = product[3]

        if stock_actual > 0:

            nuevo_stock = stock_actual - 1
            total = product[2]

            c.execute(
                "UPDATE products SET stock=%s WHERE id=%s",
                (nuevo_stock, id)
            )

            c.execute(
                "INSERT INTO sales (product_id, quantity, total) VALUES (%s, %s, %s)",
                (id, 1, total)
            )

            conn.commit()

    conn.close()
    return redirect(url_for("dashboard"))

# ---------------- VENTAS ----------------
@app.route("/ventas")
def ventas():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    c = conn.cursor()

    c.execute("""
        SELECT s.id, p.name, s.quantity, s.total, s.created_at
        FROM sales s
        JOIN products p ON s.product_id = p.id
        ORDER BY s.id DESC
    """)

    ventas = c.fetchall()
    conn.close()

    html = "<h2>💰 Caja de Ventas</h2>"
    html += "<a href='/dashboard'>Volver</a><br><br>"

    total_general = 0

    for v in ventas:
        html += f"""
        Venta ID: {v[0]} |
        Producto: {v[1]} |
        Cantidad: {v[2]} |
        Total: S/{v[3]} |
        Fecha: {v[4]}
        <br>
        """
        total_general += float(v[3])

    html += f"<br><h2>Total en caja: S/{total_general}</h2>"

    return html
# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()