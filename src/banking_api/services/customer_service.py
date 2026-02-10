import pandas as pd
from typing import Dict, Any, List

class CustomerService:
    @staticmethod
    def get_customer_history(df: pd.DataFrame, client_id: int) -> List[Dict[str, Any]]:
        """Récupère toutes les transactions d'un client spécifique."""
        # On filtre par la colonne client_id (vue dans ton dataset)
        customer_df = df[df['client_id'] == client_id].copy()
        return customer_df.fillna(0).to_dict(orient="records")

    @staticmethod
    def get_customer_metrics(df: pd.DataFrame, client_id: int) -> Dict[str, Any]:
        """Calcule le profil de dépense d'un client."""
        customer_df = df[df['client_id'] == client_id]
        
        if customer_df.empty:
            return {}

        # Nettoyage du montant pour le calcul
        amounts = customer_df['amount'].str.replace('$', '').str.replace(',', '').astype(float)
        
        return {
            "client_id": client_id,
            "total_transactions": len(customer_df),
            "total_spent": round(amounts.sum(), 2),
            "avg_transaction": round(amounts.mean(), 2),
            "fraud_detected": int(customer_df['isFraud'].sum())
        }