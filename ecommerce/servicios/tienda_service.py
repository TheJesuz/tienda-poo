"""
TiendaService — Servicio principal del sistema e-commerce.

Patrones y principios aplicados:
- Observer (GoF Comportamiento): _notificar() desacopla eventos de manejadores.
- DIP (SOLID): recibe IRepositorio por inyección, no instancia BaseDatos directo.
  Esto permite pasar un RepositorioEnMemoria en tests sin tocar este archivo.
- SRP: cada método tiene UNA responsabilidad definida.
- OCP: se pueden agregar nuevos tipos de productos sin modificar este servicio.
"""

import uuid
from modelos.cliente import Cliente
from modelos.pedido import Pedido, CarritoCompras
from modelos.interfaces import IRepositorio               # DIP: dependemos de la abstracción
from persistencia.base_datos import BaseDatos
from servicios.producto_factory import ProductoFactory
from servicios.pedido_builder import PedidoBuilder        # Builder (GoF Creacional)
from utils.excepciones import (
    ClienteExistenteError,
    ClienteNoEncontradoError,
    ProductoNoEncontradoError,
    StockInsuficienteError,
    CarritoVacioError,
)


class TiendaService:
    """
    Orquesta todas las operaciones de la tienda.

    DIP en práctica:
        El constructor acepta cualquier objeto que cumpla IRepositorio.
        Por defecto usa BaseDatos (Singleton con JSON), pero en tests
        se puede inyectar un repositorio en memoria sin cambiar esta clase.
    """

    STOCK_MINIMO = 3

    def __init__(self, repositorio: IRepositorio = None):
        # DIP: dependemos de IRepositorio, no de BaseDatos directamente.
        self._db: IRepositorio = repositorio if repositorio is not None else BaseDatos()
        self._carritos: dict[str, CarritoCompras] = {}
        self._observadores = []

    # ── Observer ──────────────────────────────────────────────────────────────

    def registrar_observador(self, fn):
        """Registra una función que será llamada cuando ocurra un evento."""
        self._observadores.append(fn)

    def _notificar(self, evento: str, detalle: str):
        """Recorre la lista de observadores y los notifica. Acoplamiento cero."""
        for fn in self._observadores:
            fn(evento, detalle)

    # ── Clientes ──────────────────────────────────────────────────────────────

    def registrar_cliente(self, nombre: str, email: str, telefono: str, direccion: str,
                          password: str = "", rol: str = "comprador") -> Cliente:
        if self._db.obtener_cliente(email):
            raise ClienteExistenteError(email)
        cliente = Cliente(nombre, email, telefono, direccion, password=password, rol=rol)
        self._db.guardar_cliente(cliente.to_dict())
        self._notificar("NUEVO_CLIENTE", f"{nombre} ({email}) [{rol}]")
        return cliente

    def obtener_cliente(self, email: str) -> Cliente:
        data = self._db.obtener_cliente(email)
        if not data:
            raise ClienteNoEncontradoError(email)
        return Cliente.from_dict(data)

    def listar_clientes(self) -> list:
        """
        SRP + Anti-patrón corregido:
        Antes, main.py accedía a tienda._db.listar_clientes() directamente,
        violando encapsulamiento. Ahora todo pasa por TiendaService.
        """
        return [Cliente.from_dict(d) for d in self._db.listar_clientes()]

    # ── Productos ─────────────────────────────────────────────────────────────

    def agregar_producto(self, tipo: str, **kwargs):
        if not kwargs.get("id"):
            kwargs["id"] = f"PROD-{uuid.uuid4().hex[:6].upper()}"
        producto = ProductoFactory.crear(tipo, **kwargs)
        self._db.guardar_producto(producto.to_dict())
        return producto

    def listar_productos(self):
        return [ProductoFactory.desde_dict(d) for d in self._db.listar_productos()]

    def buscar_producto(self, id_producto: str):
        """Retorna el producto o lanza ProductoNoEncontradoError."""
        data = self._db.obtener_producto(id_producto)
        if not data:
            raise ProductoNoEncontradoError(id_producto)
        return ProductoFactory.desde_dict(data)

    def buscar_productos_por_nombre(self, texto: str):
        """
        Búsqueda por texto usando filter() + lambda.
        Preparado para Semana 10-11 (Programación Funcional).
        """
        texto = texto.lower()
        return list(filter(
            lambda p: texto in p.nombre.lower(),
            self.listar_productos()
        ))

    def productos_ordenados_por_precio(self, ascendente: bool = True):
        """sorted() con key lambda. Semana 10-11."""
        return sorted(
            self.listar_productos(),
            key=lambda p: p.calcular_precio_final(),
            reverse=not ascendente
        )

    # ── Carrito ───────────────────────────────────────────────────────────────

    def obtener_carrito(self, cliente_email: str) -> CarritoCompras:
        if cliente_email not in self._carritos:
            self._carritos[cliente_email] = CarritoCompras(cliente_email)
        return self._carritos[cliente_email]

    def agregar_al_carrito(self, cliente_email: str, id_producto: str, cantidad: int):
        producto = self.buscar_producto(id_producto)
        if producto.stock < cantidad:
            raise StockInsuficienteError(producto.nombre, producto.stock, cantidad)
        self.obtener_carrito(cliente_email).agregar_producto(producto, cantidad)

    # ── Pedidos ───────────────────────────────────────────────────────────────

    def confirmar_pedido(self, cliente_email: str) -> Pedido:
        """
        Usa PedidoBuilder internamente para construir el Pedido.
        Builder (GoF Creacional) centraliza la lógica de construcción.
        """
        carrito = self.obtener_carrito(cliente_email)
        if not carrito.items:
            raise CarritoVacioError(cliente_email)

        # Builder valida stock por ítem y construye el Pedido
        builder = PedidoBuilder(cliente_email)
        for item in carrito.items:
            producto_actual = self.buscar_producto(item.producto.id)
            builder.agregar_item(producto_actual, item.cantidad)

        pedido = builder.construir()

        # Descontar stock y persistir
        for item in carrito.items:
            producto = self.buscar_producto(item.producto.id)
            producto.reducir_stock(item.cantidad)
            self._db.guardar_producto(producto.to_dict())

            if producto.stock <= self.STOCK_MINIMO:
                self._notificar(
                    "STOCK_BAJO",
                    f"{producto.nombre} — quedan {producto.stock} unidades"
                )

        # Persistir pedido y actualizar historial del cliente
        self._db.guardar_pedido(pedido.to_dict())

        cliente_data = self._db.obtener_cliente(cliente_email)
        if cliente_data:
            cliente_data["historial_pedidos"].append(pedido.id)
            self._db.guardar_cliente(cliente_data)

        carrito.vaciar()
        self._notificar("PEDIDO_CONFIRMADO", f"#{pedido.id} — Total: ${pedido.total:,.2f}")
        return pedido

    def listar_pedidos(self):
        return self._db.listar_pedidos()

    def nuevo_builder(self, cliente_email: str) -> PedidoBuilder:
        """
        Expone el Builder para construir pedidos fuera del flujo del carrito.
        """
        return PedidoBuilder(cliente_email)
