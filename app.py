from flask import Flask, request, redirect, url_for, session, jsonify
import psycopg2
import psycopg2.extras
import os
from datetime import datetime, date
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave_secreta_pos_2024")

DB_URL = os.environ.get(
    "DB_URL",
    "postgresql://postgres:bg4BarSND11nN3hU@db.muzoufplncpyumoaqmet.supabase.co:5432/postgres"
)

def get_db():
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = False
    return conn

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

CSS = """
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Inter', sans-serif; background: #0f1117; color: #e2e8f0; min-height: 100vh; }

  /* NAV */
  .nav {
    background: #1a1d27;
    border-bottom: 1px solid #2d3148;
    padding: 0 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 60px;
    position: sticky; top: 0; z-index: 100;
  }
  .nav-brand { font-size: 1.1rem; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 0.5rem; }
  .nav-brand span { background: #4f6ef7; color: #fff; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; }
  .nav-links { display: flex; gap: 0.5rem; }
  .nav-links a {
    color: #94a3b8; text-decoration: none; padding: 6px 14px;
    border-radius: 8px; font-size: 0.875rem; font-weight: 500;
    display: flex; align-items: center; gap: 6px; transition: all 0.2s;
  }
  .nav-links a:hover { background: #2d3148; color: #fff; }
  .nav-links a.danger:hover { background: #3d1f1f; color: #f87171; }
  .nav-user { font-size: 0.8rem; color: #64748b; display: flex; align-items: center; gap: 8px; }
  .avatar { width: 32px; height: 32px; background: #4f6ef7; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.8rem; color: #fff; }

  /* LAYOUT */
  .container { max-width: 1300px; margin: 0 auto; padding: 2rem; }
  .page-header { margin-bottom: 2rem; }
  .page-header h1 { font-size: 1.5rem; font-weight: 700; color: #fff; }
  .page-header p { color: #64748b; font-size: 0.875rem; margin-top: 4px; }

  /* STATS */
  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
  .stat-card {
    background: #1a1d27; border: 1px solid #2d3148;
    border-radius: 12px; padding: 1.25rem;
  }
  .stat-label { font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }
  .stat-value { font-size: 1.75rem; font-weight: 700; color: #fff; }
  .stat-sub { font-size: 0.75rem; color: #64748b; margin-top: 4px; }
  .stat-card.blue .stat-value { color: #60a5fa; }
  .stat-card.green .stat-value { color: #34d399; }
  .stat-card.amber .stat-value { color: #fbbf24; }
  .stat-card.red .stat-value { color: #f87171; }

  /* TABLE */
  .table-card { background: #1a1d27; border: 1px solid #2d3148; border-radius: 12px; overflow: hidden; }
  .table-header { padding: 1rem 1.5rem; border-bottom: 1px solid #2d3148; display: flex; align-items: center; justify-content: space-between; }
  .table-header h2 { font-size: 1rem; font-weight: 600; color: #fff; }
  table { width: 100%; border-collapse: collapse; }
  th { background: #12141e; padding: 0.75rem 1.5rem; text-align: left; font-size: 0.75rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }
  td { padding: 0.875rem 1.5rem; border-top: 1px solid #2d3148; font-size: 0.875rem; vertical-align: middle; }
  tr:hover td { background: #1e2130; }
  .badge {
    display: inline-flex; align-items: center; padding: 3px 10px;
    border-radius: 20px; font-size: 0.75rem; font-weight: 600;
  }
  .badge-green { background: #052e16; color: #34d399; }
  .badge-amber { background: #2d1f00; color: #fbbf24; }
  .badge-red { background: #2d0f0f; color: #f87171; }
  .product-name { font-weight: 500; color: #e2e8f0; }
  .price { font-weight: 600; color: #60a5fa; font-family: 'Inter', monospace; }
  .action-btn {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 5px 12px; border-radius: 7px; font-size: 0.8rem;
    font-weight: 500; text-decoration: none; transition: all 0.2s; margin: 0 2px;
    border: 1px solid transparent;
  }
  .btn-sell { background: #1a3a1a; color: #34d399; border-color: #1e4d1e; }
  .btn-sell:hover { background: #34d399; color: #052e16; }
  .btn-edit { background: #1a2a4a; color: #60a5fa; border-color: #1e3a6e; }
  .btn-edit:hover { background: #60a5fa; color: #0c1a3a; }
  .btn-delete { background: #2d0f0f; color: #f87171; border-color: #3d1515; }
  .btn-delete:hover { background: #f87171; color: #2d0f0f; }

  /* SEARCH / FILTER BAR */
  .toolbar { padding: 1rem 1.5rem; border-bottom: 1px solid #2d3148; display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap; }
  .search-input {
    background: #12141e; border: 1px solid #2d3148; color: #e2e8f0;
    padding: 8px 14px; border-radius: 8px; font-size: 0.875rem; width: 260px; outline: none;
  }
  .search-input:focus { border-color: #4f6ef7; }
  .search-input::placeholder { color: #475569; }

  /* BUTTONS */
  .btn-primary {
    background: #4f6ef7; color: #fff; border: none;
    padding: 8px 18px; border-radius: 8px; font-size: 0.875rem;
    font-weight: 600; cursor: pointer; text-decoration: none;
    display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s;
  }
  .btn-primary:hover { background: #3d5be0; }
  .btn-secondary {
    background: transparent; color: #94a3b8; border: 1px solid #2d3148;
    padding: 8px 18px; border-radius: 8px; font-size: 0.875rem;
    font-weight: 500; cursor: pointer; text-decoration: none;
    display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s;
  }
  .btn-secondary:hover { background: #2d3148; color: #fff; }

  /* FORMS */
  .form-card { background: #1a1d27; border: 1px solid #2d3148; border-radius: 16px; padding: 2rem; max-width: 480px; }
  .form-group { margin-bottom: 1.25rem; }
  label { display: block; font-size: 0.8rem; font-weight: 600; color: #94a3b8; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.04em; }
  input[type=text], input[type=password], input[type=number], input[type=search], select {
    width: 100%; background: #12141e; border: 1px solid #2d3148;
    color: #e2e8f0; padding: 10px 14px; border-radius: 8px;
    font-size: 0.95rem; outline: none; transition: border 0.2s;
  }
  input:focus, select:focus { border-color: #4f6ef7; }
  input::placeholder { color: #475569; }

  /* LOGIN */
  .login-wrapper { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #0f1117; }
  .login-card { background: #1a1d27; border: 1px solid #2d3148; border-radius: 20px; padding: 2.5rem; width: 380px; }
  .login-logo { text-align: center; margin-bottom: 2rem; }
  .login-logo h1 { font-size: 1.5rem; font-weight: 800; color: #fff; }
  .login-logo p { color: #64748b; font-size: 0.875rem; margin-top: 4px; }
  .login-logo img { width: 80px; border-radius: 12px; margin-bottom: 1rem; }

  /* VENTAS */
  .venta-row { display: flex; align-items: center; justify-content: space-between; padding: 0.875rem 1.5rem; border-top: 1px solid #2d3148; font-size: 0.875rem; }
  .venta-row:hover { background: #1e2130; }
  .total-bar { background: #12141e; padding: 1rem 1.5rem; display: flex; justify-content: space-between; align-items: center; }
  .total-bar span { font-size: 0.875rem; color: #64748b; }
  .total-bar strong { font-size: 1.1rem; color: #34d399; font-weight: 700; }

  /* ALERT */
  .alert { padding: 0.75rem 1.25rem; border-radius: 8px; margin-bottom: 1rem; font-size: 0.875rem; }
  .alert-error { background: #2d0f0f; border: 1px solid #f87171; color: #f87171; }
  .alert-success { background: #052e16; border: 1px solid #34d399; color: #34d399; }

  /* EMPTY */
  .empty-state { text-align: center; padding: 3rem; color: #475569; }
  .empty-state p { font-size: 0.95rem; }

  .flex { display: flex; }
  .items-center { align-items: center; }
  .justify-between { justify-content: space-between; }
  .gap-2 { gap: 0.5rem; }
  .gap-3 { gap: 0.75rem; }
  .mb-1 { margin-bottom: 1rem; }
</style>
"""

