"""
app.py -- Servidor Flask del sistema E-Commerce POO
Tinoco Acosta T00068324 - Pajaro Garcia T00068185

Para correr localmente:
    pip install flask gunicorn
    python ecommerce/app.py

Para Render.com el Procfile y render.yaml en la raiz del repo se encargan del arranque.
"""

import sys, os, uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, request, send_from_directory
from servicios.tienda_service import TiendaService
from servicios.producto_factory import ProductoFactory
from utils.excepciones import TiendaError, ClienteExistenteError

app = Flask(__name__, static_folder="static")
tienda = TiendaService()

ADMIN_PASS = os.environ.get("ADMIN_PASS", "admin1234")

DEMO_PRODS = [
    {"id":"PROD-001","nombre":"Teclado Mecanico RGB","precio":250000,"stock":10,
     "tipo":"fisico","peso_kg":1.2,"vendedor_email":None},
    {"id":"PROD-002","nombre":"Monitor 24 Full HD","precio":890000,"stock":5,
     "tipo":"fisico","peso_kg":4.5,"vendedor_email":None},
    {"id":"PROD-003","nombre":"Curso Python Avanzado","precio":120000,"stock":999,
     "tipo":"digital","url_descarga":"https://tienda.com/cursos","vendedor_email":None},
    {"id":"PROD-004","nombre":"Audifonos Bluetooth","precio":180000,"stock":8,
     "tipo":"oferta","descuento_pct":25,"vendedor_email":None},
    {"id":"PROD-005","nombre":"Pack Plantillas Office","precio":45000,"stock":999,
     "tipo":"digital","url_descarga":"https://tienda.com/plantillas","vendedor_email":None},
]


def _normalizar_tipo(tipo_raw: str) -> str:
    t = (tipo_raw or "").lower()
    if "oferta" in t:
        return "oferta"
    if "digital" in t:
        return "digital"
    return "fisico"


def _prod_con_precio_final(raw: dict) -> dict:
    """Agrega precio_final al dict del producto y normaliza el campo tipo."""
    entry = dict(raw)
    entry["tipo"] = _normalizar_tipo(raw.get("tipo", "fisico"))
    try:
        prod = ProductoFactory.desde_dict(dict(raw))
        entry["precio_final"] = round(prod.calcular_precio_final())
    except Exception:
        entry["precio_final"] = raw.get("precio", 0)
    return entry


def _init_demo():
    """Carga los productos de demo si el catalogo esta vacio."""
    db = tienda._db
    if not db.listar_productos():
        for p in DEMO_PRODS:
            db.guardar_producto(p)
        db.registrar_evento("SISTEMA", "5 productos de demo cargados")


# ── Pagina principal ──────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# ── Login ─────────────────────────────────────────────────────────────────────

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    cliente_data = tienda._db.obtener_cliente(email)
    if not cliente_data:
        return jsonify({"error": "Cuenta no encontrada."}), 401
    stored = cliente_data.get("password", "")
    if stored and stored != password:
        return jsonify({"error": "Contrasena incorrecta."}), 401
    return jsonify({
        "ok": True,
        "email": email,
        "nombre": cliente_data["nombre"],
        "rol": cliente_data.get("rol", "comprador"),
    })


@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.json or {}
    if data.get("password") != ADMIN_PASS:
        return jsonify({"error": "Contrasena incorrecta."}), 401
    return jsonify({"ok": True})


# ── Productos ─────────────────────────────────────────────────────────────────

@app.route("/api/productos", methods=["GET"])
def listar_productos():
    return jsonify([_prod_con_precio_final(r) for r in tienda._db.listar_productos()])


@app.route("/api/productos", methods=["POST"])
def agregar_producto():
    data = dict(request.json or {})
    tipo = data.pop("tipo", "fisico")
    vendedor_email = data.pop("vendedor_email", None)
    if not data.get("id"):
        data["id"] = "PROD-" + uuid.uuid4().hex[:6].upper()
    try:
        p = tienda.agregar_producto(tipo, **data)
        # Guardar vendedor_email en el dict persistido
        prod_data = tienda._db.obtener_producto(p.id)
        if prod_data:
            prod_data["vendedor_email"] = vendedor_email
            tienda._db.guardar_producto(prod_data)
        tienda._db.registrar_evento("PRODUCTO_AGREGADO", f"{p.nombre} ({p.id})")
        return jsonify({"ok": True, "id": p.id})
    except TiendaError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/productos/<pid>", methods=["DELETE"])
