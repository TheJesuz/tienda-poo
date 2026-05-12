from abc import ABC, abstractmethod


class Persona(ABC):
    """Clase base abstracta para todas las personas del sistema."""

    def __init__(self, nombre: str, email: str, telefono: str):
        self._nombre = nombre
        self._email = email
        self._telefono = telefono

    # ----- Getters y Setters -----
    @property
    def nombre(self):
        return self._nombre

    @property
    def email(self):
        return self._email

    @property
    def telefono(self):
        return self._telefono

    @abstractmethod
    def mostrar_info(self) -> str:
        """Cada subclase muestra su información de forma distinta (polimorfismo)."""
        pass

    def __str__(self):
        return self.mostrar_info()