def nav(user):
    initial = user[0].upper()
    return f"""
    <nav class="nav">
      <div class="nav-brand">&#9776; POS <span>Sistema</span></div>
      <div class="nav-links">
        <a href='/dashboard'>&#9783; Inventario</a>
        <a href='/ventas'>&#128200; Ventas</a>
        <a href='/add'>&#43; Producto</a>
        <a href='/logout' class='danger'>&#8594; Salir</a>
      </div>
      <div class="nav-user">
        <div class="avatar">{initial}</div>
        <span>{user}</span>
      </div>
    </nav>
    """

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            user = c.fetchone()
            conn.close()
            if user:
                session["user"] = username
                return redirect(url_for("dashboard"))
            error = "Usuario o contraseña incorrectos"
        except Exception as e:
            error = f"Error de conexión: {str(e)}"

    logo_tag = '<img src="/static/logo.gif">' if os.path.exists("static/logo.gif") else ""

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">{CSS}<title>POS - Login</title></head><body>
    <div class="login-wrapper">
      <div class="login-card">
        <div class="login-logo">
          {logo_tag}
          <h1>&#9783; POS Sistema</h1>
          <p>Ingresa tus credenciales para continuar</p>
        </div>
        {'<div class="alert alert-error">' + error + '</div>' if error else ''}
        <form method="POST">
          <div class="form-group">
            <label>Usuario</label>
            <input name="username" placeholder="Ingresa tu usuario" required autofocus>
          </div>
          <div class="form-group">
            <label>Contraseña</label>
            <input name="password" type="password" placeholder="&#9679;&#9679;&#9679;&#9679;&#9679;&#9679;&#9679;&#9679;" required>
          </div>
          <button class="btn-primary" type="submit" style="width:100%; justify-content:center; padding:12px;">
            Iniciar sesión
          </button>
        </form>
      </div>
    </div>
    </body></html>"""

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    c.execute("SELECT * FROM products ORDER BY name ASC")
    products = c.fetchall()

    c.execute("SELECT COUNT(*) FROM products")
    total_productos = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM products WHERE stock <= 5")
    stock_bajo = c.fetchone()[0]

    c.execute("SELECT COALESCE(SUM(total), 0) FROM sales WHERE DATE(created_at) = CURRENT_DATE")
    ventas_hoy = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM sales WHERE DATE(created_at) = CURRENT_DATE")
    num_ventas_hoy = c.fetchone()[0]

    conn.close()

    rows = ""
    for p in products:
        stock = p["stock"]
        if stock <= 0:
            badge = '<span class="badge badge-red">Sin stock</span>'
        elif stock <= 5:
            badge = f'<span class="badge badge-amber">{stock} uds</span>'
        else:
            badge = f'<span class="badge badge-green">{stock} uds</span>'

        rows += f"""
        <tr>
          <td style="color:#475569; font-size:0.8rem;">{p['id']}</td>
          <td><span class="product-name">{p['name']}</span></td>
          <td><span class="price">S/ {float(p['price']):.2f}</span></td>
          <td>{badge}</td>
          <td>
            <a href='/sell/{p['id']}' class='action-btn btn-sell'>&#9654; Vender</a>
            <a href='/edit/{p['id']}' class='action-btn btn-edit'>&#9998; Editar</a>
            <a href='/delete/{p['id']}' class='action-btn btn-delete' onclick="return confirm('¿Eliminar producto?')">&#10005;</a>
          </td>
        </tr>"""

    if not rows:
        rows = '<tr><td colspan="5"><div class="empty-state"><p>No hay productos. <a href="/add" style="color:#4f6ef7;">Agrega el primero</a></p></div></td></tr>'

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">{CSS}<title>POS - Dashboard</title>
    <script>
    function filterTable() {{
      const q = document.getElementById('search').value.toLowerCase();
      document.querySelectorAll('tbody tr').forEach(row => {{
        row.style.display = row.innerText.toLowerCase().includes(q) ? '' : 'none';
      }});
    }}
    </script>
    </head><body>
    {nav(session['user'])}
    <div class="container">
      <div class="page-header">
        <h1>Inventario</h1>
        <p>Gestiona tus productos y realiza ventas</p>
      </div>

      <div class="stats-grid">
        <div class="stat-card blue">
          <div class="stat-label">Productos</div>
          <div class="stat-value">{total_productos}</div>
          <div class="stat-sub">En inventario</div>
        </div>
        <div class="stat-card green">
          <div class="stat-label">Ventas hoy</div>
          <div class="stat-value">S/ {float(ventas_hoy):.2f}</div>
          <div class="stat-sub">{num_ventas_hoy} transacciones</div>
        </div>
        <div class="stat-card {'red' if stock_bajo > 0 else 'green'}">
          <div class="stat-label">Stock bajo</div>
          <div class="stat-value">{stock_bajo}</div>
          <div class="stat-sub">Productos con ≤ 5 unidades</div>
        </div>
      </div>

      <div class="table-card">
        <div class="table-header">
          <h2>Lista de productos</h2>
          <a href='/add' class='btn-primary'>+ Agregar producto</a>
        </div>
        <div class="toolbar">
          <input class="search-input" id="search" type="search" placeholder="Buscar producto..." oninput="filterTable()">
        </div>
        <table>
          <thead><tr>
            <th>ID</th><th>Producto</th><th>Precio</th><th>Stock</th><th>Acciones</th>
          </tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </div>
    </body></html>"""

