from flask import Flask, request, redirect, url_for, session, jsonify, Response
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

# ================================================================
# CSS + JS GLOBAL
# ================================================================
CSS = """
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
  :root {
    --bg: #080b12; --surface: #0e1420; --surface2: #141928;
    --border: #1e2640; --border2: #252d45;
    --text: #e2e8f0; --muted: #64748b; --muted2: #94a3b8;
    --blue: #4f6ef7; --blue2: #3d5be0; --blue-glow: rgba(79,110,247,0.15);
    --green: #10b981; --green2: #059669; --green-dim: #052e16; --green-text: #34d399;
    --amber: #f59e0b; --amber-dim: #2d1f00; --amber-text: #fbbf24;
    --red: #ef4444; --red-dim: #2d0f0f; --red-text: #f87171;
    --radius: 12px; --radius-sm: 8px;
  }
  html { scroll-behavior: smooth; }
  body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; -webkit-font-smoothing: antialiased; }

  /* ---- SCROLLBAR ---- */
  ::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }

  /* ---- SIDEBAR ---- */
  .sidebar {
    position: fixed; top: 0; left: 0; height: 100vh; width: 260px;
    background: var(--surface); border-right: 1px solid var(--border);
    transform: translateX(-260px); transition: transform 0.3s cubic-bezier(.4,0,.2,1);
    z-index: 200; display: flex; flex-direction: column; padding: 1.5rem 1rem;
    box-shadow: 4px 0 40px rgba(0,0,0,0.4);
  }
  .sidebar.open { transform: translateX(0); }
  .sidebar-overlay {
    position: fixed; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(2px);
    z-index: 199; display: none;
  }
  .sidebar-overlay.open { display: block; }
  .sidebar-title { font-size: 0.7rem; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; padding: 0.5rem 0.75rem; margin-top: 1rem; margin-bottom: 0.25rem; }
  .sidebar a {
    display: flex; align-items: center; gap: 0.75rem; padding: 0.65rem 0.75rem;
    color: var(--muted2); text-decoration: none; border-radius: var(--radius-sm);
    font-size: 0.875rem; font-weight: 500; transition: all 0.15s; margin-bottom: 2px;
  }
  .sidebar a:hover, .sidebar a.active { background: var(--blue-glow); color: #fff; }
  .sidebar a .icon { width: 18px; text-align: center; font-size: 1rem; }
  .sidebar-close { position: absolute; top: 1rem; right: 1rem; background: var(--border); border: none; color: var(--muted2); width: 28px; height: 28px; border-radius: 50%; cursor: pointer; font-size: 1rem; display: flex; align-items: center; justify-content: center; }

  /* ---- NAV ---- */
  .nav {
    background: var(--surface); border-bottom: 1px solid var(--border);
    padding: 0 1.5rem; display: flex; align-items: center; justify-content: space-between;
    height: 58px; position: sticky; top: 0; z-index: 100;
    backdrop-filter: blur(12px);
  }
  .nav-left { display: flex; align-items: center; gap: 1rem; }
  .hamburger { background: none; border: none; color: var(--muted2); cursor: pointer; padding: 6px; border-radius: var(--radius-sm); font-size: 1.2rem; transition: all 0.15s; display: flex; align-items: center; }
  .hamburger:hover { background: var(--border); color: #fff; }
  .nav-brand { font-size: 1rem; font-weight: 800; color: #fff; display: flex; align-items: center; gap: 0.5rem; letter-spacing: -0.01em; }
  .nav-brand .chip { background: var(--blue); color: #fff; padding: 2px 8px; border-radius: 6px; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.03em; }
  .nav-links { display: flex; gap: 0.25rem; }
  .nav-links a {
    color: var(--muted2); text-decoration: none; padding: 6px 12px;
    border-radius: var(--radius-sm); font-size: 0.8rem; font-weight: 500;
    display: flex; align-items: center; gap: 5px; transition: all 0.15s;
  }
  .nav-links a:hover { background: var(--border); color: #fff; }
  .nav-links a.danger:hover { background: var(--red-dim); color: var(--red-text); }
  .nav-user { display: flex; align-items: center; gap: 8px; }
  .avatar { width: 30px; height: 30px; background: linear-gradient(135deg, var(--blue), #7c3aed); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.75rem; color: #fff; }
  .nav-username { font-size: 0.8rem; color: var(--muted2); font-weight: 500; }

  /* ---- LAYOUT ---- */
  .container { max-width: 1320px; margin: 0 auto; padding: 1.75rem 2rem; }
  .page-header { margin-bottom: 1.75rem; display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 1rem; }
  .page-header-left h1 { font-size: 1.4rem; font-weight: 800; color: #fff; letter-spacing: -0.02em; }
  .page-header-left p { color: var(--muted); font-size: 0.825rem; margin-top: 3px; }

  /* ---- STATS ---- */
  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 1rem; margin-bottom: 1.75rem; }
  .stat-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.25rem 1.5rem;
    transition: border-color 0.2s, transform 0.2s;
    cursor: default; position: relative; overflow: hidden;
  }
  .stat-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; border-radius: 2px 2px 0 0; }
  .stat-card.blue::before { background: var(--blue); }
  .stat-card.green::before { background: var(--green); }
  .stat-card.amber::before { background: var(--amber); }
  .stat-card.red::before { background: var(--red); }
  .stat-card:hover { border-color: var(--border2); transform: translateY(-2px); }
  .stat-label { font-size: 0.7rem; color: var(--muted); font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.6rem; }
  .stat-value { font-size: 1.65rem; font-weight: 800; letter-spacing: -0.02em; }
  .stat-sub { font-size: 0.72rem; color: var(--muted); margin-top: 5px; }
  .stat-card.blue .stat-value { color: #60a5fa; }
  .stat-card.green .stat-value { color: var(--green-text); }
  .stat-card.amber .stat-value { color: var(--amber-text); }
  .stat-card.red .stat-value { color: var(--red-text); }

  /* ---- TABLE ---- */
  .table-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
  .table-header { padding: 1rem 1.5rem; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
  .table-header h2 { font-size: 0.95rem; font-weight: 700; color: #fff; }
  table { width: 100%; border-collapse: collapse; }
  th { background: #0a0d16; padding: 0.65rem 1.5rem; text-align: left; font-size: 0.68rem; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; }
  td { padding: 0.8rem 1.5rem; border-top: 1px solid var(--border); font-size: 0.85rem; vertical-align: middle; }
  tr:hover td { background: var(--surface2); }
  .badge { display: inline-flex; align-items: center; padding: 3px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 700; }
  .badge-green { background: var(--green-dim); color: var(--green-text); }
  .badge-amber { background: var(--amber-dim); color: var(--amber-text); }
  .badge-red { background: var(--red-dim); color: var(--red-text); }
  .badge-blue { background: rgba(79,110,247,0.15); color: #93b4ff; }
  .product-name { font-weight: 600; color: var(--text); }
  .price { font-weight: 700; color: #60a5fa; font-variant-numeric: tabular-nums; }
  .action-btn {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 5px 11px; border-radius: 7px; font-size: 0.78rem;
    font-weight: 600; text-decoration: none; transition: all 0.15s; margin: 0 2px;
    border: 1px solid transparent; white-space: nowrap;
  }
  .btn-sell { background: rgba(16,185,129,0.1); color: var(--green-text); border-color: rgba(16,185,129,0.2); }
  .btn-sell:hover { background: var(--green); color: #fff; border-color: var(--green); }
  .btn-edit { background: rgba(79,110,247,0.1); color: #93b4ff; border-color: rgba(79,110,247,0.2); }
  .btn-edit:hover { background: var(--blue); color: #fff; border-color: var(--blue); }
  .btn-delete { background: rgba(239,68,68,0.08); color: var(--red-text); border-color: rgba(239,68,68,0.2); }
  .btn-delete:hover { background: var(--red); color: #fff; border-color: var(--red); }
  .btn-receipt { background: rgba(245,158,11,0.1); color: var(--amber-text); border-color: rgba(245,158,11,0.2); }
  .btn-receipt:hover { background: var(--amber); color: #000; border-color: var(--amber); }

  /* ---- TOOLBAR ---- */
  .toolbar { padding: 0.875rem 1.5rem; border-bottom: 1px solid var(--border); display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap; }
  .search-input {
    background: var(--bg); border: 1px solid var(--border); color: var(--text);
    padding: 7px 14px; border-radius: var(--radius-sm); font-size: 0.85rem; width: 280px; outline: none; transition: border 0.2s;
  }
  .search-input:focus { border-color: var(--blue); }
  .search-input::placeholder { color: var(--muted); }

  /* ---- BUTTONS ---- */
  .btn-primary {
    background: var(--blue); color: #fff; border: none;
    padding: 8px 18px; border-radius: var(--radius-sm); font-size: 0.85rem;
    font-weight: 700; cursor: pointer; text-decoration: none;
    display: inline-flex; align-items: center; gap: 6px; transition: all 0.15s;
    letter-spacing: 0.01em;
  }
  .btn-primary:hover { background: var(--blue2); transform: translateY(-1px); box-shadow: 0 4px 20px rgba(79,110,247,0.3); }
  .btn-secondary {
    background: transparent; color: var(--muted2); border: 1px solid var(--border);
    padding: 8px 18px; border-radius: var(--radius-sm); font-size: 0.85rem;
    font-weight: 500; cursor: pointer; text-decoration: none;
    display: inline-flex; align-items: center; gap: 6px; transition: all 0.15s;
  }
  .btn-secondary:hover { background: var(--border); color: #fff; }

  /* ---- FORMS ---- */
  .form-card { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 2rem; max-width: 500px; }
  .form-group { margin-bottom: 1.25rem; }
  label { display: block; font-size: 0.72rem; font-weight: 700; color: var(--muted2); margin-bottom: 7px; text-transform: uppercase; letter-spacing: 0.06em; }
  input, select, textarea {
    width: 100%; background: var(--bg) !important; border: 1px solid var(--border);
    color: var(--text) !important; padding: 10px 14px; border-radius: var(--radius-sm);
    font-size: 0.9rem; outline: none; transition: border 0.2s; font-family: 'Inter', sans-serif;
    -webkit-text-fill-color: var(--text) !important;
  }
  input:-webkit-autofill, input:-webkit-autofill:hover, input:-webkit-autofill:focus {
    -webkit-box-shadow: 0 0 0 1000px #080b12 inset !important;
    -webkit-text-fill-color: #e2e8f0 !important; border: 1px solid var(--border) !important;
    caret-color: #e2e8f0;
  }
  input:focus, select:focus { border-color: var(--blue); box-shadow: 0 0 0 3px var(--blue-glow); }
  input::placeholder { color: var(--muted) !important; }

  /* ---- LOGIN ---- */
  .login-wrapper { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: var(--bg); background-image: radial-gradient(ellipse at 20% 50%, rgba(79,110,247,0.06) 0%, transparent 60%), radial-gradient(ellipse at 80% 20%, rgba(124,58,237,0.05) 0%, transparent 50%); }
  .login-card { background: var(--surface); border: 1px solid var(--border); border-radius: 24px; padding: 2.5rem; width: 400px; box-shadow: 0 25px 60px rgba(0,0,0,0.5); }
  .login-logo { text-align: center; margin-bottom: 2rem; }
  .login-logo h1 { font-size: 1.6rem; font-weight: 900; color: #fff; letter-spacing: -0.02em; }
  .login-logo p { color: var(--muted); font-size: 0.85rem; margin-top: 5px; }
  .login-logo img { max-width: 130px; border-radius: 14px; margin-bottom: 1rem; }

  /* ---- ALERTS ---- */
  .alert { padding: 0.75rem 1.25rem; border-radius: var(--radius-sm); margin-bottom: 1rem; font-size: 0.85rem; font-weight: 500; }
  .alert-error { background: var(--red-dim); border: 1px solid rgba(239,68,68,0.3); color: var(--red-text); }
  .alert-success { background: var(--green-dim); border: 1px solid rgba(16,185,129,0.3); color: var(--green-text); }

  /* ---- TOTAL BAR ---- */
  .total-bar { background: #0a0d16; padding: 1rem 1.5rem; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border); }
  .total-bar span { font-size: 0.8rem; color: var(--muted); }
  .total-bar strong { font-size: 1.1rem; color: var(--green-text); font-weight: 800; }

  /* ---- EMPTY STATE ---- */
  .empty-state { text-align: center; padding: 3.5rem; color: var(--muted); }
  .empty-state .empty-icon { font-size: 2.5rem; margin-bottom: 1rem; opacity: 0.4; }
  .empty-state p { font-size: 0.9rem; }

  /* ---- TOOLTIP ---- */
  .has-tooltip { position: relative; cursor: default; }
  .tooltip {
    position: absolute; bottom: calc(100% + 8px); left: 50%; transform: translateX(-50%);
    background: #1e2640; border: 1px solid var(--border2); color: var(--text);
    padding: 8px 12px; border-radius: 8px; font-size: 0.75rem; white-space: nowrap;
    opacity: 0; pointer-events: none; transition: opacity 0.2s;
    z-index: 50; box-shadow: 0 8px 24px rgba(0,0,0,0.4); line-height: 1.6;
  }
  .tooltip::after { content: ''; position: absolute; top: 100%; left: 50%; transform: translateX(-50%); border: 5px solid transparent; border-top-color: var(--border2); }
  .has-tooltip:hover .tooltip { opacity: 1; }

  /* ---- MODAL FACTURA ---- */
  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(4px); z-index: 300; display: none; align-items: center; justify-content: center; }
  .modal-overlay.open { display: flex; }
  .modal { background: var(--surface); border: 1px solid var(--border); border-radius: 20px; padding: 2rem; width: 420px; max-width: 95vw; box-shadow: 0 30px 80px rgba(0,0,0,0.5); }
  .modal h2 { font-size: 1.1rem; font-weight: 800; color: #fff; margin-bottom: 1.25rem; display: flex; align-items: center; gap: 8px; }
  .receipt { background: #fff; color: #111; border-radius: 10px; padding: 1.5rem; font-family: 'Courier New', monospace; font-size: 0.8rem; line-height: 1.8; }
  .receipt .r-title { text-align: center; font-size: 1rem; font-weight: 900; margin-bottom: 0.25rem; }
  .receipt .r-sub { text-align: center; color: #555; font-size: 0.72rem; margin-bottom: 1rem; }
  .receipt .r-line { border-top: 1px dashed #bbb; margin: 0.5rem 0; }
  .receipt .r-row { display: flex; justify-content: space-between; }
  .receipt .r-total { display: flex; justify-content: space-between; font-weight: 900; font-size: 0.95rem; margin-top: 0.5rem; }
  .receipt .r-footer { text-align: center; color: #777; font-size: 0.7rem; margin-top: 1rem; }
  .modal-actions { display: flex; gap: 0.75rem; margin-top: 1.25rem; }

  /* ---- PRINT ---- */
  @media print { .no-print { display: none !important; } .receipt { box-shadow: none; } }
</style>
"""

