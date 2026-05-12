import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from servicios.tienda_service import TiendaService
from utils.excepciones import (
    TiendaError,            # Base: captura cualquier error del dominio
    ClienteExistenteError,
    ClienteNoEncontradoError,
    ProductoNoEncontradoError,
    StockInsuficienteError,
    CarritoVacioError,
)


# ── Observer: función registrada como listener ─────────────────────────────────
def logger_eventos(evento: str, detalle: str):
    iconos = {
        "NUEVO_CLIENTE":     "",
        "PEDIDO_CONFIRMADO": "",
        "STOCK_BAJO":        "",
    }
    icono = iconos.get(evento, "")
    print(f"\n  {icono}  [{evento}] {detalle}")


def separador(titulo=""):
    ancho = 48
    if titulo:
        print(f"\n{'─'*ancho}")
        print(f"  {titulo.upper()}")
        print(f"{'─'*ancho}")
    else:
        print(f"{'─'*ancho}")


def menu_principal():
    tienda = TiendaService()          # DIP: usa BaseDatos por defecto
    tienda.registrar_observador(logger_eventos)

    if not tienda.listar_productos():
        _cargar_datos_demo(tienda)

    while True:
        print("\n" + "═"*48)
        print("TIENDA POO — MENÚ PRINCIPAL")
        print("═"*48)
        print("  1. Ver catálogo de productos")
        print("  2. Registrar cliente")
        print("  3. Agregar producto al carrito")
        print("  4. Ver carrito")
        print("  5. Confirmar pedido")
        print("  6. Ver pedidos realizados")
        print("  7. Ver clientes registrados")
        print("  8. Buscar productos por nombre")
        print("  9. Catálogo ordenado por precio")
        print("  0. Salir")
        print("═"*48)

        opcion = input("  Selecciona una opción: ").strip()

        if opcion == "1":
            _ver_catalogo(tienda)
        elif opcion == "2":
            _registrar_cliente(tienda)
        elif opcion == "3":
            _agregar_al_carrito(tienda)
        elif opcion == "4":
            _ver_carrito(tienda)
        elif opcion == "5":
            _confirmar_pedido(tienda)
        elif opcion == "6":
            _ver_pedidos(tienda)
        elif opcion == "7":
            _ver_clientes(tienda)
        elif opcion == "8":
            _buscar_productos(tienda)
        elif opcion == "9":
            _catalogo_por_precio(tienda)
        elif opcion == "0":
            print("\n ¡Hasta pronto!\n")
            break
        else:
            print("Opción no válida.")


# ── Funciones de cada opción ───────────────────────────────────────────────────

def _ver_catalogo(tienda: TiendaService):
    separador("Catálogo de Productos")
    productos = tienda.listar_productos()
    if not productos:
        print("  No hay productos disponibles.")
        return
    for p in productos:
        print(f"  {p}")


def _registrar_cliente(tienda: TiendaService):
    separador("Registro de Cliente")
    try:
        nombre    = input("  Nombre    : ").strip()
        email     = input("  Email     : ").strip()
        telefono  = input("  Teléfono  : ").strip()
        direccion = input("  Dirección : ").strip()
        tienda.registrar_cliente(nombre, email, telefono, direccion)
        print("  Cliente registrado exitosamente.")
    except ClienteExistenteError as e:
        # Captura específica: sabemos exactamente qué falló
        print(f"  error: {e}")
    except TiendaError as e:
        print(f"Error del sistema: {e}")


def _agregar_al_carrito(tienda: TiendaService):
    separador("Agregar al Carrito")
    try:
        email    = input("  Email del cliente  : ").strip()
        id_prod  = input("  ID del producto    : ").strip()
        cantidad = int(input("  Cantidad           : ").strip())
        tienda.agregar_al_carrito(email, id_prod, cantidad)
        print(" Producto agregado al carrito.")
    except ProductoNoEncontradoError as e:
        print(f"  error: {e}")
    except StockInsuficienteError as e:
        print(f"  error: {e}")
    except TiendaError as e:
        print(f"  error: {e}")


def _ver_carrito(tienda: TiendaService):
    email = input("\n  Email del cliente: ").strip()
    tienda.obtener_carrito(email).mostrar()


def _confirmar_pedido(tienda: TiendaService):
    email = input("\n  Email del cliente: ").strip()
    try:
        pedido = tienda.confirmar_pedido(email)
        print(pedido.mostrar_resumen())
    except CarritoVacioError as e:
        print(f"  error: {e}")
    except StockInsuficienteError as e:
        print(f"  error: {e}")
    except TiendaError as e:
        print(f"  error: {e}")


def _ver_pedidos(tienda: TiendaService):
    separador("Pedidos Realizados")
    pedidos = tienda.listar_pedidos()
    if not pedidos:
        print("  No hay pedidos aún.")
        return
    for p in pedidos:
        print(f"  #{p['id']} | {p['cliente_email']} | {p['estado'].upper()} | ${p['total']:,.2f}")


def _ver_clientes(tienda: TiendaService):
    separador("Clientes Registrados")
    # Anti-patrón corregido: antes era tienda._db.listar_clientes()
    # Ahora usamos el método público de TiendaService (SRP + Encapsulamiento)
    clientes = tienda.listar_clientes()
    if not clientes:
        print("  No hay clientes registrados.")
        return
    for c in clientes:
        print(f"  {c}")


def _buscar_productos(tienda: TiendaService):
    separador("Buscar Productos")
    texto = input("  Texto a buscar: ").strip()
    resultados = tienda.buscar_productos_por_nombre(texto)
    if not resultados:
        print("  No se encontraron productos.")
        return
    for p in resultados:
        print(f"  {p}")


def _catalogo_por_precio(tienda: TiendaService):
    separador("Catálogo Ordenado por Precio")
    orden = input("  Orden (1=menor a mayor, 2=mayor a menor): ").strip()
    ascendente = orden != "2"
    for p in tienda.productos_ordenados_por_precio(ascendente):
        print(f"  {p}")


# ── Datos de demostración ──────────────────────────────────────────────────────

def _cargar_datos_demo(tienda: TiendaService):
    tienda.agregar_producto("fisico",  id="PROD-001", nombre="Teclado Mecánico RGB",  precio=250_000, stock=10, peso_kg=1.2)
    tienda.agregar_producto("fisico",  id="PROD-002", nombre='Monitor 24" Full HD',   precio=890_000, stock=5,  peso_kg=4.5)
    tienda.agregar_producto("digital", id="PROD-003", nombre="Curso Python Avanzado", precio=120_000, stock=999, url_descarga="https://tienda.com/cursos/python")
    tienda.agregar_producto("oferta",  id="PROD-004", nombre="Audífonos Bluetooth",   precio=180_000, stock=8,  descuento_pct=25)
    tienda.agregar_producto("digital", id="PROD-005", nombre="Pack Plantillas Office",precio=45_000,  stock=999, url_descarga="https://tienda.com/plantillas")


if __name__ == "__main__":
    menu_principal()
