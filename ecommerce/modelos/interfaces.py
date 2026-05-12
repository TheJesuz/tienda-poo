"""
Interfaces formales del sistema usando typing.Protocol (Python 3.8+).

Por qué esto importa (SOLID – Sem 7):

I – Interface Segregation Principle:
    En lugar de una sola interfaz gigante, se define una interfaz pequeña
    y específica para cada capacidad. Ninguna clase es obligada a implementar
    métodos que no usa.

D – Dependency Inversion Principle:
    Los módulos de alto nivel (TiendaService) no deben depender de módulos
    de bajo nivel (BaseDatos). Ambos deben depender de esta abstracción.
    TiendaService depende de IRepositorio, no de BaseDatos directamente.

Python y las interfaces:
    Python no tiene la palabra clave 'interface'. El equivalente idiomático
    es typing.Protocol: define el contrato sin herencia obligatoria
    (duck typing estructural). Si una clase implementa los métodos del
    protocolo, cumple la interfaz — sin importar su árbol de herencia.
"""

from typing import Protocol, runtime_checkable


# ── ISP: Interfaces pequeñas y específicas ────────────────────────────────────

@runtime_checkable
class ISerializable(Protocol):
    """
    Contrato para objetos que se pueden convertir a/desde diccionario.
    Cumple SRP: la serialización es UNA responsabilidad.
    """
    def to_dict(self) -> dict:
        ...

    @classmethod
    def from_dict(cls, data: dict):
        ...


@runtime_checkable
class IPreciable(Protocol):
    """
    Contrato para cualquier objeto que tenga un precio calculable.
    Separa el cálculo de precio de otras responsabilidades del producto.
    """
    def calcular_precio_final(self) -> float:
        ...


@runtime_checkable
class ICategorizeable(Protocol):
    """
    Contrato para objetos que pertenecen a una categoría.
    """
    def categoria(self) -> str:
        ...


# ── DIP: Abstracción del repositorio ─────────────────────────────────────────

@runtime_checkable
class IRepositorio(Protocol):
    """
    Contrato que cualquier repositorio de datos debe cumplir.

    DIP en práctica:
        - TiendaService depende de IRepositorio (abstracción).
        - BaseDatos implementa IRepositorio (detalle concreto).
        - En tests podemos pasar un RepositorioEnMemoria sin tocar TiendaService.
    """

    # ── Clientes ──
    def guardar_cliente(self, cliente_dict: dict) -> None: ...
    def obtener_cliente(self, email: str) -> dict | None: ...
    def listar_clientes(self) -> list[dict]: ...

    # ── Productos ──
    def guardar_producto(self, producto_dict: dict) -> None: ...
    def obtener_producto(self, id_producto: str) -> dict | None: ...
    def listar_productos(self) -> list[dict]: ...
    def eliminar_producto(self, id_producto: str) -> None: ...

    # ── Pedidos ──
    def guardar_pedido(self, pedido_dict: dict) -> None: ...
    def obtener_pedido(self, id_pedido: str) -> dict | None: ...
    def listar_pedidos(self) -> list[dict]: ...
