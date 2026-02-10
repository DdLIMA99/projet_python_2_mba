import pandas as pd
import json
import os
from typing import Optional, Dict, Any

class SystemService:
    _data: Optional[pd.DataFrame] = None
    _status: Dict[str, Any] = {"status": "starting", "dataset_loaded": False}

    @classmethod
    def load_dataset(cls):
        """
        Fusionne les transactions et les labels de fraude au démarrage.
        """
        try:
            print("Fusion des données en cours...")
            # 1. Charger les transactions
            transactions_path = "data/transactions_data.csv"
            df_tx = pd.read_csv(transactions_path)
        

            # 2. Charger les labels de fraude (JSON)
            labels_path = "data/train_fraud_labels.json"
            with open(labels_path, 'r') as f:
                labels_data = json.load(f)
            
            # Transformer le JSON en DataFrame
            
        # ... après le chargement du JSON ...
            
            # Transformer le JSON en DataFrame
            df_labels = pd.DataFrame.from_dict(labels_data['target'], orient='index', columns=['isFraud'])
            
            # Conversion : "No" -> 0 et "Yes" -> 1
            # On utilise .map pour traduire les textes en nombres
            df_labels['isFraud'] = df_labels['isFraud'].map({'No': 0, 'Yes': 1, 0: 0, 1: 1})
            
            # On s'assure que l'index est bien un nombre pour la fusion
            df_labels.index = pd.to_numeric(df_labels.index, errors='coerce')
            df_labels = df_labels.dropna(subset=['isFraud']) # On enlève les erreurs éventuelles
            df_labels.index.name = 'id'

            # 3. Fusion (Merge)
            cls._data = df_tx.join(df_labels, how='left')
            cls._data['isFraud'] = cls._data['isFraud'].fillna(0).astype(int)
            
            # ... reste du code ...
            cls._status = {"status": "ok", "dataset_loaded": True}
            print("Fusion réussie ! Colonne 'isFraud' disponible.")
            
        except Exception as e:
            print(f"Erreur lors du chargement : {e}")
            cls._status = {"status": "error", "message": str(e), "dataset_loaded": False}

    @classmethod
    def get_data(cls) -> pd.DataFrame:
        if cls._data is None:
            raise RuntimeError("Le dataset n'est pas chargé.")
        return cls._data

    @classmethod
    def get_health_status(cls) -> Dict[str, Any]:
        return cls._status