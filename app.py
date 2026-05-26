from flask import Flask, request, redirect, url_for, session, jsonify
import psycopg2
import psycopg2.extras
import os
from datetime import datetime
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

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        if session.get("rol") != "admin":
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated

# ================================================================
# CSS GLOBAL
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
    --green: #10b981; --green-dim: #052e16; --green-text: #34d399;
    --amber: #f59e0b; --amber-dim: #2d1f00; --amber-text: #fbbf24;
    --red: #ef4444; --red-dim: #2d0f0f; --red-text: #f87171;
    --purple: #7c3aed; --purple-dim: #1e1040; --purple-text: #a78bfa;
    --radius: 12px; --radius-sm: 8px;
  }
  html { scroll-behavior: smooth; }
  body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; -webkit-font-smoothing: antialiased; }
  ::-webkit-scrollbar { width: 5px; } ::-webkit-scrollbar-track { background: var(--bg); } ::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }

  /* SIDEBAR */
  .sidebar { position: fixed; top: 0; left: 0; height: 100vh; width: 260px; background: var(--surface); border-right: 1px solid var(--border); transform: translateX(-260px); transition: transform 0.3s cubic-bezier(.4,0,.2,1); z-index: 200; display: flex; flex-direction: column; padding: 1.25rem 0.75rem; box-shadow: 4px 0 40px rgba(0,0,0,0.5); overflow-y: auto; }
  .sidebar.open { transform: translateX(0); }
  .sidebar-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(2px); z-index: 199; display: none; }
  .sidebar-overlay.open { display: block; }
  .sidebar-brand { display: flex; align-items: center; gap: 10px; padding: 0.25rem 0.5rem 1.25rem; border-bottom: 1px solid var(--border); margin-bottom: 0.75rem; }
  .sidebar-brand-icon { width: 36px; height: 36px; background: linear-gradient(135deg,#4f6ef7,#7c3aed); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; flex-shrink: 0; }
  .sidebar-brand-text { font-weight: 800; color: #fff; font-size: 0.9rem; }
  .sidebar-brand-sub { font-size: 0.68rem; color: var(--muted); }
  .sidebar-close { position: absolute; top: 0.9rem; right: 0.75rem; background: var(--border); border: none; color: var(--muted2); width: 26px; height: 26px; border-radius: 50%; cursor: pointer; font-size: 0.8rem; display: flex; align-items: center; justify-content: center; }
  .sidebar-section { font-size: 0.65rem; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; padding: 0.75rem 0.75rem 0.3rem; }
  .sidebar a { display: flex; align-items: center; gap: 0.65rem; padding: 0.6rem 0.75rem; color: var(--muted2); text-decoration: none; border-radius: var(--radius-sm); font-size: 0.82rem; font-weight: 500; transition: all 0.15s; margin-bottom: 1px; }
  .sidebar a:hover, .sidebar a.active { background: var(--blue-glow); color: #fff; }
  .sidebar a.danger:hover { background: var(--red-dim); color: var(--red-text); }
  .sidebar-footer { margin-top: auto; padding-top: 0.75rem; border-top: 1px solid var(--border); }

  /* NAV */
  .nav { background: var(--surface); border-bottom: 1px solid var(--border); padding: 0 1.5rem; display: flex; align-items: center; justify-content: space-between; height: 56px; position: sticky; top: 0; z-index: 100; }
  .nav-left { display: flex; align-items: center; gap: 0.875rem; }
  .hamburger { background: none; border: none; color: var(--muted2); cursor: pointer; padding: 6px; border-radius: var(--radius-sm); font-size: 1.1rem; transition: all 0.15s; display: flex; align-items: center; }
  .hamburger:hover { background: var(--border); color: #fff; }
  .nav-brand { font-size: 0.95rem; font-weight: 800; color: #fff; display: flex; align-items: center; gap: 0.5rem; }
  .nav-brand .chip { background: var(--blue); color: #fff; padding: 2px 7px; border-radius: 5px; font-size: 0.65rem; font-weight: 700; }
  .nav-links { display: flex; gap: 0.2rem; }
  .nav-links a { color: var(--muted2); text-decoration: none; padding: 5px 10px; border-radius: var(--radius-sm); font-size: 0.78rem; font-weight: 500; display: flex; align-items: center; gap: 4px; transition: all 0.15s; }
  .nav-links a:hover { background: var(--border); color: #fff; }
  .nav-links a.danger:hover { background: var(--red-dim); color: var(--red-text); }
  .nav-right { display: flex; align-items: center; gap: 8px; }
  .avatar { width: 30px; height: 30px; background: linear-gradient(135deg,var(--blue),var(--purple)); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.72rem; color: #fff; }
  .nav-username { font-size: 0.78rem; color: var(--muted2); font-weight: 500; }
  .role-chip { font-size: 0.65rem; font-weight: 700; padding: 2px 7px; border-radius: 4px; }
  .role-admin { background: rgba(79,110,247,0.15); color: #93b4ff; }
  .role-vendedor { background: rgba(16,185,129,0.15); color: var(--green-text); }

  /* LAYOUT */
  .container { max-width: 1320px; margin: 0 auto; padding: 1.5rem 2rem; }
  .page-header { margin-bottom: 1.5rem; display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 1rem; }
  .page-header-left h1 { font-size: 1.3rem; font-weight: 800; color: #fff; letter-spacing: -0.02em; }
  .page-header-left p { color: var(--muted); font-size: 0.8rem; margin-top: 3px; }

  /* STATS */
  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.875rem; margin-bottom: 1.5rem; }
  .stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.1rem 1.25rem; transition: all 0.2s; cursor: default; position: relative; overflow: hidden; }
  .stat-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; border-radius: 2px 2px 0 0; }
  .stat-card.blue::before { background: var(--blue); }
  .stat-card.green::before { background: var(--green); }
  .stat-card.amber::before { background: var(--amber); }
  .stat-card.red::before { background: var(--red); }
  .stat-card.purple::before { background: var(--purple); }
  .stat-card:hover { border-color: var(--border2); transform: translateY(-2px); }
  .stat-label { font-size: 0.68rem; color: var(--muted); font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem; }
  .stat-value { font-size: 1.55rem; font-weight: 800; letter-spacing: -0.02em; }
  .stat-sub { font-size: 0.7rem; color: var(--muted); margin-top: 4px; }
  .stat-card.blue .stat-value { color: #60a5fa; }
  .stat-card.green .stat-value { color: var(--green-text); }
  .stat-card.amber .stat-value { color: var(--amber-text); }
  .stat-card.red .stat-value { color: var(--red-text); }
  .stat-card.purple .stat-value { color: var(--purple-text); }

  /* TABLE */
  .table-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
  .table-header { padding: 0.875rem 1.5rem; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
  .table-header h2 { font-size: 0.9rem; font-weight: 700; color: #fff; }
  table { width: 100%; border-collapse: collapse; }
  th { background: #0a0d16; padding: 0.6rem 1.5rem; text-align: left; font-size: 0.65rem; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; }
  td { padding: 0.75rem 1.5rem; border-top: 1px solid var(--border); font-size: 0.83rem; vertical-align: middle; }
  tr:hover td { background: var(--surface2); }

  /* BADGES */
  .badge { display: inline-flex; align-items: center; padding: 3px 9px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; }
  .badge-green { background: var(--green-dim); color: var(--green-text); }
  .badge-amber { background: var(--amber-dim); color: var(--amber-text); }
  .badge-red { background: var(--red-dim); color: var(--red-text); }
  .badge-blue { background: rgba(79,110,247,0.15); color: #93b4ff; }
  .badge-purple { background: var(--purple-dim); color: var(--purple-text); }

  .product-name { font-weight: 600; color: var(--text); }
  .price { font-weight: 700; color: #60a5fa; font-variant-numeric: tabular-nums; }

  /* ACTION BUTTONS */
  .action-btn { display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 6px; font-size: 0.76rem; font-weight: 600; text-decoration: none; transition: all 0.15s; margin: 0 1px; border: 1px solid transparent; white-space: nowrap; cursor: pointer; background: none; }
  .btn-sell { background: rgba(16,185,129,0.1); color: var(--green-text); border-color: rgba(16,185,129,0.2); }
  .btn-sell:hover { background: var(--green); color: #fff; border-color: var(--green); }
  .btn-edit { background: rgba(79,110,247,0.1); color: #93b4ff; border-color: rgba(79,110,247,0.2); }
  .btn-edit:hover { background: var(--blue); color: #fff; }
  .btn-delete { background: rgba(239,68,68,0.08); color: var(--red-text); border-color: rgba(239,68,68,0.2); }
  .btn-delete:hover { background: var(--red); color: #fff; }
  .btn-receipt { background: rgba(245,158,11,0.1); color: var(--amber-text); border-color: rgba(245,158,11,0.2); }
  .btn-receipt:hover { background: var(--amber); color: #000; }
  .btn-stock { background: var(--purple-dim); color: var(--purple-text); border-color: rgba(124,58,237,0.2); }
  .btn-stock:hover { background: var(--purple); color: #fff; }

  /* TOOLBAR */
  .toolbar { padding: 0.75rem 1.5rem; border-bottom: 1px solid var(--border); display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap; }
  .search-input { background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 7px 13px; border-radius: var(--radius-sm); font-size: 0.83rem; width: 260px; outline: none; transition: border 0.2s; }
  .search-input:focus { border-color: var(--blue); }
  .search-input::placeholder { color: var(--muted); }

  /* BUTTONS */
  .btn-primary { background: var(--blue); color: #fff; border: none; padding: 7px 16px; border-radius: var(--radius-sm); font-size: 0.83rem; font-weight: 700; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 5px; transition: all 0.15s; }
  .btn-primary:hover { background: var(--blue2); transform: translateY(-1px); box-shadow: 0 4px 16px rgba(79,110,247,0.3); }
  .btn-secondary { background: transparent; color: var(--muted2); border: 1px solid var(--border); padding: 7px 16px; border-radius: var(--radius-sm); font-size: 0.83rem; font-weight: 500; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 5px; transition: all 0.15s; }
  .btn-secondary:hover { background: var(--border); color: #fff; }
  .btn-danger { background: var(--red-dim); color: var(--red-text); border: 1px solid rgba(239,68,68,0.2); padding: 7px 16px; border-radius: var(--radius-sm); font-size: 0.83rem; font-weight: 600; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 5px; transition: all 0.15s; }
  .btn-danger:hover { background: var(--red); color: #fff; }

  /* FORMS */
  .form-card { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 1.75rem; max-width: 500px; }
  .form-group { margin-bottom: 1.1rem; }
  label { display: block; font-size: 0.7rem; font-weight: 700; color: var(--muted2); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.06em; }
  input, select, textarea { width: 100%; background: var(--bg) !important; border: 1px solid var(--border); color: var(--text) !important; padding: 9px 13px; border-radius: var(--radius-sm); font-size: 0.88rem; outline: none; transition: border 0.2s; font-family: 'Inter', sans-serif; -webkit-text-fill-color: var(--text) !important; }
  input:-webkit-autofill, input:-webkit-autofill:hover, input:-webkit-autofill:focus { -webkit-box-shadow: 0 0 0 1000px #080b12 inset !important; -webkit-text-fill-color: #e2e8f0 !important; border: 1px solid var(--border) !important; caret-color: #e2e8f0; }
  input:focus, select:focus { border-color: var(--blue); box-shadow: 0 0 0 3px var(--blue-glow); }
  input::placeholder { color: var(--muted) !important; }
  select option { background: var(--surface2); color: var(--text); }

  /* LOGIN */
  .login-wrapper { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: var(--bg); background-image: radial-gradient(ellipse at 20% 50%, rgba(79,110,247,0.07) 0%, transparent 60%), radial-gradient(ellipse at 80% 20%, rgba(124,58,237,0.05) 0%, transparent 50%); }
  .login-card { background: var(--surface); border: 1px solid var(--border); border-radius: 24px; padding: 2.5rem; width: 400px; box-shadow: 0 25px 60px rgba(0,0,0,0.5); }
  .login-logo { text-align: center; margin-bottom: 2rem; }
  .login-logo h1 { font-size: 1.5rem; font-weight: 900; color: #fff; letter-spacing: -0.02em; }
  .login-logo p { color: var(--muted); font-size: 0.83rem; margin-top: 4px; }
  .login-logo img { max-width: 130px; border-radius: 14px; margin-bottom: 1rem; }

  /* ALERTS */
  .alert { padding: 0.7rem 1.1rem; border-radius: var(--radius-sm); margin-bottom: 1rem; font-size: 0.83rem; font-weight: 500; }
  .alert-error { background: var(--red-dim); border: 1px solid rgba(239,68,68,0.3); color: var(--red-text); }
  .alert-success { background: var(--green-dim); border: 1px solid rgba(16,185,129,0.3); color: var(--green-text); }

  /* TOTAL BAR */
  .total-bar { background: #0a0d16; padding: 0.875rem 1.5rem; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border); }
  .total-bar span { font-size: 0.78rem; color: var(--muted); }
  .total-bar strong { font-size: 1.05rem; color: var(--green-text); font-weight: 800; }

  /* EMPTY */
  .empty-state { text-align: center; padding: 3rem; color: var(--muted); }
  .empty-state .empty-icon { font-size: 2.2rem; margin-bottom: 0.75rem; opacity: 0.4; }

  /* TOOLTIP */
  .has-tooltip { position: relative; cursor: default; }
  .tooltip { position: absolute; bottom: calc(100% + 8px); left: 50%; transform: translateX(-50%); background: #1e2640; border: 1px solid var(--border2); color: var(--text); padding: 8px 12px; border-radius: 8px; font-size: 0.73rem; white-space: nowrap; opacity: 0; pointer-events: none; transition: opacity 0.2s; z-index: 50; box-shadow: 0 8px 24px rgba(0,0,0,0.4); line-height: 1.7; }
  .tooltip::after { content: ''; position: absolute; top: 100%; left: 50%; transform: translateX(-50%); border: 5px solid transparent; border-top-color: var(--border2); }
  .has-tooltip:hover .tooltip { opacity: 1; }

  /* MODAL */
  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.75); backdrop-filter: blur(4px); z-index: 300; display: none; align-items: center; justify-content: center; }
  .modal-overlay.open { display: flex; }
  .modal { background: var(--surface); border: 1px solid var(--border); border-radius: 20px; padding: 1.75rem; width: 430px; max-width: 95vw; box-shadow: 0 30px 80px rgba(0,0,0,0.5); }
  .modal h2 { font-size: 1rem; font-weight: 800; color: #fff; margin-bottom: 1.25rem; display: flex; align-items: center; gap: 8px; }
  .receipt { background: #fff; color: #111; border-radius: 10px; padding: 1.5rem; font-family: 'Courier New', monospace; font-size: 0.78rem; line-height: 1.9; }
  .receipt .r-title { text-align: center; font-size: 0.95rem; font-weight: 900; margin-bottom: 3px; }
  .receipt .r-sub { text-align: center; color: #555; font-size: 0.68rem; margin-bottom: 0.875rem; }
  .receipt .r-line { border-top: 1px dashed #bbb; margin: 0.4rem 0; }
  .receipt .r-row { display: flex; justify-content: space-between; }
  .receipt .r-total { display: flex; justify-content: space-between; font-weight: 900; font-size: 0.9rem; margin-top: 0.4rem; }
  .receipt .r-footer { text-align: center; color: #777; font-size: 0.67rem; margin-top: 0.875rem; }
  .modal-actions { display: flex; gap: 0.75rem; margin-top: 1.1rem; }

  /* GRID 2 COL */
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
  @media(max-width:768px) { .grid-2 { grid-template-columns: 1fr; } .nav-links { display: none; } }

  @media print { .no-print { display: none !important; } .receipt { box-shadow: none; } }
</style>
"""

# ================================================================
# SIDEBAR
# ================================================================
def sidebar(rol="vendedor"):
    admin_links = ""
    if rol == "admin":
        admin_links = """
        <div class="sidebar-section">Administración</div>
        <a href="/usuarios">👥 Usuarios</a>
        <a href="/stock">📥 Gestión de Stock</a>
        <a href="/stock/historial">📋 Historial de Stock</a>
        """
    return f"""
    <div class="sidebar-overlay" id="overlay" onclick="closeSidebar()"></div>
    <div class="sidebar" id="sidebar">
      <button class="sidebar-close no-print" onclick="closeSidebar()">✕</button>
      <div class="sidebar-brand">
        <div class="sidebar-brand-icon">🏪</div>
        <div><div class="sidebar-brand-text">POS Sistema</div><div class="sidebar-brand-sub">Panel de control</div></div>
      </div>
      <div class="sidebar-section">Principal</div>
      <a href="/dashboard">📦 Inventario</a>
      <a href="/ventas">📊 Ventas</a>
      <a href="/facturacion">🧾 Facturación</a>
      {admin_links}
      <div class="sidebar-footer">
        <a href="/logout" class="danger">🚪 Cerrar Sesión</a>
      </div>
    </div>
    <script>
    function openSidebar() {{ document.getElementById('sidebar').classList.add('open'); document.getElementById('overlay').classList.add('open'); }}
    function closeSidebar() {{ document.getElementById('sidebar').classList.remove('open'); document.getElementById('overlay').classList.remove('open'); }}
    </script>
    """

def nav(user, rol="vendedor"):
    initial = user[0].upper()
    chip_class = "role-admin" if rol == "admin" else "role-vendedor"
    admin_nav = ""
    if rol == "admin":
        admin_nav = "<a href='/stock'>📥 Stock</a><a href='/usuarios'>👥 Usuarios</a>"
    return f"""
    {sidebar(rol)}
    <nav class="nav no-print">
      <div class="nav-left">
        <button class="hamburger" onclick="openSidebar()">☰</button>
        <div class="nav-brand">POS <span class="chip">Sistema</span></div>
      </div>
      <div class="nav-links">
        <a href='/dashboard'>📦 Inventario</a>
        <a href='/ventas'>📊 Ventas</a>
        <a href='/facturacion'>🧾 Facturación</a>
        {admin_nav}
        <a href='/logout' class='danger'>🚪 Salir</a>
      </div>
      <div class="nav-right">
        <div class="avatar">{initial}</div>
        <span class="nav-username">{user}</span>
        <span class="role-chip {chip_class}">{rol}</span>
      </div>
    </nav>
    """

# ================================================================
# MODAL COMPROBANTE
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
      const fecha = now.toLocaleDateString('es-PE') + ' ' + now.toLocaleTimeString('es-PE',{hour:'2-digit',minute:'2-digit'});
      const num = 'B' + String(Date.now()).slice(-6);
      document.getElementById('receiptContent').innerHTML = `
        <div class="r-title">BOLETA DE VENTA</div>
        <div class="r-sub">N° ${num} | POS Sistema<br>${fecha}</div>
        <div class="r-line"></div>
        <div class="r-row"><span>Producto:</span><span>${data.name}</span></div>
        <div class="r-row"><span>Cantidad:</span><span>${data.qty} uds.</span></div>
        <div class="r-row"><span>Precio unit.:</span><span>S/ ${parseFloat(data.price).toFixed(2)}</span></div>
        <div class="r-line"></div>
        <div class="r-total"><span>TOTAL A PAGAR:</span><span>S/ ${parseFloat(data.total).toFixed(2)}</span></div>
        <div class="r-line"></div>
        <div class="r-footer">✓ Gracias por su compra<br>Conserve este comprobante</div>
      `;
      document.getElementById('receiptModal').classList.add('open');
    }
    function closeReceipt() { document.getElementById('receiptModal').classList.remove('open'); }
    function printReceipt() {
      const content = document.getElementById('receiptContent').innerHTML;
      const win = window.open('','_blank','width=380,height=520');
      win.document.write('<html><head><title>Comprobante</title><style>body{font-family:Courier New,monospace;padding:20px;font-size:12px;line-height:1.9}.r-title{text-align:center;font-size:15px;font-weight:900;margin-bottom:3px}.r-sub{text-align:center;color:#555;font-size:10px;margin-bottom:10px}.r-line{border-top:1px dashed #bbb;margin:5px 0}.r-row,.r-total{display:flex;justify-content:space-between}.r-total{font-weight:900;font-size:14px;margin-top:5px}.r-footer{text-align:center;color:#777;font-size:10px;margin-top:10px}</style></head><body>'+content+'</body></html>');
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
            c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            c.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            user = c.fetchone()
            conn.close()
            if user:
                session["user"] = username
                session["rol"] = user["rol"] if user["rol"] else "vendedor"
                return redirect(url_for("dashboard"))
            error = "Usuario o contraseña incorrectos"
        except Exception as e:
            error = f"Error: {str(e)}"
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
          <button class="btn-primary" type="submit" style="width:100%;justify-content:center;padding:11px;font-size:0.9rem;margin-top:0.5rem;">
            Iniciar sesión →
          </button>
        </form>
      </div>
    </div></body></html>"""

# ================================================================
# DASHBOARD
# ================================================================
@app.route("/dashboard")
@login_required
def dashboard():
    rol = session.get("rol", "vendedor")
    conn = get_db()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    c.execute("SELECT * FROM products ORDER BY name ASC")
    products = c.fetchall()
    c.execute("SELECT COUNT(*) FROM products")
    total_productos = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM products WHERE stock <= 5")
    stock_bajo = c.fetchone()[0]
    c.execute("SELECT COALESCE(SUM(total),0) FROM sales WHERE DATE(created_at)=CURRENT_DATE")
    ventas_hoy = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM sales WHERE DATE(created_at)=CURRENT_DATE")
    num_ventas_hoy = c.fetchone()[0]
    c.execute("SELECT COALESCE(SUM(total),0) FROM sales")
    total_all = c.fetchone()[0]
    conn.close()

    rows = ""
    for p in products:
        stock = p["stock"]
        precio = float(p["price"])
        valor_inv = precio * stock
        if stock <= 0:
            badge = '<span class="badge badge-red">Sin stock</span>'
            tip = "❌ Sin unidades disponibles"
        elif stock <= 5:
            badge = f'<span class="badge badge-amber">{stock} uds</span>'
            tip = f"⚠️ Stock bajo: solo {stock} unidades"
        else:
            badge = f'<span class="badge badge-green">{stock} uds</span>'
            tip = f"✅ {stock} unidades disponibles"

        pid = p['id']; pname = p['name']
        acciones = f'<a href="/sell/{pid}" class="action-btn btn-sell" onclick="return doSell({pid}, \'{pname}\', {precio})">▶ Vender</a>'
        if rol == "admin":
            acciones += f'<a href="/edit/{pid}" class="action-btn btn-edit">✏ Editar</a>'
            acciones += f'<a href="/stock/add/{pid}" class="action-btn btn-stock">📥 Stock</a>'
            acciones += f'<a href="/delete/{pid}" class="action-btn btn-delete" onclick="return confirm(\'¿Eliminar {pname}?\')">✕</a>'

        rows += f"""<tr>
          <td style="color:var(--muted);font-size:0.76rem;">#{p['id']}</td>
          <td><div class="has-tooltip"><span class="product-name">{p['name']}</span><div class="tooltip">🏷️ {p['name']}<br>💰 Precio: S/ {precio:.2f}<br>🗃️ Valor en stock: S/ {valor_inv:.2f}</div></div></td>
          <td><div class="has-tooltip"><span class="price">S/ {precio:.2f}</span><div class="tooltip">💵 Precio unitario de venta<br>📦 Stock total: S/ {valor_inv:.2f}</div></div></td>
          <td><div class="has-tooltip">{badge}<div class="tooltip">{tip}</div></div></td>
          <td>{acciones}</td></tr>"""

    if not rows:
        rows = '<tr><td colspan="5"><div class="empty-state"><div class="empty-icon">📦</div><p>No hay productos. <a href="/add" style="color:var(--blue);">Agrega el primero</a></p></div></td></tr>'

    add_btn = '<a href="/add" class="btn-primary">+ Agregar producto</a>' if rol == "admin" else ""

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">{CSS}<title>POS - Inventario</title>
    <script>
    function filterTable() {{ const q=document.getElementById('search').value.toLowerCase(); document.querySelectorAll('tbody tr').forEach(r=>r.style.display=r.innerText.toLowerCase().includes(q)?'':'none'); }}
    function doSell(id, name, price) {{
      fetch('/sell/'+id).then(()=>showReceipt({{name:name,qty:1,price:price,total:price}}));
      return false;
    }}
    </script></head><body>
    {nav(session['user'], rol)}
    {modal_receipt()}
    <div class="container">
      <div class="page-header">
        <div class="page-header-left"><h1>📦 Inventario</h1><p>Productos disponibles para venta</p></div>
        {add_btn}
      </div>
      <div class="stats-grid">
        <div class="stat-card blue has-tooltip"><div class="stat-label">Productos</div><div class="stat-value">{total_productos}</div><div class="stat-sub">En inventario</div><div class="tooltip">Total de SKUs registrados</div></div>
        <div class="stat-card green has-tooltip"><div class="stat-label">Ventas hoy</div><div class="stat-value">S/ {float(ventas_hoy):.2f}</div><div class="stat-sub">{num_ventas_hoy} transacciones</div><div class="tooltip">💰 Ingresos del día de hoy<br>🔢 {num_ventas_hoy} ventas realizadas</div></div>
        <div class="stat-card {'red' if stock_bajo>0 else 'green'} has-tooltip"><div class="stat-label">Stock bajo</div><div class="stat-value">{stock_bajo}</div><div class="stat-sub">Productos ≤ 5 unidades</div><div class="tooltip">{'⚠️ Requieren reposición' if stock_bajo>0 else '✅ Stock en buen nivel'}</div></div>
        <div class="stat-card amber has-tooltip"><div class="stat-label">Total histórico</div><div class="stat-value">S/ {float(total_all):.2f}</div><div class="stat-sub">Todas las ventas</div><div class="tooltip">💰 Suma total acumulada de ventas</div></div>
      </div>
      <div class="table-card">
        <div class="table-header"><h2>Productos</h2>
          <input class="search-input" id="search" type="search" placeholder="🔍 Buscar..." oninput="filterTable()">
        </div>
        <table><thead><tr><th>ID</th><th>Producto</th><th>Precio</th><th>Stock</th><th>Acciones</th></tr></thead>
        <tbody>{rows}</tbody></table>
      </div>
    </div></body></html>"""

# ================================================================
# ADD PRODUCT (solo admin)
# ================================================================
@app.route("/add", methods=["GET", "POST"])
@admin_required
def add():
    error = ""
    if request.method == "POST":
        name = request.form["name"].strip()
        price = request.form["price"]
        stock = request.form["stock"]
        try:
            conn = get_db()
            c = conn.cursor()
            c.execute("INSERT INTO products (name, price, stock) VALUES (%s,%s,%s)", (name, float(price), int(stock)))
            conn.commit()
            # registrar en historial de stock
            c.execute("INSERT INTO stock_history (product_id, cantidad, tipo, nota, usuario) VALUES ((SELECT id FROM products WHERE name=%s ORDER BY id DESC LIMIT 1), %s, 'entrada', 'Stock inicial', %s)",
                      (name, int(stock), session['user']))
            conn.commit()
            conn.close()
            return redirect(url_for("dashboard"))
        except Exception as e:
            error = f"Error: {str(e)}"

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">{CSS}<title>Agregar Producto</title></head><body>
    {nav(session['user'], session.get('rol','vendedor'))}
    <div class="container">
      <div class="page-header"><div class="page-header-left"><h1>➕ Agregar producto</h1><p>Nuevo producto al inventario</p></div></div>
      {'<div class="alert alert-error">⚠️ ' + error + '</div>' if error else ''}
      <div class="form-card">
        <form method="POST" autocomplete="off">
          <div class="form-group"><label>Nombre del producto</label><input name="name" type="text" autocomplete="off" placeholder="Ej: Coca Cola 500ml" required></div>
          <div class="grid-2">
            <div class="form-group"><label>Precio (S/)</label><input name="price" type="number" step="0.01" min="0" placeholder="0.00" required></div>
            <div class="form-group"><label>Stock inicial</label><input name="stock" type="number" min="0" placeholder="0" required></div>
          </div>
          <div style="display:flex;gap:0.75rem;margin-top:1.5rem;">
            <button class="btn-primary" type="submit">💾 Guardar</button>
            <a href="/dashboard" class="btn-secondary">Cancelar</a>
          </div>
        </form>
      </div>
    </div></body></html>"""

# ================================================================
# SELL
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
            c.execute("UPDATE products SET stock=%s WHERE id=%s", (product["stock"]-1, id))
            c.execute("INSERT INTO sales (product_id, quantity, total) VALUES (%s,%s,%s)", (id, 1, product["price"]))
            conn.commit()
        conn.close()
    except: pass
    return redirect(url_for("dashboard"))

# ================================================================
# EDIT (solo admin)
# ================================================================
@app.route("/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit(id):
    conn = get_db()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    error = ""
    if request.method == "POST":
        name = request.form["name"].strip()
        price = request.form["price"]
        stock = request.form["stock"]
        try:
            c.execute("UPDATE products SET name=%s, price=%s, stock=%s WHERE id=%s", (name, float(price), int(stock), id))
            conn.commit()
            conn.close()
            return redirect(url_for("dashboard"))
        except Exception as e:
            error = f"Error: {str(e)}"
    c.execute("SELECT * FROM products WHERE id=%s", (id,))
    p = c.fetchone()
    conn.close()
    if not p: return redirect(url_for("dashboard"))
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">{CSS}<title>Editar</title></head><body>
    {nav(session['user'], session.get('rol','vendedor'))}
    <div class="container">
      <div class="page-header"><div class="page-header-left"><h1>✏️ Editar producto</h1></div></div>
      {'<div class="alert alert-error">⚠️ ' + error + '</div>' if error else ''}
      <div class="form-card">
        <form method="POST" autocomplete="off">
          <div class="form-group"><label>Nombre</label><input name="name" type="text" autocomplete="off" value="{p['name']}" required></div>
          <div class="grid-2">
            <div class="form-group"><label>Precio (S/)</label><input name="price" type="number" step="0.01" min="0" value="{float(p['price']):.2f}" required></div>
            <div class="form-group"><label>Stock</label><input name="stock" type="number" min="0" value="{p['stock']}" required></div>
          </div>
          <div style="display:flex;gap:0.75rem;margin-top:1.5rem;">
            <button class="btn-primary" type="submit">💾 Guardar cambios</button>
            <a href="/dashboard" class="btn-secondary">Cancelar</a>
          </div>
        </form>
      </div>
    </div></body></html>"""

# ================================================================
# DELETE (solo admin)
# ================================================================
@app.route("/delete/<int:id>")
@admin_required
def delete(id):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("DELETE FROM products WHERE id=%s", (id,))
        conn.commit()
        conn.close()
    except: pass
    return redirect(url_for("dashboard"))

# ================================================================
# STOCK - AGREGAR (solo admin)
# ================================================================
@app.route("/stock")
@admin_required
def stock():
    conn = get_db()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    c.execute("SELECT * FROM products ORDER BY name ASC")
    products = c.fetchall()
    conn.close()
    rows = ""
    for p in products:
        stock_v = p["stock"]
        if stock_v <= 0:
            badge = '<span class="badge badge-red">Sin stock</span>'
        elif stock_v <= 5:
            badge = f'<span class="badge badge-amber">{stock_v} uds</span>'
        else:
            badge = f'<span class="badge badge-green">{stock_v} uds</span>'
        rows += f"""<tr>
          <td><span class="product-name">{p['name']}</span></td>
          <td><span class="price">S/ {float(p['price']):.2f}</span></td>
          <td>{badge}</td>
          <td><a href="/stock/add/{p['id']}" class="action-btn btn-stock">📥 Agregar stock</a>
              <a href="/edit/{p['id']}" class="action-btn btn-edit">✏ Editar</a></td></tr>"""
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">{CSS}<title>Gestión de Stock</title></head><body>
    {nav(session['user'], 'admin')}
    <div class="container">
      <div class="page-header">
        <div class="page-header-left"><h1>📥 Gestión de Stock</h1><p>Agrega unidades a tus productos</p></div>
        <div style="display:flex;gap:0.75rem;">
          <a href="/stock/historial" class="btn-secondary">📋 Ver historial</a>
          <a href="/add" class="btn-primary">+ Nuevo producto</a>
        </div>
      </div>
      <div class="table-card">
        <div class="table-header"><h2>Productos</h2></div>
        <table><thead><tr><th>Producto</th><th>Precio</th><th>Stock actual</th><th>Acción</th></tr></thead>
        <tbody>{rows}</tbody></table>
      </div>
    </div></body></html>"""

@app.route("/stock/add/<int:id>", methods=["GET", "POST"])
@admin_required
def stock_add(id):
    conn = get_db()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    error = ""
    msg = ""
    if request.method == "POST":
        cantidad = int(request.form["cantidad"])
        tipo = request.form["tipo"]
        nota = request.form.get("nota", "").strip()
        try:
            c.execute("SELECT * FROM products WHERE id=%s", (id,))
            p = c.fetchone()
            if tipo == "entrada":
                nuevo = p["stock"] + cantidad
            else:
                nuevo = max(0, p["stock"] - cantidad)
            c.execute("UPDATE products SET stock=%s WHERE id=%s", (nuevo, id))
            c.execute("INSERT INTO stock_history (product_id, cantidad, tipo, nota, usuario) VALUES (%s,%s,%s,%s,%s)",
                      (id, cantidad, tipo, nota, session["user"]))
            conn.commit()
            msg = f"✅ Stock actualizado correctamente. Nuevo stock: {nuevo} uds."
        except Exception as e:
            error = f"Error: {str(e)}"
    c.execute("SELECT * FROM products WHERE id=%s", (id,))
    p = c.fetchone()
    conn.close()
    if not p: return redirect(url_for("stock"))
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">{CSS}<title>Agregar Stock</title></head><body>
    {nav(session['user'], 'admin')}
    <div class="container">
      <div class="page-header"><div class="page-header-left"><h1>📥 Actualizar Stock</h1><p>Producto: <strong>{p['name']}</strong> — Stock actual: {p['stock']} uds.</p></div></div>
      {'<div class="alert alert-error">⚠️ ' + error + '</div>' if error else ''}
      {'<div class="alert alert-success">' + msg + '</div>' if msg else ''}
      <div class="form-card">
        <form method="POST" autocomplete="off">
          <div class="form-group"><label>Tipo de movimiento</label>
            <select name="tipo">
              <option value="entrada">📥 Entrada (agregar stock)</option>
              <option value="salida">📤 Salida (retirar stock)</option>
            </select>
          </div>
          <div class="form-group"><label>Cantidad</label><input name="cantidad" type="number" min="1" placeholder="0" required></div>
          <div class="form-group"><label>Nota / Motivo (opcional)</label><input name="nota" type="text" autocomplete="off" placeholder="Ej: Compra a proveedor, ajuste de inventario..."></div>
          <div style="display:flex;gap:0.75rem;margin-top:1.5rem;">
            <button class="btn-primary" type="submit">💾 Actualizar stock</button>
            <a href="/stock" class="btn-secondary">Cancelar</a>
          </div>
        </form>
      </div>
    </div></body></html>"""

# ================================================================
# HISTORIAL DE STOCK (solo admin)
# ================================================================
@app.route("/stock/historial")
@admin_required
def stock_historial():
    conn = get_db()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    c.execute("""
        SELECT sh.id, p.name, sh.cantidad, sh.tipo, sh.nota, sh.usuario, sh.created_at
        FROM stock_history sh JOIN products p ON sh.product_id = p.id
        ORDER BY sh.id DESC LIMIT 100
    """)
    historial = c.fetchall()
    conn.close()
    rows = ""
    for h in historial:
        fecha = h["created_at"].strftime("%d/%m/%Y %H:%M") if h["created_at"] else "-"
        tipo_badge = '<span class="badge badge-green">📥 Entrada</span>' if h["tipo"] == "entrada" else '<span class="badge badge-red">📤 Salida</span>'
        rows += f"""<tr>
          <td style="color:var(--muted);font-size:0.76rem;">#{h['id']}</td>
          <td><span class="product-name">{h['name']}</span></td>
          <td>{tipo_badge}</td>
          <td><strong style="color:{'var(--green-text)' if h['tipo']=='entrada' else 'var(--red-text)'}">{'+'if h['tipo']=='entrada' else '-'}{h['cantidad']} uds</strong></td>
          <td style="color:var(--muted2);font-size:0.8rem;">{h['nota'] or '—'}</td>
          <td><span class="badge badge-blue">{h['usuario']}</span></td>
          <td style="color:var(--muted);font-size:0.76rem;">{fecha}</td></tr>"""
    if not rows:
        rows = '<tr><td colspan="7"><div class="empty-state"><div class="empty-icon">📋</div><p>No hay movimientos registrados</p></div></td></tr>'
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">{CSS}<title>Historial de Stock</title></head><body>
    {nav(session['user'], 'admin')}
    <div class="container">
      <div class="page-header">
        <div class="page-header-left"><h1>📋 Historial de Stock</h1><p>Todos los movimientos de inventario</p></div>
        <a href="/stock" class="btn-secondary">← Volver a Stock</a>
      </div>
      <div class="table-card">
        <div class="table-header"><h2>Movimientos</h2></div>
        <table><thead><tr><th>#</th><th>Producto</th><th>Tipo</th><th>Cantidad</th><th>Nota</th><th>Usuario</th><th>Fecha</th></tr></thead>
        <tbody>{rows}</tbody></table>
      </div>
    </div></body></html>"""

# ================================================================
# FACTURACIÓN
# ================================================================
@app.route("/facturacion")
@login_required
def facturacion():
    rol = session.get("rol", "vendedor")
    conn = get_db()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    c.execute("SELECT * FROM products WHERE stock > 0 ORDER BY name ASC")
    products = c.fetchall()
    conn.close()

    product_options = "".join([f'<option value="{p["id"]}" data-price="{float(p["price"])}" data-stock="{p["stock"]}">{p["name"]} — S/ {float(p["price"]):.2f} ({p["stock"]} uds)</option>' for p in products])

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">{CSS}<title>Facturación</title>
    <style>
    .fact-card {{ background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.5rem; }}
    .fact-items {{ margin:1rem 0; }}
    .fact-item {{ display:flex;align-items:center;gap:0.75rem;padding:0.6rem 0;border-bottom:1px solid var(--border); }}
    .fact-item:last-child {{ border-bottom:none; }}
    .fact-total {{ background:#0a0d16;border-radius:var(--radius-sm);padding:1rem 1.25rem;margin-top:1rem;display:flex;justify-content:space-between;align-items:center; }}
    </style>
    <script>
    let items = [];
    function addItem() {{
      const sel = document.getElementById('prod_select');
      const opt = sel.options[sel.selectedIndex];
      const id = parseInt(sel.value);
      const name = opt.text.split(' — ')[0];
      const price = parseFloat(opt.getAttribute('data-price'));
      const stock = parseInt(opt.getAttribute('data-stock'));
      const qty = parseInt(document.getElementById('prod_qty').value) || 1;
      if (!id) return;
      if (qty > stock) {{ alert('Stock insuficiente. Disponible: ' + stock); return; }}
      const existing = items.find(i => i.id === id);
      if (existing) {{ existing.qty += qty; existing.total = existing.price * existing.qty; }}
      else {{ items.push({{id, name, price, qty, total: price*qty}}); }}
      renderItems();
    }}
    function removeItem(id) {{ items = items.filter(i => i.id !== id); renderItems(); }}
    function renderItems() {{
      const container = document.getElementById('items_list');
      if (items.length === 0) {{ container.innerHTML = '<p style="color:var(--muted);text-align:center;padding:1rem;">Sin productos agregados</p>'; document.getElementById('total_display').innerText = 'S/ 0.00'; return; }}
      let html = ''; let total = 0;
      items.forEach(i => {{
        total += i.total;
        html += `<div class="fact-item">
          <div style="flex:1"><strong>${{i.name}}</strong><br><span style="font-size:0.75rem;color:var(--muted)">${{i.qty}} x S/ ${{i.price.toFixed(2)}}</span></div>
          <span class="price">S/ ${{i.total.toFixed(2)}}</span>
          <button onclick="removeItem(${{i.id}})" class="action-btn btn-delete">✕</button>
        </div>`;
      }});
      container.innerHTML = html;
      document.getElementById('total_display').innerText = 'S/ ' + total.toFixed(2);
    }}
    function procesarVenta() {{
      if (items.length === 0) {{ alert('Agrega al menos un producto'); return; }}
      const total = items.reduce((s,i) => s+i.total, 0);
      fetch('/facturacion/procesar', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{items}})
      }}).then(r=>r.json()).then(data => {{
        if (data.ok) {{
          const now = new Date();
          const fecha = now.toLocaleDateString('es-PE') + ' ' + now.toLocaleTimeString('es-PE',{{hour:'2-digit',minute:'2-digit'}});
          const num = 'B' + String(Date.now()).slice(-6);
          let detalle = items.map(i => `<div class="r-row"><span>${{i.name}} x${{i.qty}}</span><span>S/ ${{i.total.toFixed(2)}}</span></div>`).join('');
          document.getElementById('receiptContent').innerHTML = `
            <div class="r-title">BOLETA DE VENTA</div>
            <div class="r-sub">N° ${{num}} | POS Sistema<br>${{fecha}}</div>
            <div class="r-line"></div>
            ${{detalle}}
            <div class="r-line"></div>
            <div class="r-total"><span>TOTAL:</span><span>S/ ${{total.toFixed(2)}}</span></div>
            <div class="r-line"></div>
            <div class="r-footer">✓ Gracias por su compra</div>`;
          document.getElementById('receiptModal').classList.add('open');
          items = []; renderItems();
        }} else {{ alert('Error: ' + data.error); }}
      }});
    }}
    </script>
    </head><body>
    {nav(session['user'], rol)}
    {modal_receipt()}
    <div class="container">
      <div class="page-header">
        <div class="page-header-left"><h1>🧾 Facturación</h1><p>Crea ventas con múltiples productos y genera boleta</p></div>
      </div>
      <div class="grid-2" style="gap:1.5rem;align-items:start;">
        <div class="fact-card">
          <h2 style="font-size:0.95rem;font-weight:700;margin-bottom:1rem;color:#fff;">Agregar productos</h2>
          <div class="form-group"><label>Producto</label>
            <select id="prod_select"><option value="">— Selecciona un producto —</option>{product_options}</select>
          </div>
          <div class="form-group"><label>Cantidad</label>
            <input id="prod_qty" type="number" min="1" value="1" placeholder="1">
          </div>
          <button class="btn-primary" onclick="addItem()" style="width:100%;justify-content:center;">+ Agregar</button>
        </div>
        <div class="fact-card">
          <h2 style="font-size:0.95rem;font-weight:700;margin-bottom:0.5rem;color:#fff;">Resumen de venta</h2>
          <div class="fact-items" id="items_list">
            <p style="color:var(--muted);text-align:center;padding:1rem;">Sin productos agregados</p>
          </div>
          <div class="fact-total">
            <span style="color:var(--muted);font-size:0.85rem;">Total a cobrar</span>
            <strong id="total_display" style="font-size:1.3rem;color:var(--green-text);font-weight:800;">S/ 0.00</strong>
          </div>
          <button class="btn-primary" onclick="procesarVenta()" style="width:100%;justify-content:center;margin-top:1rem;padding:12px;">
            💰 Procesar venta y emitir boleta
          </button>
        </div>
      </div>
    </div></body></html>"""

@app.route("/facturacion/procesar", methods=["POST"])
@login_required
def facturacion_procesar():
    data = request.get_json()
    items = data.get("items", [])
    try:
        conn = get_db()
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        for item in items:
            c.execute("SELECT * FROM products WHERE id=%s", (item["id"],))
            p = c.fetchone()
            if p and p["stock"] >= item["qty"]:
                c.execute("UPDATE products SET stock=%s WHERE id=%s", (p["stock"]-item["qty"], item["id"]))
                c.execute("INSERT INTO sales (product_id, quantity, total) VALUES (%s,%s,%s)", (item["id"], item["qty"], item["total"]))
        conn.commit()
        conn.close()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

# ================================================================
# VENTAS
# ================================================================
@app.route("/ventas")
@login_required
def ventas():
    rol = session.get("rol", "vendedor")
    conn = get_db()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    filtro = request.args.get("filtro", "hoy")
    if filtro == "hoy":
        where = "WHERE DATE(s.created_at)=CURRENT_DATE"; label_filtro = "Hoy"
    elif filtro == "semana":
        where = "WHERE s.created_at>=CURRENT_DATE-INTERVAL '7 days'"; label_filtro = "Últimos 7 días"
    elif filtro == "mes":
        where = "WHERE DATE_TRUNC('month',s.created_at)=DATE_TRUNC('month',CURRENT_DATE)"; label_filtro = "Este mes"
    else:
        where = ""; label_filtro = "Todo el historial"
    c.execute(f"SELECT s.id, p.name, s.quantity, s.total, s.created_at, p.price FROM sales s JOIN products p ON s.product_id=p.id {where} ORDER BY s.id DESC")
    ventas_list = c.fetchall()
    c.execute(f"SELECT COALESCE(SUM(s.total),0) FROM sales s {where}")
    total_general = float(c.fetchone()[0])
    c.execute(f"SELECT COUNT(*) FROM sales s {where}")
    num_ventas = c.fetchone()[0]
    conn.close()
    rows = ""
    for v in ventas_list:
        fecha = v["created_at"].strftime("%d/%m/%Y %H:%M") if v["created_at"] else "-"
        fecha_full = v["created_at"].strftime("%A %d de %B, %Y — %H:%M") if v["created_at"] else "-"
        precio_unit = float(v["price"]); total_v = float(v["total"])
        rows += f"""<tr>
          <td style="color:var(--muted);font-size:0.76rem;">#{v['id']}</td>
          <td><span class="product-name">{v['name']}</span></td>
          <td><div class="has-tooltip"><span class="badge badge-green">{v['quantity']} uds</span><div class="tooltip">Precio unit.: S/ {precio_unit:.2f}</div></div></td>
          <td><span class="price">S/ {total_v:.2f}</span></td>
          <td><div class="has-tooltip"><span style="color:var(--muted);font-size:0.76rem;">{fecha}</span><div class="tooltip">🗓️ {fecha_full}</div></div></td>
          <td><button class="action-btn btn-receipt" onclick="showReceipt({{name:'{v['name']}',qty:{v['quantity']},price:{precio_unit},total:{total_v}}})">🧾 Boleta</button></td></tr>"""
    if not rows:
        rows = '<tr><td colspan="6"><div class="empty-state"><div class="empty-icon">📊</div><p>No hay ventas en este período</p></div></td></tr>'
    filtro_links = ""
    for f, label in [("hoy","Hoy"),("semana","7 días"),("mes","Mes"),("todo","Todo")]:
        active = "background:var(--border2);color:#fff;" if filtro==f else ""
        filtro_links += f'<a href="/ventas?filtro={f}" style="padding:5px 12px;border-radius:7px;text-decoration:none;font-size:0.76rem;font-weight:600;color:var(--muted2);{active}">{label}</a>'
    prom = total_general/num_ventas if num_ventas > 0 else 0
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">{CSS}<title>Ventas</title></head><body>
    {nav(session['user'], rol)}
    {modal_receipt()}
    <div class="container">
      <div class="page-header"><div class="page-header-left"><h1>📊 Historial de ventas</h1><p>Revisa y emite boletas de todas las transacciones</p></div></div>
      <div class="stats-grid">
        <div class="stat-card green"><div class="stat-label">Total — {label_filtro}</div><div class="stat-value">S/ {total_general:.2f}</div><div class="stat-sub">Ingresos del período</div></div>
        <div class="stat-card blue"><div class="stat-label">Transacciones</div><div class="stat-value">{num_ventas}</div><div class="stat-sub">{label_filtro}</div></div>
        <div class="stat-card amber"><div class="stat-label">Ticket promedio</div><div class="stat-value">S/ {prom:.2f}</div><div class="stat-sub">Por transacción</div></div>
      </div>
      <div class="table-card">
        <div class="table-header"><h2>Ventas — {label_filtro}</h2>
          <div style="display:flex;gap:3px;background:#0a0d16;padding:4px;border-radius:10px;">{filtro_links}</div>
        </div>
        <table><thead><tr><th>#</th><th>Producto</th><th>Cantidad</th><th>Total</th><th>Fecha</th><th>Acción</th></tr></thead>
        <tbody>{rows}</tbody></table>
        <div class="total-bar"><span>{num_ventas} ventas registradas</span><strong>Total: S/ {total_general:.2f}</strong></div>
      </div>
    </div></body></html>"""

# ================================================================
# USUARIOS (solo admin)
# ================================================================
@app.route("/usuarios")
@admin_required
def usuarios():
    conn = get_db()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    c.execute("SELECT id, username, rol FROM users ORDER BY id ASC")
    users = c.fetchall()
    conn.close()
    rows = ""
    for u in users:
        rol_badge = f'<span class="badge badge-blue">{u["rol"]}</span>' if u["rol"]=="admin" else f'<span class="badge badge-green">{u["rol"]}</span>'
        rows += f"""<tr>
          <td style="color:var(--muted);">#{u['id']}</td>
          <td><div style="display:flex;align-items:center;gap:8px;"><div class="avatar" style="width:26px;height:26px;font-size:0.65rem;">{u['username'][0].upper()}</div><span class="product-name">{u['username']}</span></div></td>
          <td>{rol_badge}</td>
          <td>
            <a href="/usuarios/edit/{u['id']}" class="action-btn btn-edit">✏ Editar</a>
            {"" if u['username']=='admin' else f'<a href="/usuarios/delete/{u[\'id\']}" class="action-btn btn-delete" onclick="return confirm(\'¿Eliminar usuario?\')">✕ Eliminar</a>'}
          </td></tr>"""
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">{CSS}<title>Usuarios</title></head><body>
    {nav(session['user'], 'admin')}
    <div class="container">
      <div class="page-header">
        <div class="page-header-left"><h1>👥 Usuarios</h1><p>Gestiona los accesos al sistema</p></div>
        <a href="/usuarios/add" class="btn-primary">+ Nuevo usuario</a>
      </div>
      <div class="table-card">
        <div class="table-header"><h2>Lista de usuarios</h2></div>
        <table><thead><tr><th>#</th><th>Usuario</th><th>Rol</th><th>Acciones</th></tr></thead>
        <tbody>{rows}</tbody></table>
      </div>
    </div></body></html>"""

@app.route("/usuarios/add", methods=["GET", "POST"])
@admin_required
def usuarios_add():
    error = ""
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        rol = request.form["rol"]
        try:
            conn = get_db()
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password, rol) VALUES (%s,%s,%s)", (username, password, rol))
            conn.commit()
            conn.close()
            return redirect(url_for("usuarios"))
        except Exception as e:
            error = f"Error: {str(e)}"
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">{CSS}<title>Nuevo Usuario</title></head><body>
    {nav(session['user'], 'admin')}
    <div class="container">
      <div class="page-header"><div class="page-header-left"><h1>➕ Nuevo usuario</h1><p>Crea un nuevo acceso al sistema</p></div></div>
      {'<div class="alert alert-error">⚠️ ' + error + '</div>' if error else ''}
      <div class="form-card">
        <form method="POST" autocomplete="off">
          <div class="form-group"><label>Nombre de usuario</label><input name="username" type="text" autocomplete="off" placeholder="Ej: cajero1" required></div>
          <div class="form-group"><label>Contraseña</label><input name="password" type="password" autocomplete="new-password" placeholder="••••••••" required></div>
          <div class="form-group"><label>Rol</label>
            <select name="rol">
              <option value="vendedor">🟢 Vendedor — solo vende</option>
              <option value="admin">🔵 Administrador — acceso total</option>
            </select>
          </div>
          <div style="display:flex;gap:0.75rem;margin-top:1.5rem;">
            <button class="btn-primary" type="submit">💾 Crear usuario</button>
            <a href="/usuarios" class="btn-secondary">Cancelar</a>
          </div>
        </form>
      </div>
    </div></body></html>"""

@app.route("/usuarios/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def usuarios_edit(id):
    conn = get_db()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    error = ""
    if request.method == "POST":
        password = request.form["password"]
        rol = request.form["rol"]
        try:
            c.execute("UPDATE users SET password=%s, rol=%s WHERE id=%s", (password, rol, id))
            conn.commit()
            conn.close()
            return redirect(url_for("usuarios"))
        except Exception as e:
            error = f"Error: {str(e)}"
    c.execute("SELECT * FROM users WHERE id=%s", (id,))
    u = c.fetchone()
    conn.close()
    if not u: return redirect(url_for("usuarios"))
    sel_v = 'selected' if u["rol"]=="vendedor" else ""
    sel_a = 'selected' if u["rol"]=="admin" else ""
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">{CSS}<title>Editar Usuario</title></head><body>
    {nav(session['user'], 'admin')}
    <div class="container">
      <div class="page-header"><div class="page-header-left"><h1>✏️ Editar usuario: {u['username']}</h1></div></div>
      {'<div class="alert alert-error">⚠️ ' + error + '</div>' if error else ''}
      <div class="form-card">
        <form method="POST" autocomplete="off">
          <div class="form-group"><label>Nueva contraseña</label><input name="password" type="password" autocomplete="new-password" placeholder="Nueva contraseña" required></div>
          <div class="form-group"><label>Rol</label>
            <select name="rol">
              <option value="vendedor" {sel_v}>🟢 Vendedor</option>
              <option value="admin" {sel_a}>🔵 Administrador</option>
            </select>
          </div>
          <div style="display:flex;gap:0.75rem;margin-top:1.5rem;">
            <button class="btn-primary" type="submit">💾 Guardar</button>
            <a href="/usuarios" class="btn-secondary">Cancelar</a>
          </div>
        </form>
      </div>
    </div></body></html>"""

@app.route("/usuarios/delete/<int:id>")
@admin_required
def usuarios_delete(id):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE id=%s", (id,))
        conn.commit()
        conn.close()
    except: pass
    return redirect(url_for("usuarios"))

# ================================================================
# LOGOUT
# ================================================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ================================================================
# RUN
# ================================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)