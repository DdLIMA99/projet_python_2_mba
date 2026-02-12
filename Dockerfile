FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sécurité : Création de l'utilisateur d'abord
RUN useradd -m appuser

# CORRECTION : Copie et changement de propriétaire en une seule étape
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.banking_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