# ================================================================
# SIDEBAR + NAV
# ================================================================
def sidebar():
    return """
    <div class="sidebar-overlay" id="overlay" onclick="closeSidebar()"></div>
    <div class="sidebar" id="sidebar">
      <button class="sidebar-close no-print" onclick="closeSidebar()">&#10005;</button>
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:1.5rem;padding:0 0.5rem;">
        <div style="width:36px;height:36px;background:linear-gradient(135deg,#4f6ef7,#7c3aed);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;">🏪</div>
        <div><div style="font-weight:800;color:#fff;font-size:0.95rem;">POS Sistema</div><div style="font-size:0.7rem;color:#64748b;">Panel de control</div></div>
      </div>

      <div class="sidebar-title">Principal</div>
      <a href="/dashboard"><span class="icon">📦</span> Inventario</a>
      <a href="/ventas"><span class="icon">📊</span> Ventas</a>
      <a href="/add"><span class="icon">➕</span> Agregar Producto</a>

      <div class="sidebar-title">Reportes</div>
      <a href="/ventas?filtro=hoy"><span class="icon">📅</span> Ventas de Hoy</a>
      <a href="/ventas?filtro=semana"><span class="icon">📈</span> Última Semana</a>
      <a href="/ventas?filtro=mes"><span class="icon">🗓️</span> Este Mes</a>
      <a href="/ventas?filtro=todo"><span class="icon">📋</span> Todo el Historial</a>

      <div style="margin-top:auto;padding-top:1rem;border-top:1px solid var(--border);">
        <a href="/logout" style="color:#f87171;"><span class="icon">🚪</span> Cerrar Sesión</a>
      </div>
    </div>
    <script>
    function openSidebar() {
      document.getElementById('sidebar').classList.add('open');
      document.getElementById('overlay').classList.add('open');
    }
    function closeSidebar() {
      document.getElementById('sidebar').classList.remove('open');
      document.getElementById('overlay').classList.remove('open');
    }
    </script>
    """

