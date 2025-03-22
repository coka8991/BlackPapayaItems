# Usar la imagen base de Python 3.13.0
FROM python:3.11.9-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y git

WORKDIR /app/scripts

# Copiar el archivo de dependencias al nivel raíz del contenedor
COPY requirements.txt /app/

# Instalar las dependencias especificadas en requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiar todo el contenido del proyecto al contenedor
COPY . /app/

# Exponer el puerto predeterminado de Streamlit (8501)
EXPOSE 8501

# Comando para ejecutar la aplicación con Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]