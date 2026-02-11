from fastapi import FastAPI, Query, HTTPException
from contextlib import asynccontextmanager
from typing import List, Optional
import logging

from .services.system_service import SystemService
from .services.transactions_service import TransactionsService
from .services.fraud_detection_service import FraudDetectionService

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    SystemService.load_dataset()
    yield

app = FastAPI(title="Banking Transactions API", version="1.0.0")

@app.get("/api/system/health")
def health_check():
    return SystemService.get_status()

@app.get("/api/transactions")
def get_transactions(page: int = Query(1, ge=1), limit: int = Query(10, le=100)):
    try:
        df = SystemService.get_data()
        return TransactionsService.get_paginated_transactions(df, page, limit)
    except Exception as e:
        logger.error(f"Erreur transactions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e

@app.get("/api/fraud/summary")
def get_fraud_report():
    try:
        df = SystemService.get_data()
        return FraudDetectionService.get_fraud_summary(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur calcul fraude") from e