def nav(user):
    initial = user[0].upper()
    return f"""
    {sidebar()}
    <nav class="nav no-print">
      <div class="nav-left">
        <button class="hamburger" onclick="openSidebar()">&#9776;</button>
        <div class="nav-brand">POS <span class="chip">Sistema</span></div>
      </div>
      <div class="nav-links">
        <a href='/dashboard'>📦 Inventario</a>
        <a href='/ventas'>📊 Ventas</a>
        <a href='/add'>➕ Producto</a>
        <a href='/logout' class='danger'>🚪 Salir</a>
      </div>
      <div class="nav-user">
        <div class="avatar">{initial}</div>
        <span class="nav-username">{user}</span>
      </div>
    </nav>
    """

# ================================================================
# MODAL FACTURA / BOLETA
# ================================================================
def modal_receipt():
    return """
    <div class="modal-overlay no-print" id="receiptModal">
      <div class="modal">
        <h2>🧾 Comprobante de Venta</h2>
        <div class="receipt" id="receiptContent"></div>
        <div class="modal-actions">
          <button class="btn-primary" onclick="printReceipt()">🖨️ Imprimir</button>
          <button class="btn-secondary" onclick="closeReceipt()">Cerrar</button>
        </div>
      </div>
    </div>
    <script>
    function showReceipt(data) {
      const now = new Date();
      const fecha = now.toLocaleDateString('es-PE') + ' ' + now.toLocaleTimeString('es-PE', {hour:'2-digit',minute:'2-digit'});
      document.getElementById('receiptContent').innerHTML = `
        <div class="r-title">COMPROBANTE DE VENTA</div>
        <div class="r-sub">POS Sistema | ${fecha}</div>
        <div class="r-line"></div>
        <div class="r-row"><span>Producto:</span><span>${data.name}</span></div>
        <div class="r-row"><span>Cantidad:</span><span>${data.qty} uds.</span></div>
        <div class="r-row"><span>Precio unit.:</span><span>S/ ${parseFloat(data.price).toFixed(2)}</span></div>
        <div class="r-line"></div>
        <div class="r-total"><span>TOTAL:</span><span>S/ ${parseFloat(data.total).toFixed(2)}</span></div>
        <div class="r-line"></div>
        <div class="r-footer">Gracias por su compra<br>Conserve este comprobante</div>
      `;
      document.getElementById('receiptModal').classList.add('open');
    }
    function closeReceipt() {
      document.getElementById('receiptModal').classList.remove('open');
    }
    function printReceipt() {
      const content = document.getElementById('receiptContent').innerHTML;
      const win = window.open('', '_blank', 'width=400,height=500');
      win.document.write('<html><head><title>Comprobante</title><style>body{font-family:Courier New,monospace;padding:20px;font-size:13px;line-height:1.8}.r-title{text-align:center;font-size:16px;font-weight:900;margin-bottom:4px}.r-sub{text-align:center;color:#555;font-size:11px;margin-bottom:12px}.r-line{border-top:1px dashed #bbb;margin:6px 0}.r-row,.r-total{display:flex;justify-content:space-between}.r-total{font-weight:900;font-size:15px;margin-top:6px}.r-footer{text-align:center;color:#777;font-size:11px;margin-top:12px}</style></head><body>' + content + '</body></html>');
      win.document.close(); win.print(); win.close();
    }
    </script>
    """

