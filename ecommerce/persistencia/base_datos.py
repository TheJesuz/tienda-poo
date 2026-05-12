import json
import os
from datetime import datetime


class BaseDatos:
    """
    Patrón Singleton: garantiza una única instancia de la base de datos
    durante toda la ejecución del programa.
    """

    _instancia = None
    _ARCHIVO = "datos_tienda.json"

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._datos = {
                "clientes": {},
                "productos": {},
                "pedidos": {},
                "carritos": {},
                "eventos": [],
            }
            cls._instancia._cargar()
        return cls._instancia

    def _cargar(self):
        if os.path.exists(self._ARCHIVO):
            with open(self._ARCHIVO, "r", encoding="utf-8") as f:
                self._datos = json.load(f)
            if "carritos" not in self._datos:
                self._datos["carritos"] = {}
            if "eventos" not in self._datos:
                self._datos["eventos"] = []

    def guardar(self):
        with open(self._ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(self._datos, f, ensure_ascii=False, indent=2)

    # ── Observer: persiste eventos ─────────────────────────────
    def registrar_evento(self, evento: str, detalle: str):
        self._datos["eventos"].append({
            "evento": evento,
            "detalle": detalle,
            "hora": datetime.now().strftime("%H:%M:%S"),
        })
        self._datos["eventos"] = self._datos["eventos"][-50:]
        self.guardar()

    # ── Clientes ───────────────────────────────────────────────
    def guardar_cliente(self, cliente_dict: dict):
        self._datos["clientes"][cliente_dict["email"]] = cliente_dict
        self.guardar()

    def obtener_cliente(self, email: str) -> dict | None:
        return self._datos["clientes"].get(email)

    def listar_clientes(self) -> list[dict]:
        return list(self._datos["clientes"].values())

    # ── Productos ──────────────────────────────────────────────
    def guardar_producto(self, producto_dict: dict):
        self._datos["productos"][producto_dict["id"]] = producto_dict
        self.guardar()

    def obtener_producto(self, id_producto: str) -> dict | None:
        return self._datos["productos"].get(id_producto)

    def listar_productos(self) -> list[dict]:
        return list(self._datos["productos"].values())

    def eliminar_producto(self, id_producto: str):
        self._datos["productos"].pop(id_producto, None)
        self.guardar()

    # ── Pedidos ────────────────────────────────────────────────
    def guardar_pedido(self, pedido_dict: dict):
        self._datos["pedidos"][pedido_dict["id"]] = pedido_dict
        self.guardar()

    def obtener_pedido(self, id_pedido: str) -> dict | None:
        return self._datos["pedidos"].get(id_pedido)

    def listar_pedidos(self) -> list[dict]:
        return list(self._datos["pedidos"].values())