# ---------------- ADD ----------------
@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    error = ""
    if request.method == "POST":
        name = request.form["name"].strip()
        price = request.form["price"]
        stock = request.form["stock"]
        category = request.form.get("category", "").strip()
        try:
            conn = get_db()
            c = conn.cursor()
            c.execute(
                "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s)",
                (name, float(price), int(stock))
            )
            conn.commit()
            conn.close()
            return redirect(url_for("dashboard"))
        except Exception as e:
            error = f"Error al guardar: {str(e)}"

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">{CSS}<title>Agregar Producto</title></head><body>
    {nav(session['user'])}
    <div class="container">
      <div class="page-header">
        <h1>Agregar producto</h1>
        <p>Completa los datos del nuevo producto</p>
      </div>
      {'<div class="alert alert-error">' + error + '</div>' if error else ''}
      <div class="form-card">
        <form method="POST">
          <div class="form-group">
            <label>Nombre del producto</label>
            <input name="name" placeholder="Ej: Coca Cola 500ml" required>
          </div>
          <div class="form-group">
            <label>Precio (S/)</label>
            <input name="price" type="number" step="0.01" min="0" placeholder="0.00" required>
          </div>
          <div class="form-group">
            <label>Stock inicial</label>
            <input name="stock" type="number" min="0" placeholder="0" required>
          </div>
          <div style="display:flex; gap:0.75rem; margin-top:1.5rem;">
            <button class="btn-primary" type="submit">Guardar producto</button>
            <a href="/dashboard" class="btn-secondary">Cancelar</a>
          </div>
        </form>
      </div>
    </div>
    </body></html>"""

# ---------------- SELL ----------------
@app.route("/sell/<int:id>")
@login_required
def sell(id):
    try:
        conn = get_db()
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        c.execute("SELECT * FROM products WHERE id=%s", (id,))
        product = c.fetchone()
        if product and product["stock"] > 0:
            c.execute("UPDATE products SET stock=%s WHERE id=%s", (product["stock"] - 1, id))
            c.execute(
                "INSERT INTO sales (product_id, quantity, total) VALUES (%s, %s, %s)",
                (id, 1, product["price"])
            )
            conn.commit()
        conn.close()
    except Exception as e:
        pass
    return redirect(url_for("dashboard"))

# ---------------- SELL QUANTITY ----------------
@app.route("/sell_qty/<int:id>", methods=["POST"])
@login_required
def sell_qty(id):
    qty = int(request.form.get("qty", 1))
    try:
        conn = get_db()
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        c.execute("SELECT * FROM products WHERE id=%s", (id,))
        product = c.fetchone()
        if product and product["stock"] >= qty:
            c.execute("UPDATE products SET stock=%s WHERE id=%s", (product["stock"] - qty, id))
            c.execute(
                "INSERT INTO sales (product_id, quantity, total) VALUES (%s, %s, %s)",
                (id, qty, float(product["price"]) * qty)
            )
            conn.commit()
        conn.close()
    except:
        pass
    return redirect(url_for("dashboard"))

# ---------------- EDIT ----------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    conn = get_db()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    error = ""
    if request.method == "POST":
        name = request.form["name"].strip()
        price = request.form["price"]
        stock = request.form["stock"]
        try:
            c.execute(
                "UPDATE products SET name=%s, price=%s, stock=%s WHERE id=%s",
                (name, float(price), int(stock), id)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("dashboard"))
        except Exception as e:
            error = f"Error al actualizar: {str(e)}"

    c.execute("SELECT * FROM products WHERE id=%s", (id,))
    p = c.fetchone()
    conn.close()
    if not p:
        return redirect(url_for("dashboard"))

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">{CSS}<title>Editar Producto</title></head><body>
    {nav(session['user'])}
    <div class="container">
      <div class="page-header">
        <h1>Editar producto</h1>
        <p>Modifica los datos del producto</p>
      </div>
      {'<div class="alert alert-error">' + error + '</div>' if error else ''}
      <div class="form-card">
        <form method="POST">
          <div class="form-group">
            <label>Nombre</label>
            <input name="name" value="{p['name']}" required>
          </div>
          <div class="form-group">
            <label>Precio (S/)</label>
            <input name="price" type="number" step="0.01" min="0" value="{float(p['price']):.2f}" required>
          </div>
          <div class="form-group">
            <label>Stock</label>
            <input name="stock" type="number" min="0" value="{p['stock']}" required>
          </div>
          <div style="display:flex; gap:0.75rem; margin-top:1.5rem;">
            <button class="btn-primary" type="submit">Guardar cambios</button>
            <a href="/dashboard" class="btn-secondary">Cancelar</a>
          </div>
        </form>
      </div>
    </div>
    </body></html>"""