# ================================================================
# LOGIN
# ================================================================
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

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">{CSS}<title>POS - Login</title></head><body>
    <div class="login-wrapper">
      <div class="login-card">
        <div class="login-logo">
          <img src="/static/logo.gif" onerror="this.style.display='none'">
          <h1>🏪 POS Sistema</h1>
          <p>Ingresa tus credenciales para continuar</p>
        </div>
        {'<div class="alert alert-error">⚠️ ' + error + '</div>' if error else ''}
        <form method="POST" autocomplete="off">
          <div class="form-group">
            <label>Usuario</label>
            <input name="username" type="text" autocomplete="new-password" placeholder="Tu usuario" required autofocus>
          </div>
          <div class="form-group">
            <label>Contraseña</label>
            <input name="password" type="password" autocomplete="new-password" placeholder="••••••••" required>
          </div>
          <button class="btn-primary" type="submit" style="width:100%;justify-content:center;padding:12px;font-size:0.95rem;margin-top:0.5rem;">
            Iniciar sesión →
          </button>
        </form>
      </div>
    </div>
    </body></html>"""

# ================================================================
# DASHBOARD
# ================================================================
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
    c.execute("SELECT COALESCE(SUM(total), 0) FROM sales")
    total_all = c.fetchone()[0]
    conn.close()

    rows = ""
    for p in products:
        stock = p["stock"]
        precio = float(p["price"])
        valor_inventario = precio * stock
        if stock <= 0:
            badge = '<span class="badge badge-red">Sin stock</span>'
            stock_tip = "Sin unidades disponibles"
        elif stock <= 5:
            badge = f'<span class="badge badge-amber">{stock} uds</span>'
            stock_tip = f"⚠️ Stock bajo: solo {stock} unidades restantes"
        else:
            badge = f'<span class="badge badge-green">{stock} uds</span>'
            stock_tip = f"✅ Stock disponible: {stock} unidades"

        rows += f"""
        <tr>
          <td style="color:var(--muted);font-size:0.78rem;font-variant-numeric:tabular-nums;">#{p['id']}</td>
          <td>
            <div class="has-tooltip">
              <span class="product-name">{p['name']}</span>
              <div class="tooltip">🏷️ ID: {p['id']}<br>📦 Producto: {p['name']}<br>💰 Precio: S/ {precio:.2f}<br>🗃️ Valor en stock: S/ {valor_inventario:.2f}</div>
            </div>
          </td>
          <td>
            <div class="has-tooltip">
              <span class="price">S/ {precio:.2f}</span>
              <div class="tooltip">💵 Precio de venta unitario<br>📈 Valor total en stock: S/ {valor_inventario:.2f}</div>
            </div>
          </td>
          <td>
            <div class="has-tooltip">
              {badge}
              <div class="tooltip">{stock_tip}</div>
            </div>
          </td>
          <td>
            <a href='/sell/{p['id']}' class='action-btn btn-sell'
               onclick="return registerSell({p['id']}, '{p['name']}', {precio})">▶ Vender</a>
            <a href='/edit/{p['id']}' class='action-btn btn-edit'>✏ Editar</a>
            <a href='/delete/{p['id']}' class='action-btn btn-delete'
               onclick="return confirm('¿Eliminar {p['name']}?')">✕</a>
          </td>
        </tr>"""

    if not rows:
        rows = '<tr><td colspan="5"><div class="empty-state"><div class="empty-icon">📦</div><p>No hay productos. <a href="/add" style="color:var(--blue);">Agrega el primero</a></p></div></td></tr>'

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">{CSS}<title>POS - Inventario</title>
    <script>
    function filterTable() {{
      const q = document.getElementById('search').value.toLowerCase();
      document.querySelectorAll('tbody tr').forEach(row => {{
        row.style.display = row.innerText.toLowerCase().includes(q) ? '' : 'none';
      }});
    }}
    function registerSell(id, name, price) {{
      // Muestra comprobante después de vender
      fetch('/sell/' + id).then(() => {{
        showReceipt({{ name: name, qty: 1, price: price, total: price }});
      }});
      return false;
    }}
    </script>
    </head><body>
    {nav(session['user'])}
    {modal_receipt()}
    <div class="container">
      <div class="page-header">
        <div class="page-header-left">
          <h1>📦 Inventario</h1>
          <p>Gestiona productos y registra ventas en tiempo real</p>
        </div>
        <a href='/add' class='btn-primary'>+ Agregar producto</a>
      </div>

      <div class="stats-grid">
        <div class="stat-card blue has-tooltip">
          <div class="stat-label">Productos</div>
          <div class="stat-value">{total_productos}</div>
          <div class="stat-sub">En inventario</div>
          <div class="tooltip">Total de productos registrados en el sistema</div>
        </div>
        <div class="stat-card green has-tooltip">
          <div class="stat-label">Ventas hoy</div>
          <div class="stat-value">S/ {float(ventas_hoy):.2f}</div>
          <div class="stat-sub">{num_ventas_hoy} transacciones</div>
          <div class="tooltip">📅 Ingresos del día de hoy<br>🔢 {num_ventas_hoy} ventas realizadas hoy</div>
        </div>
        <div class="stat-card {'red' if stock_bajo > 0 else 'green'} has-tooltip">
          <div class="stat-label">Stock bajo</div>
          <div class="stat-value">{stock_bajo}</div>
          <div class="stat-sub">Productos con ≤ 5 unidades</div>
          <div class="tooltip">{'⚠️ ' + str(stock_bajo) + ' productos necesitan reposición' if stock_bajo > 0 else '✅ Todo el stock está en buen nivel'}</div>
        </div>
        <div class="stat-card amber has-tooltip">
          <div class="stat-label">Total histórico</div>
          <div class="stat-value">S/ {float(total_all):.2f}</div>
          <div class="stat-sub">Todas las ventas</div>
          <div class="tooltip">💰 Suma total de todas las ventas registradas</div>
        </div>
      </div>

      <div class="table-card">
        <div class="table-header">
          <h2>Lista de productos</h2>
          <input class="search-input" id="search" type="search" placeholder="🔍 Buscar producto..." oninput="filterTable()">
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

# ================================================================
# ADD PRODUCT
# ================================================================
@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    error = ""
    if request.method == "POST":
        name = request.form["name"].strip()
        price = request.form["price"]
        stock = request.form["stock"]
        try:
            conn = get_db()
            c = conn.cursor()
            c.execute("INSERT INTO products (name, price, stock) VALUES (%s, %s, %s)",
                      (name, float(price), int(stock)))
            conn.commit()
            conn.close()
            return redirect(url_for("dashboard"))
        except Exception as e:
            error = f"Error al guardar: {str(e)}"

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">{CSS}<title>Agregar Producto</title></head><body>
    {nav(session['user'])}
    <div class="container">
      <div class="page-header">
        <div class="page-header-left"><h1>➕ Agregar producto</h1><p>Completa los datos del nuevo producto</p></div>
      </div>
      {'<div class="alert alert-error">⚠️ ' + error + '</div>' if error else ''}
      <div class="form-card">
        <form method="POST" autocomplete="off">
          <div class="form-group">
            <label>Nombre del producto</label>
            <input name="name" type="text" autocomplete="off" placeholder="Ej: Coca Cola 500ml" required>
          </div>
          <div class="form-group">
            <label>Precio (S/)</label>
            <input name="price" type="number" step="0.01" min="0" placeholder="0.00" required>
          </div>
          <div class="form-group">
            <label>Stock inicial</label>
            <input name="stock" type="number" min="0" placeholder="0" required>
          </div>
          <div style="display:flex;gap:0.75rem;margin-top:1.75rem;">
            <button class="btn-primary" type="submit">💾 Guardar producto</button>
            <a href="/dashboard" class="btn-secondary">Cancelar</a>
          </div>
        </form>
      </div>
    </div>
    </body></html>"""

