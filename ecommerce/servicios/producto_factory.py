from modelos.producto import Producto, ProductoFisico, ProductoDigital, ProductoOferta
from utils.excepciones import TipoProductoInvalidoError


class ProductoFactory:
    """
    Patrón Factory: centraliza la creación de productos.
    Recibe un tipo como string y devuelve la instancia correcta,
    sin que el resto del sistema necesite conocer las subclases.
    """

    @staticmethod
    def crear(tipo: str, **kwargs) -> Producto:
        tipo = tipo.lower()
        # Extraer solo los campos base comunes; ignorar extras (vendedor_email, precio_final, etc.)
        pid    = kwargs.get("id")
        nombre = kwargs.get("nombre")
        precio = kwargs.get("precio")
        stock  = kwargs.get("stock", 0)

        if tipo == "fisico":
            return ProductoFisico(
                id_producto=pid, nombre=nombre, precio=precio, stock=stock,
                peso_kg=kwargs.get("peso_kg", 0.5),
            )
        elif tipo == "digital":
            return ProductoDigital(
                id_producto=pid, nombre=nombre, precio=precio,
                stock=kwargs.get("stock", 9999),
                url_descarga=kwargs.get("url_descarga", ""),
            )
        elif tipo == "oferta":
            return ProductoOferta(
                id_producto=pid, nombre=nombre, precio=precio, stock=stock,
                descuento_pct=kwargs.get("descuento_pct", 10),
            )
        else:
            raise TipoProductoInvalidoError(tipo)

    @staticmethod
    def desde_dict(data: dict) -> Producto:
        """Reconstruye un producto a partir de un diccionario (útil para persistencia)."""
        data = dict(data)  # copia para no mutar el original
        tipo_raw = data.pop("tipo", "fisico").lower()

        if "oferta" in tipo_raw:
            tipo = "oferta"
        elif tipo_raw == "digital":
            tipo = "digital"
        else:
            tipo = "fisico"

        return ProductoFactory.crear(tipo, **data)
