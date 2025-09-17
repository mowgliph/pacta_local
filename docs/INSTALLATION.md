# Instalación

Para instalar y configurar PACTA, sigue los siguientes pasos:

## 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd pacta_local
```

## 2. Crear un entorno virtual

```bash
python -m venv venv
venv\Scripts\activate  # En Windows
# source venv/bin/activate  # En macOS/Linux
```

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 4. Ejecutar la aplicación

```bash
set FLASK_APP=app.py
set FLASK_ENV=development
flask run
```

La aplicación estará disponible en: **http://127.0.0.1:5000**