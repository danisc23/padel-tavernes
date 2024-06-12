# Usa la imagen base de Python
FROM python:3.12-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requerimientos
COPY pyproject.toml poetry.lock /app/

# Instala Poetry
RUN pip install poetry

# Instala las dependencias del proyecto
RUN poetry install --no-dev

# Copia el código fuente de la aplicación
COPY . /app

# Expone el puerto en el que se ejecutará la aplicación
EXPOSE 8000

# Ejecuta la aplicación Flask
CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0", "--port=8000"]
