from abc import ABC, abstractmethod
from utils.excepciones import StockInsuficienteError

# ISP: Producto cumple implícitamente IPreciable, ICategorizeable e ISerializable
# (definidas en modelos/interfaces.py). Python lo verifica estructuralmente
# gracias a typing.Protocol — no hace falta herencia explícita.


class Producto(ABC):
    """
    Clase base abstracta para todos los productos de la tienda.

    Principios aplicados:
    - Abstracción: define el CONTRATO sin implementación completa.
    - Encapsulamiento: atributos privados expuestos solo vía @property.
    - Herencia + Polimorfismo: calcular_precio_final() es diferente en cada subclase.
    - ISP: cumple IPreciable, ICategorizeable, ISerializable (modelos/interfaces.py).
    """

    def __init__(self, id_producto: str, nombre: str, precio: float, stock: int):
        self._id = id_producto
        self._nombre = nombre
        self._precio = precio
        self._stock = stock

    # ----- Getters -----
    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @property
    def precio(self):
        return self._precio

    @property
    def stock(self):
        return self._stock

    def reducir_stock(self, cantidad: int):
        if cantidad > self._stock:
            raise StockInsuficienteError(self._nombre, self._stock, cantidad)
        self._stock -= cantidad

    def aumentar_stock(self, cantidad: int):
        self._stock += cantidad

    @abstractmethod
    def calcular_precio_final(self) -> float:
        """Cada tipo de producto puede aplicar lógica de precio diferente (polimorfismo)."""
        pass

    @abstractmethod
    def categoria(self) -> str:
        pass

    def mostrar_info(self) -> str:
        return (
            f"[{self.categoria()}] {self._nombre} (ID: {self._id}) | "
            f"Precio: ${self.calcular_precio_final():,.2f} | Stock: {self._stock}"
        )

    def __str__(self):
        return self.mostrar_info()

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "nombre": self._nombre,
            "precio": self._precio,
            "stock": self._stock,
            "tipo": self.categoria(),
        }


# ─────────────────────────────────────────────
#  Subclases concretas (herencia + polimorfismo)
# ─────────────────────────────────────────────

class ProductoFisico(Producto):
    """Producto que requiere envío físico."""

    def __init__(self, id_producto, nombre, precio, stock, peso_kg: float):
        super().__init__(id_producto, nombre, precio, stock)
        self._peso_kg = peso_kg

    @property
    def peso_kg(self):
        return self._peso_kg

    def calcular_precio_final(self) -> float:
        # Aplica cargo de envío según peso
        costo_envio = self._peso_kg * 2_000  # $2.000 por kg
        return self._precio + costo_envio

    def categoria(self) -> str:
        return "FÍSICO"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["peso_kg"] = self._peso_kg
        return data


class ProductoDigital(Producto):
    """Producto de descarga digital (sin envío)."""

    def __init__(self, id_producto, nombre, precio, stock, url_descarga: str):
        super().__init__(id_producto, nombre, precio, stock)
        self._url_descarga = url_descarga

    def calcular_precio_final(self) -> float:
        # Sin costo de envío, pero aplica IVA del 19 %
        return self._precio * 1.19

    def categoria(self) -> str:
        return "DIGITAL"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["url_descarga"] = self._url_descarga
        return data


class ProductoOferta(Producto):
    """Producto con descuento especial."""

    def __init__(self, id_producto, nombre, precio, stock, descuento_pct: float):
        super().__init__(id_producto, nombre, precio, stock)
        self._descuento_pct = descuento_pct  # ej. 20 para 20 %

    def calcular_precio_final(self) -> float:
        return self._precio * (1 - self._descuento_pct / 100)

    def categoria(self) -> str:
        return f"OFERTA -{self._descuento_pct}%"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["descuento_pct"] = self._descuento_pct
        return data
