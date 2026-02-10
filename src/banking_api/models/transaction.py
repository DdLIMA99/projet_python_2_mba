from pydantic import BaseModel
from typing import Optional, Any

class Transaction(BaseModel):
    id: int
    date: str
    client_id: int
    card_id: int
    amount: Any  # Accepte le format "$-77.00"
    use_chip: str
    merchant_id: int
    merchant_city: str
    merchant_state: Optional[str] = None
    zip: Optional[float] = None
    mcc: int
    errors: Optional[int] = 0
    isFraud: Optional[int] = 0 # Ajouté par ta fusion de données