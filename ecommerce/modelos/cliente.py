from modelos.persona import Persona


class Cliente(Persona):
    """Representa a un cliente registrado en la tienda."""

    def __init__(self, nombre: str, email: str, telefono: str, direccion: str,
                 password: str = "", rol: str = "comprador"):
        super().__init__(nombre, email, telefono)
        self._direccion = direccion
        self._password = password
        self._rol = rol
        self._historial_pedidos = []   # Lista de IDs de pedidos

    @property
    def direccion(self):
        return self._direccion

    @property
    def historial_pedidos(self):
        return self._historial_pedidos

    def agregar_pedido(self, pedido_id: str):
        self._historial_pedidos.append(pedido_id)

    # Polimorfismo: implementación concreta de mostrar_info
    def mostrar_info(self) -> str:
        return (
            f"[CLIENTE] {self._nombre} | "
            f"Email: {self._email} | "
            f"Tel: {self._telefono} | "
            f"Dirección: {self._direccion} | "
            f"Pedidos realizados: {len(self._historial_pedidos)}"
        )

    def to_dict(self) -> dict:
        return {
            "nombre": self._nombre,
            "email": self._email,
            "telefono": self._telefono,
            "direccion": self._direccion,
            "password": self._password,
            "rol": self._rol,
            "historial_pedidos": self._historial_pedidos,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Cliente":
        cliente = cls(
            data["nombre"], data["email"], data["telefono"], data["direccion"],
            password=data.get("password", ""), rol=data.get("rol", "comprador"),
        )
        cliente._historial_pedidos = data.get("historial_pedidos", [])
        return cliente
