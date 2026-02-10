# Utiliser une version légère de Python
FROM python:3.10-slim

# Définir le dossier de travail dans le container
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le reste du projet (le code + les données)
COPY . .

# Exposer le port utilisé par FastAPI
EXPOSE 8000

# Commande pour lancer l'API
CMD ["uvicorn", "src.banking_api.main:app", "--host", "0.0.0.0", "--port", "8000"]