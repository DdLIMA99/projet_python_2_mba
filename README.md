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

1.  **Swagger UI** : Documentation interactive intégrée .
2.  **Streamlit (PROJET EXTERNE)** : Interface métier séparée pour le monitoring .
    * Lien du dépôt séparé : https://github.com/DdLIMA99/Projet-Streamlit-Banking
3.  **CI/CD (GitHub Actions)** : Pipeline automatisé de vérification du code .
4.  **Docker** : Conteneurisation complète de l'API .

---

## 🚀 Installation et Lancement

### 1. Prérequis
* Python 3.10+
* Dossier `data/` contenant : `transactions_data.csv` et `train_fraud_labels.json`.

### 2. Méthode Classique (Local)
1. **Installation des dépendances** : 
   `pip install -r requirements.txt`
2. **Démarrage de l'API** : 
   `uvicorn src.banking_api.main:app --reload`
3. **Accès Swagger** : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 3. Méthode Docker (Bonus 🐳)
Pour isoler l'environnement et garantir le fonctionnement quel que soit l'hôte :
1. **Build de l'image** : `docker build -t banking-api .`
2. **Lancement** : `docker run -p 8000:8000 banking-api`

---

## 📊 Application Métier (Streamlit)
L'application métier est hébergée sur un dépôt séparé pour respecter la consigne de séparation des projets.
* **Lancement** : `streamlit run app_streamlit.py` (nécessite que l'API soit active).

---

## 🛠️ Endpoints Principaux
* **Santé du système** : `GET /api/system/health`
* **Résumé de la Fraude** : `GET /api/fraud/summary`
* **Liste des Transactions** : `GET /api/transactions`

---

## 📈 Performance & Validation
* **Volume** : 13 305 915 lignes traitées.

* **Optimisation** : Temps de réponse rapide grâce au **Singleton Pattern** pour le pré-chargement en mémoire vive (RAM).
