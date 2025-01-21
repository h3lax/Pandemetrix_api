# Dockerfile (identique)
FROM python:3.9-slim

WORKDIR /app

# Copier le fichier requirements.txt
COPY ./requirements.txt /app/requirements.txt

# Mettre à jour pip et installer les dépendances
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copier le script Python
COPY ./display_app.py /app/display_app.py

# Commande pour lancer le script Python
CMD ["python", "/app/display_app.py"]

# docker build -t plotly_img .
# docker run -h localhost -p 9008:9000 -d --name plotly_container plotly_img
