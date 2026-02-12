# 🏦 Banking Transactions API - MBA ESG

## 👥 L'Équipe (Groupe)
Ce projet a été réalisé en binôme par :
* **Kodzo LIMA**
* **Cecile EONE**

## 📝 Présentation du Projet
Cette API industrielle a été développée pour traiter et analyser un volume massif de transactions bancaires (**+13 millions de lignes**, ~1.2 Go) avec une latence de réponse optimisée.

Le projet intègre une **fusion de données dynamique** entre des transactions brutes (CSV) et des labels de fraude (JSON).

---

## 🏗️ Architecture & Bonus 
Ce projet respecte les exigences de mise en conformité technique suivantes :

1.  **Swagger UI** : Documentation interactive intégrée.
2.  **Streamlit (PROJET EXTERNE)** : Interface métier séparée pour le monitoring.
    * Lien du dépôt : https://github.com/DdLIMA99/Projet-Streamlit-Banking
3.  **CI/CD (GitHub Actions)** : Pipeline automatisé de vérification du code.
4.  **Docker** : Conteneurisation complète de l'API.

---

## 🚀 Installation et Lancement

### 1. Prérequis
* **Python 3.12+** (Indispensable pour la compatibilité des dépendances).
* Dossier `data/` contenant les sources CSV et JSON.

### 2. Méthode Classique (Local)
1. **Installation** : `pip install -r requirements.txt`
2. **Démarrage** : `uvicorn src.banking_api.main:app --reload`
3. **Accès Swagger** : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 3. Méthode Docker (Bonus 🐳)
1. **Build** : `docker build -t banking-api .`
2. **Lancement** : `docker run -p 8000:8000 banking-api`

---

## 📊 Application Métier (Streamlit)
L'application est hébergée séparément.
* **Lancement** : `streamlit run streamlit_app.py` (L'API doit être active).

---

## 🛠️ Endpoints Principaux
* **Santé** : `GET /api/system/health`
* **Fraude** : `GET /api/fraud/summary`
* **Transactions** : `GET /api/transactions?page=1&limit=10`

---

## 📈 Performance & Validation
* **Volume** : 13 305 915 lignes traitées.
* **Optimisation** : Pré-chargement en mémoire via Singleton Pattern.
