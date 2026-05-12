from datetime import datetime
from modelos.producto import Producto
from utils.excepciones import EstadoInvalidoError


class ItemCarrito:
    """Representa un producto dentro del carrito con su cantidad."""

    def __init__(self, producto: Producto, cantidad: int):
        self.producto = producto
        self.cantidad = cantidad

    @property
    def subtotal(self) -> float:
        return self.producto.calcular_precio_final() * self.cantidad

    def __str__(self):
        return (
            f"  • {self.producto.nombre} x{self.cantidad} "
            f"= ${self.subtotal:,.2f}"
        )


class Pedido:
    """Representa una orden de compra confirmada."""

    ESTADOS = ["pendiente", "procesando", "enviado", "entregado", "cancelado"]

    def __init__(self, id_pedido: str, cliente_email: str, items: list[ItemCarrito]):
        self._id = id_pedido
        self._cliente_email = cliente_email
        self._items = items
        self._fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        self._estado = "pendiente"

    @property
    def id(self):
        return self._id

    @property
    def estado(self):
        return self._estado

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self._items)

    def actualizar_estado(self, nuevo_estado: str):
        if nuevo_estado not in self.ESTADOS:
            raise EstadoInvalidoError(nuevo_estado, self.ESTADOS)
        self._estado = nuevo_estado

    def mostrar_resumen(self) -> str:
        lineas = [
            f"\n{'='*45}",
            f"  PEDIDO #{self._id}",
            f"  Cliente : {self._cliente_email}",
            f"  Fecha   : {self._fecha}",
            f"  Estado  : {self._estado.upper()}",
            f"{'─'*45}",
        ]
        for item in self._items:
            lineas.append(str(item))
        lineas.append(f"{'─'*45}")
        lineas.append(f"  TOTAL   : ${self.total:,.2f}")
        lineas.append(f"{'='*45}")
        return "\n".join(lineas)

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "cliente_email": self._cliente_email,
            "fecha": self._fecha,
            "estado": self._estado,
            "items": [
                {"producto_id": i.producto.id, "cantidad": i.cantidad, "subtotal": i.subtotal}
                for i in self._items
            ],
            "total": self.total,
        }


class CarritoCompras:
    """Carrito temporal antes de confirmar el pedido."""

    def __init__(self, cliente_email: str):
        self._cliente_email = cliente_email
        self._items: list[ItemCarrito] = []

    def agregar_producto(self, producto: Producto, cantidad: int):
        # Si ya existe, aumenta cantidad
        for item in self._items:
            if item.producto.id == producto.id:
                item.cantidad += cantidad
                return
        self._items.append(ItemCarrito(producto, cantidad))

    def eliminar_producto(self, producto_id: str):
        self._items = [i for i in self._items if i.producto.id != producto_id]

    def vaciar(self):
        self._items.clear()

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self._items)

    @property
    def items(self):
        return self._items

    def mostrar(self):
        if not self._items:
            print("  El carrito está vacío.")
            return
        print(f"\n{'─'*40}")
        print(f"  🛒  CARRITO DE {self._cliente_email}")
        print(f"{'─'*40}")
        for item in self._items:
            print(item)
        print(f"{'─'*40}")
        print(f"  TOTAL: ${self.total:,.2f}\n")
