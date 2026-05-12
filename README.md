# Tienda POO — E-Commerce con Flask

Proyecto final de Programación Orientada a Objetos · UTB 2025  
**Autores:** José Tinoco Acosta T00068324 · Jesús Pájaro García T00068185  
**Profesor:** Lila López Gaviria

---

## Requisitos previos

- [Python 3.10 o superior](https://www.python.org/downloads/) — al instalarlo, marca la opción **"Add Python to PATH"**
- [Git](https://git-scm.com/downloads) (opcional, solo si vas a clonar el repo)

Verifica que estén instalados abriendo una terminal y ejecutando:

```
python --version
pip --version
```

---

## Cómo correr el proyecto localmente

### 1. Obtener el código

**Opción A — Con Git:**
```
git clone https://github.com/TheJesuz/tienda-poo.git
cd tienda-poo
```

**Opción B — Sin Git:**  
Descarga el ZIP desde GitHub (botón verde "Code" → "Download ZIP"), descomprímelo y abre la carpeta.

---

### 2. Instalar dependencias

Desde la carpeta raíz del proyecto (donde está `requirements.txt`):

```
pip install -r requirements.txt
```

---

### 3. Correr la aplicación

**Opción A — Servidor web completo (recomendado):**
```
python ecommerce/app.py
```
Luego abre tu navegador en: **http://localhost:5000**

**Opción B — Abrir directo en el navegador (sin servidor):**  
Abre el archivo `ecommerce/static/index.html` haciendo doble clic.  
> En este modo los datos se guardan en tu navegador (localStorage) y no se comparten entre usuarios.

---

## Credenciales de administrador

| Campo | Valor |
|---|---|
| Acceso | Botón "Acceso de administrador" en la pantalla de inicio |
| Contraseña | `admin1234` |

---

## Estructura del proyecto

```
tienda-poo/
├── ecommerce/
│   ├── app.py              ← Servidor Flask (API REST)
│   ├── main.py             ← Menú interactivo por consola
│   ├── modelos/            ← Clases del dominio (POO)
│   ├── servicios/          ← Lógica de negocio y patrones GoF
│   ├── persistencia/       ← Singleton + JSON
│   ├── utils/              ← Excepciones del dominio
│   └── static/
│       └── index.html      ← Frontend completo
├── wsgi.py                 ← Entry point para Render
├── requirements.txt
├── Procfile
└── render.yaml
```

---

## Posibles problemas

**"python no se reconoce como comando"**  
→ Python no está en el PATH. Reinstálalo marcando "Add Python to PATH" o usa `python3` en lugar de `python`.

**"pip no se reconoce como comando"**  
→ Usa `python -m pip install -r requirements.txt` en su lugar.

**El puerto 5000 ya está en uso**  
→ Cambia el puerto: `python ecommerce/app.py` y edita la última línea de `app.py` a `port=5001`.

**Los datos se borran al reiniciar el servidor**  
→ Es normal en el despliegue online (Render gratuito usa filesystem efímero). Localmente los datos persisten en `datos_tienda.json`.