# ================================================================
# SELL (redirige y el comprobante lo muestra el JS del dashboard)
# ================================================================
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
            c.execute("INSERT INTO sales (product_id, quantity, total) VALUES (%s, %s, %s)",
                      (id, 1, product["price"]))
            conn.commit()
        conn.close()
    except:
        pass
    return redirect(url_for("dashboard"))

# ================================================================
# EDIT
# ================================================================
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
            c.execute("UPDATE products SET name=%s, price=%s, stock=%s WHERE id=%s",
                      (name, float(price), int(stock), id))
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
        <div class="page-header-left"><h1>✏️ Editar producto</h1><p>Modifica los datos del producto</p></div>
      </div>
      {'<div class="alert alert-error">⚠️ ' + error + '</div>' if error else ''}
      <div class="form-card">
        <form method="POST" autocomplete="off">
          <div class="form-group">
            <label>Nombre</label>
            <input name="name" type="text" autocomplete="off" value="{p['name']}" required>
          </div>
          <div class="form-group">
            <label>Precio (S/)</label>
            <input name="price" type="number" step="0.01" min="0" value="{float(p['price']):.2f}" required>
          </div>
          <div class="form-group">
            <label>Stock</label>
            <input name="stock" type="number" min="0" value="{p['stock']}" required>
          </div>
          <div style="display:flex;gap:0.75rem;margin-top:1.75rem;">
            <button class="btn-primary" type="submit">💾 Guardar cambios</button>
            <a href="/dashboard" class="btn-secondary">Cancelar</a>
          </div>
        </form>
      </div>
    </div>
    </body></html>"""

# ================================================================
# DELETE
# ================================================================
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

# ================================================================
# VENTAS
# ================================================================
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
        SELECT s.id, p.name, s.quantity, s.total, s.created_at, p.price
        FROM sales s JOIN products p ON s.product_id = p.id
        {where} ORDER BY s.id DESC
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
        fecha_full = v["created_at"].strftime("%A %d de %B, %Y a las %H:%M") if v["created_at"] else "-"
        precio_unit = float(v["price"])
        total_v = float(v["total"])
        rows += f"""
        <tr>
          <td style="color:var(--muted);font-size:0.78rem;">#{v['id']}</td>
          <td><span class="product-name">{v['name']}</span></td>
          <td>
            <div class="has-tooltip">
              <span class="badge badge-green">{v['quantity']} uds</span>
              <div class="tooltip">Precio unitario: S/ {precio_unit:.2f}<br>Subtotal: S/ {total_v:.2f}</div>
            </div>
          </td>
          <td>
            <div class="has-tooltip">
              <span class="price">S/ {total_v:.2f}</span>
              <div class="tooltip">💵 Total cobrado: S/ {total_v:.2f}<br>📦 {v['quantity']} x S/ {precio_unit:.2f}</div>
            </div>
          </td>
          <td>
            <div class="has-tooltip">
              <span style="color:var(--muted);font-size:0.78rem;">{fecha}</span>
              <div class="tooltip">🗓️ {fecha_full}</div>
            </div>
          </td>
          <td>
            <button class="action-btn btn-receipt"
              onclick="showReceipt({{name:'{v['name']}',qty:{v['quantity']},price:{precio_unit},total:{total_v}}})">
              🧾 Comprobante
            </button>
          </td>
        </tr>"""

    if not rows:
        rows = '<tr><td colspan="6"><div class="empty-state"><div class="empty-icon">📊</div><p>No hay ventas en este período</p></div></td></tr>'

    filtro_links = ""
    for f, label in [("hoy","Hoy"), ("semana","7 días"), ("mes","Mes"), ("todo","Todo")]:
        active = "background:var(--border2);color:#fff;" if filtro == f else ""
        filtro_links += f'<a href="/ventas?filtro={f}" style="padding:6px 14px;border-radius:7px;text-decoration:none;font-size:0.78rem;font-weight:600;color:var(--muted2);transition:all 0.15s;{active}">{label}</a>'

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">{CSS}<title>POS - Ventas</title></head><body>
    {nav(session['user'])}
    {modal_receipt()}
    <div class="container">
      <div class="page-header">
        <div class="page-header-left"><h1>📊 Historial de ventas</h1><p>Revisa y emite comprobantes de todas las transacciones</p></div>
      </div>
      <div class="stats-grid">
        <div class="stat-card green has-tooltip">
          <div class="stat-label">Total — {label_filtro}</div>
          <div class="stat-value">S/ {total_general:.2f}</div>
          <div class="stat-sub">Ingresos del período</div>
          <div class="tooltip">💰 Total vendido en el período: {label_filtro}</div>
        </div>
        <div class="stat-card blue has-tooltip">
          <div class="stat-label">Transacciones</div>
          <div class="stat-value">{num_ventas}</div>
          <div class="stat-sub">{label_filtro}</div>
          <div class="tooltip">🔢 {num_ventas} ventas registradas en el período</div>
        </div>
        <div class="stat-card amber has-tooltip">
          <div class="stat-label">Ticket promedio</div>
          <div class="stat-value">S/ {(total_general/num_ventas if num_ventas > 0 else 0):.2f}</div>
          <div class="stat-sub">Por transacción</div>
          <div class="tooltip">📈 Promedio de venta por transacción</div>
        </div>
      </div>
      <div class="table-card">
        <div class="table-header">
          <h2>Ventas — {label_filtro}</h2>
          <div style="display:flex;gap:3px;background:#0a0d16;padding:4px;border-radius:10px;">
            {filtro_links}
          </div>
        </div>
        <table>
          <thead><tr>
            <th>#</th><th>Producto</th><th>Cantidad</th><th>Total</th><th>Fecha</th><th>Acción</th>
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

# ================================================================
# LOGOUT
# ================================================================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# ================================================================
# RUN
# ================================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)