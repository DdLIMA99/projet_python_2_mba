import pandas as pd
from typing import Dict, Any

class StatsService:
    @staticmethod
    def get_overview(df: pd.DataFrame) -> Dict[str, Any]:
        """Route 9 : Statistiques globales avec la vraie colonne isFraud."""
        total_tx = len(df)
        fraud_count = int(df['isFraud'].sum())
        fraud_rate = float(fraud_count / total_tx) if total_tx > 0 else 0.0
        
        # Calcul du montant moyen
        # On nettoie le symbole '$' si présent
        if df['amount'].dtype == object:
             amounts = df['amount'].str.replace('$', '').str.replace(',', '').astype(float)
        else:
             amounts = df['amount']
             
        avg_amount = float(amounts.mean())

        return {
            "total_transactions": total_tx,
            "fraud_count": fraud_count,
            "fraud_rate": round(fraud_rate, 6),
            "avg_amount": round(avg_amount, 2)
        }