def eliminar_producto(pid):
    tienda._db.eliminar_producto(pid)
    tienda._db.registrar_evento("PRODUCTO_ELIMINADO", pid)
    return jsonify({"ok": True})


# ── Clientes ──────────────────────────────────────────────────────────────────

@app.route("/api/clientes", methods=["GET"])
def listar_clientes():
    result = []
    for c in tienda._db.listar_clientes():
        result.append({
            "nombre":            c["nombre"],
            "email":             c["email"],
            "telefono":          c.get("telefono", ""),
            "direccion":         c.get("direccion", ""),
            "rol":               c.get("rol", "comprador"),
            "historial_pedidos": c.get("historial_pedidos", []),
        })
    return jsonify(result)


@app.route("/api/clientes", methods=["POST"])
def registrar_cliente():
    d = request.json or {}
    try:
        tienda.registrar_cliente(
            d["nombre"], d["email"],
            d.get("telefono", ""), d.get("direccion", ""),
            password=d.get("password", ""), rol=d.get("rol", "comprador"),
        )
        return jsonify({"ok": True, "email": d["email"].strip().lower()})
    except ClienteExistenteError as e:
        return jsonify({"error": str(e)}), 400


# ── Carrito ───────────────────────────────────────────────────────────────────

def _get_carritos(db):
    if "carritos" not in db._datos:
        db._datos["carritos"] = {}
    return db._datos["carritos"]


@app.route("/api/carrito/<email>", methods=["GET"])
def ver_carrito(email):
    db = tienda._db
    items_raw = _get_carritos(db).get(email, [])
    items, total = [], 0
    for item in items_raw:
        raw = db.obtener_producto(item["id"])
        if not raw:
            continue
        try:
            prod = ProductoFactory.desde_dict(dict(raw))
            pf = round(prod.calcular_precio_final())
        except Exception:
            pf = raw.get("precio", 0)
        sub = pf * item["qty"]
        total += sub
        items.append({
            "id":           item["id"],
            "qty":          item["qty"],
            "nombre":       raw.get("nombre", ""),
            "precio":       raw.get("precio", 0),
            "precio_final": pf,
            "subtotal":     sub,
            "tipo":         _normalizar_tipo(raw.get("tipo", "fisico")),
            "descuento_pct": raw.get("descuento_pct", 0),
        })
    return jsonify({"items": items, "total": total})


@app.route("/api/carrito/<email>", methods=["POST"])
def agregar_carrito(email):
    data = request.json or {}
    prod_id = data.get("id")
    qty = int(data.get("qty", 1))
    db = tienda._db
    raw = db.obtener_producto(prod_id)
    if not raw:
        return jsonify({"error": "Producto no encontrado."}), 404
    if raw.get("stock", 0) < qty:
        return jsonify({"error": f"Stock insuficiente. Disponible: {raw['stock']}."}), 400
    carritos = _get_carritos(db)
    if email not in carritos:
        carritos[email] = []
    existing = next((i for i in carritos[email] if i["id"] == prod_id), None)
    if existing:
        if existing["qty"] + qty > raw.get("stock", 0):
            return jsonify({"error": f"Stock insuficiente (ya tienes {existing['qty']} en el carrito)."}), 400
        existing["qty"] += qty
    else:
        carritos[email].append({"id": prod_id, "qty": qty})
    db.guardar()
    return jsonify({"ok": True})


@app.route("/api/carrito/<email>/<prod_id>", methods=["DELETE"])
def quitar_carrito(email, prod_id):
    db = tienda._db
    carritos = _get_carritos(db)
    carritos[email] = [i for i in carritos.get(email, []) if i["id"] != prod_id]
    db.guardar()
    return jsonify({"ok": True})


# ── Pedidos ───────────────────────────────────────────────────────────────────

