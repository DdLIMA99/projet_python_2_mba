import pandas as pd
from typing import Dict, Any, Optional, List

class TransactionsService:
    """Service pour la consultation et le filtrage des transactions bancaires."""

    @staticmethod
    def get_paginated_transactions(
        df: pd.DataFrame, 
        page: int = 1, 
        limit: int = 10, 
        use_chip: Optional[str] = None
    ) -> Dict[str, Any]:
        """Récupère une liste paginée en nettoyant les valeurs NaN pour le JSON."""
        filtered_df = df
        
        # Filtrage basé sur la colonne réelle 'use_chip'
        if use_chip and 'use_chip' in df.columns:
            filtered_df = df[df['use_chip'] == use_chip]

        start = (page - 1) * limit
        end = start + limit
        
        # Sélection du subset et copie pour modification
        subset_df = filtered_df.iloc[start:end].copy()
        
        # NETTOYAGE CRUCIAL : Correction de l'erreur JSON 'nan'
        if 'zip' in subset_df.columns:
            subset_df['zip'] = subset_df['zip'].fillna(0)
        
        # Remplace tous les NaN restants par None (devient null en JSON)
        subset_df = subset_df.replace({float('nan'): None, pd.NA: None})

        return {
            "page": page,
            "limit": limit,
            "total_results": len(filtered_df),
            "transactions": subset_df.to_dict(orient="records")
        }

    @staticmethod
    def get_transaction_by_id(df: pd.DataFrame, tx_id: int) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'une transaction unique via son index (Route 2)."""
        try:
            if tx_id in df.index:
                transaction = df.loc[tx_id].to_dict()
                # Nettoyage individuel des valeurs pour le JSON
                return {k: (None if pd.isna(v) else v) for k, v in transaction.items()}
            return None
        except Exception:
            return None

    @staticmethod
    def get_unique_chips(df: pd.DataFrame) -> List[str]:
        """Récupère la liste des modes d'utilisation (Swipe, Chip, etc.) (Route 4)."""
        if 'use_chip' in df.columns:
            return df['use_chip'].unique().tolist()
        return []
    
    @staticmethod
    def get_transactions_by_client(df: pd.DataFrame, client_id: int) -> List[Dict[str, Any]]:
        """Récupère l'historique complet d'un client (Correction Erreur 500)."""
        try:
            if 'client_id' in df.columns:
                result = df[df['client_id'] == client_id].copy()
                # Nettoyage ZIP et NaN pour la validité JSON
                if 'zip' in result.columns:
                    result['zip'] = result['zip'].fillna(0)
                return result.replace({float('nan'): None, pd.NA: None}).to_dict(orient="records")
            return []
        except Exception:
            return []

    @staticmethod
    def get_transactions_by_merchant(df: pd.DataFrame, merchant_id: int) -> List[Dict[str, Any]]:
        """Récupère les transactions pour un marchand spécifique (Route 8)."""
        try:
            if 'merchant_id' in df.columns:
                result = df[df['merchant_id'] == merchant_id].copy()
                if 'zip' in result.columns:
                    result['zip'] = result['zip'].fillna(0)
                return result.replace({float('nan'): None, pd.NA: None}).to_dict(orient="records")
            return []
        except Exception:
            return []