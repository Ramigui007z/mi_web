from flask import Flask, request, redirect, url_for, session
import psycopg2
import os

app = Flask(__name__)
app.secret_key = "clave_secreta_pos"

# ---------------- DB ----------------
DB_URL = os.environ.get(
    "DB_URL",
    "postgresql://postgres:bg4BarSND11nN3hU@db.muzoufplncpyumoaqmet.supabase.co:5432/postgres"
)

def get_db():
    return psycopg2.connect(DB_URL)

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

    <img src="/static/logo.gif" width="200"><br><br>

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

    c.execute("SELECT * FROM products ORDER BY id DESC")
    products = c.fetchall()

    conn.close()

    html = f"""
    <h2>📊 POS - Bienvenido {session['user']}</h2>

    <a href='/add'>➕ Agregar producto</a> |
    <a href='/ventas'>💰 Ventas</a> |
    <a href='/logout'>🚪 Salir</a>

    <hr>

    <table border="1" cellpadding="8">
        <tr>
            <th>ID</th>
            <th>Producto</th>
            <th>Precio</th>
            <th>Stock</th>
            <th>Acciones</th>
        </tr>
    """

    for p in products:

        color = "black"
        if p[3] <= 5:
            color = "red"

        html += f"""
        <tr style="color:{color}">
            <td>{p[0]}</td>
            <td>{p[1]}</td>
            <td>S/{p[2]}</td>
            <td>{p[3]}</td>
            <td>
                <a href='/sell/{p[0]}'>Vender</a> |
                <a href='/edit/{p[0]}'>Editar</a>
            </td>
        </tr>
        """

    html += "</table>"

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

# ---------------- EDIT ----------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    conn = get_db()
    c = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        price = request.form["price"]
        stock = request.form["stock"]

        c.execute("""
            UPDATE products
            SET name=%s, price=%s, stock=%s
            WHERE id=%s
        """, (name, price, stock, id))

        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))

    c.execute("SELECT * FROM products WHERE id=%s", (id,))
    p = c.fetchone()
    conn.close()

    return f"""
    <h2>Editar producto</h2>
    <form method="POST">
        <input name="name" value="{p[1]}"><br><br>
        <input name="price" value="{p[2]}"><br><br>
        <input name="stock" value="{p[3]}"><br><br>
        <button>Guardar</button>
    </form>
    """

# ---------------- VENTAS ----------------
@app.route("/ventas")
def ventas():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    c = conn.cursor()

    c.execute("""
        SELECT s.id, p.name, s.quantity, s.total, s.date
        FROM sales s
        JOIN products p ON s.product_id = p.id
        ORDER BY s.id DESC
    """)

    ventas = c.fetchall()
    conn.close()

    html = "<h2>💰 Ventas</h2>"
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

    html += f"<br><h2>Total: S/{total_general}</h2>"

    return html

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()