"""
Excepciones de dominio del sistema de tienda.

Por qué esto importa (Anti-Patrones – POO 14):
- Usar ValueError genérico en todas partes es un Anemic Exception anti-pattern.
- Las excepciones propias del dominio comunican exactamente QUÉ falló y DÓNDE,
  hacen el código más legible y permiten capturar errores específicos en el main.
- Jerarquía: TiendaError es la raíz → cualquier except TiendaError captura todo.
"""


class TiendaError(Exception):
    """Raíz de todas las excepciones del dominio. Facilita captura global."""
    pass


# ── Errores de Producto ────────────────────────────────────────────────────────

class ProductoNoEncontradoError(TiendaError):
    """Se lanza cuando se busca un ID de producto que no existe en la BD."""
    def __init__(self, id_producto: str):
        super().__init__(f"Producto '{id_producto}' no encontrado en el catálogo.")
        self.id_producto = id_producto


class StockInsuficienteError(TiendaError):
    """Se lanza cuando la cantidad pedida supera el stock disponible."""
    def __init__(self, nombre_producto: str, stock_disponible: int, cantidad_pedida: int):
        super().__init__(
            f"Stock insuficiente para '{nombre_producto}'. "
            f"Disponible: {stock_disponible} | Pedido: {cantidad_pedida}."
        )
        self.stock_disponible = stock_disponible
        self.cantidad_pedida = cantidad_pedida


class TipoProductoInvalidoError(TiendaError):
    """Se lanza cuando ProductoFactory recibe un tipo desconocido."""
    TIPOS_VALIDOS = ("fisico", "digital", "oferta")

    def __init__(self, tipo: str):
        super().__init__(
            f"Tipo de producto desconocido: '{tipo}'. "
            f"Tipos válidos: {self.TIPOS_VALIDOS}."
        )


# ── Errores de Cliente ─────────────────────────────────────────────────────────

class ClienteExistenteError(TiendaError):
    """Se lanza al intentar registrar un email que ya existe en la BD."""
    def __init__(self, email: str):
        super().__init__(f"El email '{email}' ya está registrado.")
        self.email = email


class ClienteNoEncontradoError(TiendaError):
    """Se lanza cuando se intenta operar con un cliente que no existe."""
    def __init__(self, email: str):
        super().__init__(f"No se encontró ningún cliente con el email '{email}'.")
        self.email = email


# ── Errores de Carrito / Pedido ────────────────────────────────────────────────

class CarritoVacioError(TiendaError):
    """Se lanza al intentar confirmar un pedido con el carrito vacío."""
    def __init__(self, email: str):
        super().__init__(f"El carrito de '{email}' está vacío. Agregue productos antes de confirmar.")


class EstadoInvalidoError(TiendaError):
    """Se lanza al intentar poner un Pedido en un estado que no existe."""
    def __init__(self, estado: str, estados_validos: list):
        super().__init__(
            f"Estado '{estado}' no válido. Opciones: {estados_validos}."
        )
