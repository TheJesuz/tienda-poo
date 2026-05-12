"""
Patrón Builder — GoF Creacional (servicios/pedido_builder.py)

Propósito (según catálogo GoF):
    Permite la creación dinámica de objetos con base en algoritmos
    fácilmente intercambiables. Separa la CONSTRUCCIÓN de un objeto
    complejo de su REPRESENTACIÓN final.

Por qué aquí:
    Un Pedido puede ser simple (un ítem) o muy complejo (múltiples ítems,
    validaciones de stock, descuentos por volumen). El Builder permite
    construirlo paso a paso sin exponer esa complejidad al código cliente.

    Sin Builder (antes):
        pedido = Pedido(id, email, items_copiados_directo)  ← acoplado

    Con Builder (ahora):
        builder = PedidoBuilder(email)
        builder.agregar_item(producto, cantidad)            ← paso a paso
        builder.agregar_item(producto2, 2)
        pedido = builder.construir()                        ← resultado limpio

Relación con OCP:
    Se puede extender PedidoBuilder con PedidoConDescuentoBuilder o
    PedidoExpressBuilder sin modificar la clase Pedido ni TiendaService.
"""

import uuid
from modelos.pedido import Pedido, ItemCarrito
from modelos.producto import Producto
from utils.excepciones import StockInsuficienteError, CarritoVacioError


class PedidoBuilder:
    """
    Director + Builder en uno (simplificación válida para este tamaño de sistema).
    Acumula ítems validando stock en cada paso, luego construye el Pedido final.
    """

    def __init__(self, cliente_email: str):
        self._cliente_email = cliente_email
        self._items: list[ItemCarrito] = []

    # ── Construcción paso a paso ───────────────────────────────────────────────

    def agregar_item(self, producto: Producto, cantidad: int) -> "PedidoBuilder":
        """
        Agrega un ítem al pedido en construcción.
        Lanza StockInsuficienteError si la cantidad pedida supera el stock.
        Retorna self para permitir encadenamiento fluido: builder.agregar().agregar()
        """
        if cantidad > producto.stock:
            raise StockInsuficienteError(producto.nombre, producto.stock, cantidad)

        # Si el producto ya está en la lista, incrementa cantidad
        for item in self._items:
            if item.producto.id == producto.id:
                nueva_cantidad = item.cantidad + cantidad
                if nueva_cantidad > producto.stock:
                    raise StockInsuficienteError(
                        producto.nombre, producto.stock, nueva_cantidad
                    )
                item.cantidad = nueva_cantidad
                return self

        self._items.append(ItemCarrito(producto, cantidad))
        return self  # permite encadenamiento fluido

    def eliminar_item(self, id_producto: str) -> "PedidoBuilder":
        """Quita un ítem del pedido en construcción."""
        self._items = [i for i in self._items if i.producto.id != id_producto]
        return self

    def limpiar(self) -> "PedidoBuilder":
        """Reinicia la construcción desde cero."""
        self._items.clear()
        return self

    # ── Construcción final ────────────────────────────────────────────────────

    def construir(self) -> Pedido:
        """
        Produce el objeto Pedido final.
        Lanza CarritoVacioError si no se agregó ningún ítem.
        """
        if not self._items:
            raise CarritoVacioError(self._cliente_email)

        pedido_id = f"PED-{uuid.uuid4().hex[:8].upper()}"
        return Pedido(pedido_id, self._cliente_email, self._items.copy())

    # ── Consulta del estado actual ─────────────────────────────────────────────

    @property
    def total_parcial(self) -> float:
        """Permite consultar el total antes de construir el pedido."""
        return sum(item.subtotal for item in self._items)

    @property
    def cantidad_items(self) -> int:
        return len(self._items)

    def __repr__(self):
        return (
            f"PedidoBuilder(cliente='{self._cliente_email}', "
            f"items={self.cantidad_items}, total=${self.total_parcial:,.2f})"
        )
