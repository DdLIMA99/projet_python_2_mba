from fastapi import FastAPI, Query, HTTPException
from contextlib import asynccontextmanager
from typing import List, Optional

# Imports de tes services
from .services.system_service import SystemService
from .services.transactions_service import TransactionsService
from .services.stats_service import StatsService
from .services.customer_service import CustomerService 
from .services.fraud_detection_service import FraudDetectionService  

# Import du modèle 
from .models.transaction import Transaction

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Performance : Chargement et fusion au démarrage
    print("Chargement du dataset en cours...")
    SystemService.load_dataset()
    print("Dataset chargé et prêt !")
    yield

app = FastAPI(
    title="Banking Transactions API",
    version="1.0.0",
    description="API REST industrielle - Traitement de 13M de transactions",
    lifespan=lifespan
)

# --- ROUTES ADMINISTRATION ---

@app.get("/api/system/health")
def health_check() -> dict:
    """Vérifie si le dataset est bien chargé en mémoire."""
    return SystemService.get_health_status()

# --- ROUTES TRANSACTIONS ---

@app.get("/api/transactions")
def get_transactions(
    page: int = Query(1, ge=1), 
    limit: int = Query(10, le=100), 
    use_chip: Optional[str] = None 
):
    """Liste paginée avec support des colonnes réelles (use_chip)."""
    try:
        df = SystemService.get_data()
        return TransactionsService.get_paginated_transactions(df, page=page, limit=limit, use_chip=use_chip)
    except Exception as e:
        # Capture les erreurs de sérialisation JSON (comme le problème 'zip' NaN)
        raise HTTPException(status_code=500, detail=f"Erreur de données : {str(e)}")

@app.get("/api/transactions/types", response_model=List[str])
def get_transaction_types():
    """Récupère les modes de paiement (Swipe, Chip, Online)."""
    df = SystemService.get_data()
    return TransactionsService.get_unique_chips(df)

@app.get("/api/transactions/{tx_id}")
def get_transaction_details(tx_id: int):
    """Détails d'une transaction unique sécurisée contre les NaN."""
    df = SystemService.get_data()
    result = TransactionsService.get_transaction_by_id(df, tx_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")
    return result

# --- ROUTES ANALYTIQUES ---

@app.get("/api/customers/{client_id}/transactions")
def get_client_transactions(client_id: int):
    """Historique complet filtré par client_id."""
    df = SystemService.get_data()
    return TransactionsService.get_transactions_by_client(df, client_id)

@app.get("/api/fraud/summary")
def get_fraud_report():
    """Rapport de fraude basé sur la fusion CSV/JSON."""
    df = SystemService.get_data()
    return FraudDetectionService.get_fraud_summary(df)