# ---------------- DELETE ----------------
@app.route("/delete/<int:id>")
@login_required
def delete(id):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("DELETE FROM products WHERE id=%s", (id,))
        conn.commit()
        conn.close()
    except:
        pass
    return redirect(url_for("dashboard"))

# ---------------- VENTAS ----------------
@app.route("/ventas")
@login_required
def ventas():
    conn = get_db()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    filtro = request.args.get("filtro", "hoy")

    if filtro == "hoy":
        where = "WHERE DATE(s.created_at) = CURRENT_DATE"
        label_filtro = "Hoy"
    elif filtro == "semana":
        where = "WHERE s.created_at >= CURRENT_DATE - INTERVAL '7 days'"
        label_filtro = "Últimos 7 días"
    elif filtro == "mes":
        where = "WHERE DATE_TRUNC('month', s.created_at) = DATE_TRUNC('month', CURRENT_DATE)"
        label_filtro = "Este mes"
    else:
        where = ""
        label_filtro = "Todo el historial"

    c.execute(f"""
        SELECT s.id, p.name, s.quantity, s.total, s.created_at
        FROM sales s
        JOIN products p ON s.product_id = p.id
        {where}
        ORDER BY s.id DESC
    """)
    ventas_list = c.fetchall()

    c.execute(f"SELECT COALESCE(SUM(s.total), 0) FROM sales s {where}")
    total_general = float(c.fetchone()[0])

    c.execute(f"SELECT COUNT(*) FROM sales s {where}")
    num_ventas = c.fetchone()[0]

    conn.close()

    rows = ""
    for v in ventas_list:
        fecha = v["created_at"].strftime("%d/%m/%Y %H:%M") if v["created_at"] else "-"
        rows += f"""
        <tr>
          <td style="color:#475569; font-size:0.8rem;">#{v['id']}</td>
          <td><span class="product-name">{v['name']}</span></td>
          <td><span class="badge badge-green">{v['quantity']} uds</span></td>
          <td><span class="price">S/ {float(v['total']):.2f}</span></td>
          <td style="color:#64748b; font-size:0.8rem;">{fecha}</td>
        </tr>"""

    if not rows:
        rows = '<tr><td colspan="5"><div class="empty-state"><p>No hay ventas en este período</p></div></td></tr>'

    filtro_links = ""
    for f, label in [("hoy","Hoy"), ("semana","7 días"), ("mes","Mes"), ("todo","Todo")]:
        active = "background:#2d3148; color:#fff;" if filtro == f else ""
        filtro_links += f'<a href="/ventas?filtro={f}" style="padding:6px 14px; border-radius:7px; text-decoration:none; font-size:0.8rem; color:#94a3b8; {active}">{label}</a>'

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">{CSS}<title>POS - Ventas</title></head><body>
    {nav(session['user'])}
    <div class="container">
      <div class="page-header">
        <h1>Historial de ventas</h1>
        <p>Revisa todas las transacciones realizadas</p>
      </div>

      <div class="stats-grid">
        <div class="stat-card green">
          <div class="stat-label">Total ({label_filtro})</div>
          <div class="stat-value">S/ {total_general:.2f}</div>
          <div class="stat-sub">Ingresos del período</div>
        </div>
        <div class="stat-card blue">
          <div class="stat-label">Transacciones</div>
          <div class="stat-value">{num_ventas}</div>
          <div class="stat-sub">{label_filtro}</div>
        </div>
      </div>

      <div class="table-card">
        <div class="table-header">
          <h2>Ventas — {label_filtro}</h2>
          <div style="display:flex; gap:4px; background:#12141e; padding:4px; border-radius:10px;">
            {filtro_links}
          </div>
        </div>
        <table>
          <thead><tr>
            <th>#</th><th>Producto</th><th>Cantidad</th><th>Total</th><th>Fecha</th>
          </tr></thead>
          <tbody>{rows}</tbody>
        </table>
        <div class="total-bar">
          <span>{num_ventas} ventas registradas</span>
          <strong>Total: S/ {total_general:.2f}</strong>
        </div>
      </div>
    </div>
    </body></html>"""

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)