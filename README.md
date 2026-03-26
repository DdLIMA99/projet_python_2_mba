# Banking Transactions API

API REST développée avec **FastAPI** pour exposer les données de transactions bancaires fictives.

---

## Prérequis

- Python 3.12+
- Le fichier CSV du dataset (non versionné) :
  `data/transactions_data.csv`

---

## Installation

```bash
# Cloner le dépôt
git clone <url-du-fork>
cd banking-transactions-api

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Windows : .venv\Scripts\activate

# Installer en mode développement
pip install -e ".[dev]"
```

---

## Lancer l'API

```bash
# Placer le CSV dans data/
# Puis :
TRANSACTIONS_CSV_PATH=data/transactions_data.csv uvicorn banking_api.main:app --reload
```

L'API est disponible sur `http://localhost:8000`  
Documentation Swagger : `http://localhost:8000/docs`

---

## Tests

```bash
# Tests pytest + couverture
pytest --cov=banking_api --cov-report=term-missing -v

# Tests features unittest
python -m unittest discover -s tests/features -p "test_*.py" -v
```

---

## Lint et typage

```bash
flake8 banking_api/ tests/
mypy banking_api/
```

---

## Build du paquet

```bash
# Via python -m build (PEP 517)
python -m build

# Via setuptools (vu en cours)
python setup.py sdist bdist_wheel
```

---

## Docker

```bash
# Build
docker build -t banking-transactions-api .

# Run (en montant le CSV)
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  banking-transactions-api
```

---

## Structure du projet

```
banking-transactions-api/
├── banking_api/
│   ├── __init__.py
│   ├── main.py              # Point d'entrée FastAPI
│   ├── config.py            # Configuration globale
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   ├── routers/
│   │   ├── transactions.py  # Routes 1-8
│   │   ├── stats.py         # Routes 9-12
│   │   ├── fraud.py         # Routes 13-15
│   │   ├── customers.py     # Routes 16-18
│   │   └── system.py        # Routes 19-20
│   └── services/
│       ├── data_loader.py
│       ├── transactions_service.py
│       ├── stats_service.py
│       ├── fraud_detection_service.py
│       ├── customer_service.py
│       └── system_service.py
├── tests/
│   ├── conftest.py           # Fixtures pytest partagées
│   ├── test_routes.py        # Tests unitaires routes (pytest)
│   ├── test_services.py      # Tests unitaires services (pytest)
│   └── features/
│       └── test_features.py  # Tests features (unittest)
├── .github/workflows/ci.yml  # Pipeline CI/CD
├── Dockerfile
├── pyproject.toml
├── setup.py
├── setup.cfg
└── README.md
```

---

## Routes disponibles (20)

| # | Méthode | Route | Description |
|---|---------|-------|-------------|
| 1 | GET | `/api/transactions` | Liste paginée |
| 2 | GET | `/api/transactions/{id}` | Détail par ID |
| 3 | POST | `/api/transactions/search` | Recherche multicritère |
| 4 | GET | `/api/transactions/types` | Types disponibles |
| 5 | GET | `/api/transactions/recent` | N dernières transactions |
| 6 | DELETE | `/api/transactions/{id}` | Suppression (mode test) |
| 7 | GET | `/api/transactions/by-customer/{id}` | Transactions envoyées |
| 8 | GET | `/api/transactions/to-customer/{id}` | Transactions reçues |
| 9 | GET | `/api/stats/overview` | Stats globales |
| 10 | GET | `/api/stats/amount-distribution` | Histogramme montants |
| 11 | GET | `/api/stats/by-type` | Stats par type |
| 12 | GET | `/api/stats/daily` | Volume par step |
| 13 | GET | `/api/fraud/summary` | Résumé fraude |
| 14 | GET | `/api/fraud/by-type` | Fraude par type |
| 15 | POST | `/api/fraud/predict` | Prédiction fraude |
| 16 | GET | `/api/customers` | Liste clients |
| 17 | GET | `/api/customers/{id}` | Profil client |
| 18 | GET | `/api/customers/top` | Top clients |
| 19 | GET | `/api/system/health` | Santé API |
| 20 | GET | `/api/system/metadata` | Métadonnées |
