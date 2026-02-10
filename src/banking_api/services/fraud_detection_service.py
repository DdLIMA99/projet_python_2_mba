import pandas as pd
from typing import Dict, Any, List

class FraudDetectionService:
    @staticmethod
    def get_fraud_summary(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcule le taux de fraude et le score de risque global (Route 13).
        """
        total = len(df)
        fraud_df = df[df['isFraud'] == 1]
        fraud_count = len(fraud_df)
        
        return {
            "total_transactions": total,
            "fraud_incidents": fraud_count,
            "fraud_rate_percentage": round((fraud_count / total) * 100, 4) if total > 0 else 0,
            "risk_level": "High" if (fraud_count / total) > 0.01 else "Low"
        }

    @staticmethod
    def get_latest_frauds(df: pd.DataFrame, limit: int = 5) -> List[Dict[str, Any]]:
        """Récupère les dernières transactions frauduleuses détectées."""
        fraud_df = df[df['isFraud'] == 1].tail(limit)
        return fraud_df.fillna(0).to_dict(orient="records")