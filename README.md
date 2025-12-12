# Orders Analyzer - Vigie Backend Assessment

Outil d'analyse de commandes e-commerce au format JSONL.

## Installation

Python 3.7+ uniquement (bibliothèque standard).

## Usage
```bash
# Analyse basique
python orders_analyzer.py orders.json

# Avec filtre de date
python orders_analyzer.py orders.json -from=2024-11-01

# Tests
python test_orders.py
```

## Note sur le calcul du revenue

**Différence avec l'exemple fourni :**
L'exemple dans le sujet montre un total de 152.94 EUR, mais ma solution calcule 147.95 EUR.

**Ma logique :**
D'après ma compréhension et recherche, il ne fait pas sens d'ajouter les valeurs négatives en omettant simplement le signe "-". On peut soit :
- Les prendre comme valeur de dette (cashback ou retour , .....)
- Ne pas les prendre en considération

Selon la description du cas d'usage fourni, la valeur négative est un **problème**, donc je l'omets complètement du calcul.

**Résultat :**
- Total = 147.95 EUR (pas 152.94 EUR)
- La commande o3 avec -500 cents est exclue du total

## Test de la fonctionnalité de filtrage par date

J'ai ajouté une commande supplémentaire (o9) datée du 2024-10-01 avec un montant très élevé dans `orders.json` pour tester le fitre par date.

**Résultat :**
- Sans filtre : cette commande est incluse
- Avec `-from=2024-11-01` : cette commande est exclue
- Les tests passent dans les deux cas

Cela démontre que le filtrage par date fonctionne correctement.

## Questions Mindset

### 1. Si ce programme tournait en production, que surveiller / logger en priorité ?

**À surveiller :**
- Nombre de commandes suspectes (taux d'anomalies)
- Erreurs de lecture/parsing du fichier
- Temps de traitement
- Revenue total et par marketplace

**À logger :**
- Commandes suspectes avec leurs IDs et raisons
- Erreurs avec numéro de ligne
- Nombre de commandes traitées

### 2. Si le fichier passait de 10 Ko → 10 Go, que changerais-tu dans ton approche ?

**Problème actuel :**
Le programme charge tout le fichier en mémoire.

**Solutions :**
- Traiter ligne par ligne au lieu de tout charger
- Utiliser `multiprocessing` pour traiter plusieurs parties en parallèle
- Ajouter une barre de progression
- Sauvegarder dans une base de données pour les très gros fichiers

### 3. Quel est selon toi le cas de test prioritaire, et pourquoi ?

**`test_mixed_orders_with_date_filter`**

**Pourquoi :**
- Teste plusieurs choses en même temps (date filter, revenue, suspicious orders)
- Plus proche de la réalité : mix de données bonnes et mauvaises
- Vérifie que le filtre de date fonctionne correctement
- Si ce test passe, le programme fonctionne dans la majorité des cas

## Structure
```
.
├── orders_analyzer.py    # Programme principal
├── test_orders.py        # Tests
├── orders.json          # Données exemple
└── README.md            # Ce fichier
```