@app.route("/api/pedidos", methods=["GET"])
def listar_pedidos():
    email = request.args.get("email")
    pedidos = tienda._db.listar_pedidos()
    if email:
        pedidos = [p for p in pedidos if p.get("cliente_email") == email]
    return jsonify(pedidos)


@app.route("/api/pedidos", methods=["POST"])
def confirmar_pedido():
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    db = tienda._db
    carritos = _get_carritos(db)
    carrito = carritos.get(email, [])
    if not carrito:
        return jsonify({"error": "El carrito esta vacio."}), 400

    total, items_pedido = 0, []
    for item in carrito:
        raw = db.obtener_producto(item["id"])
        if not raw:
            return jsonify({"error": f"Producto {item['id']} no encontrado."}), 400
        if raw.get("stock", 0) < item["qty"]:
            return jsonify({"error": f"Stock insuficiente para \"{raw['nombre']}\"."}), 400
        try:
            prod = ProductoFactory.desde_dict(dict(raw))
            pf = round(prod.calcular_precio_final())
        except Exception:
            pf = raw.get("precio", 0)
        sub = pf * item["qty"]
        total += sub
        items_pedido.append({
            "producto_id": item["id"],
            "nombre":      raw.get("nombre", ""),
            "cantidad":    item["qty"],
            "precio_final": pf,
            "subtotal":    sub,
        })

    for item in carrito:
        raw = db.obtener_producto(item["id"])
        raw["stock"] -= item["qty"]
        db.guardar_producto(raw)
        if raw["stock"] <= 3:
            db.registrar_evento("STOCK_BAJO",
                f"{raw['nombre']} -- quedan {raw['stock']} unidades")

    pid = "PED-" + uuid.uuid4().hex[:8].upper()
    pedido = {
        "id":            pid,
        "cliente_email": email,
        "fecha":         datetime.now().strftime("%d/%m/%Y %H:%M"),
        "estado":        "pendiente",
        "items":         items_pedido,
        "total":         total,
    }
    db.guardar_pedido(pedido)

    cliente_data = db.obtener_cliente(email)
    if cliente_data:
        cliente_data.setdefault("historial_pedidos", []).append(pid)
        db.guardar_cliente(cliente_data)

    carritos[email] = []
    db.guardar()
    db.registrar_evento("PEDIDO_CONFIRMADO", f"#{pid} -- Total: ${total:,.0f}")
    return jsonify({"ok": True, "pedido": pedido})


@app.route("/api/pedidos/<pid>", methods=["PATCH"])
def actualizar_estado(pid):
    data = request.json or {}
    estado = data.get("estado")
    pedido_data = tienda._db.obtener_pedido(pid)
    if not pedido_data:
        return jsonify({"error": "Pedido no encontrado."}), 404
    pedido_data["estado"] = estado
    tienda._db.guardar_pedido(pedido_data)
    tienda._db.registrar_evento("PEDIDO_ESTADO", f"#{pid} -> {estado}")
    return jsonify({"ok": True})


# ── Eventos ───────────────────────────────────────────────────────────────────

@app.route("/api/eventos", methods=["GET"])
def get_eventos():
    return jsonify(tienda._db._datos.get("eventos", []))


# ── Admin: Reset ──────────────────────────────────────────────────────────────

@app.route("/api/admin/reset", methods=["POST"])
def admin_reset():
    data = request.json or {}
    if data.get("password") != ADMIN_PASS:
        return jsonify({"error": "No autorizado."}), 401
    db = tienda._db
    db._datos = {"clientes": {}, "productos": {}, "pedidos": {}, "carritos": {}, "eventos": []}
    for p in DEMO_PRODS:
        db.guardar_producto(p)
    db.guardar()
    db.registrar_evento("SISTEMA", "Datos reseteados por el administrador")
    return jsonify({"ok": True})


# ── Arranque ──────────────────────────────────────────────────────────────────

_init_demo()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n{'='*52}")
    print("  Tienda POO -- Servidor iniciado")
    print(f"{'='*52}")
    print(f"  http://localhost:{port}")
    print(f"{'='*52}\n")
    app.run(host="0.0.0.0", debug=False, port=port)
