# Mi Aplicación Flask

Una aplicación web básica desarrollada con Flask y Python, lista para ser ejecutada en local.

## 📋 Requisitos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)

## 🚀 Instalación y Configuración

### 1. Clonar o descargar el proyecto

```bash
# Si tienes el proyecto en un repositorio
git clone <url-del-repositorio>
cd pacta_local
```

### 2. Crear un entorno virtual (recomendado)

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 🏃‍♂️ Ejecutar la aplicación

### Método 1: Ejecutar directamente

```bash
python app.py
```

### Método 2: Usar Flask CLI

```bash
# Configurar variables de entorno (opcional)
set FLASK_APP=app.py
set FLASK_ENV=development

# Ejecutar la aplicación
flask run
```

La aplicación estará disponible en: **http://127.0.0.1:5000**

## 📁 Estructura del Proyecto

```
pacta_local/
│
├── app.py                 # Aplicación principal Flask
├── requirements.txt       # Dependencias del proyecto
├── README.md             # Este archivo
│
├── templates/            # Plantillas HTML
│   ├── base.html        # Plantilla base
│   ├── index.html       # Página principal
│   └── about.html       # Página "Acerca de"
│
└── static/              # Archivos estáticos
    └── css/
        └── style.css    # Estilos personalizados
```

## 🛠️ Funcionalidades

- ✅ **Página principal**: Interfaz de bienvenida con información sobre Flask
- ✅ **Página "Acerca de"**: Información sobre la aplicación y tecnologías
- ✅ **API REST**: Endpoint de ejemplo en `/api/saludo/<nombre>`
- ✅ **Templates responsivos**: Usando Bootstrap 5
- ✅ **Estilos personalizados**: CSS con animaciones y efectos

## 🌐 Rutas disponibles

- `/` - Página principal
- `/about` - Página "Acerca de"
- `/api/saludo/<nombre>` - API que devuelve un saludo en JSON

## 🔧 Desarrollo

### Agregar nuevas rutas

Edita el archivo `app.py` y agrega nuevas rutas:

```python
@app.route('/nueva-ruta')
def nueva_funcion():
    return render_template('nuevo_template.html')
```

### Agregar nuevos templates

1. Crea un nuevo archivo HTML en la carpeta `templates/`
2. Extiende la plantilla base:

```html
{% extends "base.html" %}

{% block content %}
<!-- Tu contenido aquí -->
{% endblock %}
```

### Agregar estilos CSS

Edita el archivo `static/css/style.css` o crea nuevos archivos CSS en la carpeta `static/`.

## 🐛 Solución de problemas

### Error: "No module named 'flask'"
- Asegúrate de haber activado el entorno virtual
- Instala las dependencias: `pip install -r requirements.txt`

### Error: "Port already in use"
- Cambia el puerto en `app.py`: `app.run(port=5001)`
- O mata el proceso que usa el puerto 5000

### La aplicación no se actualiza
- Asegúrate de que `debug=True` esté configurado en `app.py`
- Reinicia la aplicación

## 📝 Notas adicionales

- La aplicación está configurada en modo debug para desarrollo
- Los archivos estáticos se sirven automáticamente desde la carpeta `static/`
- Las plantillas se cargan desde la carpeta `templates/`
- Para producción, considera usar un servidor WSGI como Gunicorn

## 🤝 Contribuir

1. Haz un fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

---

¡Disfruta desarrollando con Flask! 🐍✨