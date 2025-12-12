# Orders Analyzer - Vigie Backend Assessment

Outil d'analyse de commandes e-commerce au format JSONL.

## Required

Python 3.7+ .

```bash
# Cloner le projet
git clone https://github.com/kiro1973/e-commerce_orders/
cd orders-processor
```

## Usage

```bash
# Analyse basique
python orders_analyzer.py orders.json

# Avec filtre de date
python orders_analyzer.py orders.json -from=2024-11-01

# Tests unitaires
python -m unittest test_orders.py
```

## Note sur le calcul du revenue

**Différence avec l'exemple fourni :**
L'exemple dans le sujet montre un total de 152.94 EUR, mais ma solution calcule 147.95 EUR.

**Ma logique :**
D'après ma compréhension, il ne fait pas sens d'ajouter les valeurs négatives en omettant simplement le signe "-". On peut soit :
- Les traiter comme une dette (cashback, retour, remboursement...)
- Ne pas les prendre en considération

Selon la description du cas d'usage fourni, la valeur négative est identifiée comme un **problème suspect**, donc je l'exclus complètement du calcul du revenue.

**Résultat :**
- Total = 147.95 EUR (et non 152.94 EUR)
- La commande o3 avec -500 cents est exclue du total et marquée comme suspicious

## Questions Mindset

### 1. Si ce programme tournait en production, que surveiller / logger en priorité ?

**Métriques de santé :**
- Taux d'erreurs de parsing JSON (fichiers corrompus)
- Nombre et pourcentage de commandes suspicious
- Distribution du revenue par marketplace (détecter les anomalies)
- Temps de traitement (performance)

**Logs prioritaires :**
- Erreurs de lecture de fichier pour n'importe quel raison
- Commandes avec des montants négatifs très élevés (possibles fraudes)

**Alerting :**
- Si les commandes sont suspicious dépassent un seuil 
- Si le temps de traitement dépasse un seuil

### 2. Si le fichier passait de 10 Ko → 10 Go, que changerais-tu dans ton approche ?

**Problèmes actuels :**
- Tout est chargé en mémoire (risque d'OOM)
- Pas de traitement en streaming

**Solutions :**
- **Streaming line-by-line** : traiter chaque ligne sans tout charger en mémoire
- **Batching** : traiter par chunks de commandes
- **Parallélisation** : utiliser multiprocessing pour diviser le fichier
- **Base de données** : importer dans PostgreSQL/ClickHouse pour l'analyse

**Architecture alternative :**
```
File → Split into Chunks → Parallel Processing → Aggregate Results → Final Output
```

### 3. Quel est selon toi le cas de test prioritaire, et pourquoi ?

**Cas prioritaire : test_mixed_orders_with_date_filter**

**Raisons :**
1. **Couverture complète** : teste plusieurs scénarios en un seul test
   - Commandes valides
   - Commandes suspicious (négatives + empty marketplace)
   - Filtrage par date (feature bonus)

2. **Cas réaliste** : en production, on aura toujours un mix de données valides et invalides



Le test `test_all_suspicious_orders` est utile pour les edge cases, mais le cas mixte est plus proche de la réalité.

## Structure du projet

```
orders-processor/
├── orders.json           # Données de test (JSONL)
├── orders_analyzer.py    # Programme principal
├── test_orders.py        # Tests unitaires
└── README.md             # Cette documentation
```
