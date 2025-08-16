#!/bin/bash

# Script pour lancer les tests Hyperion avec couverture

echo "🧪 Lancement des tests Hyperion..."

# Activer l'environnement virtuel s'il existe
if [ -d "env" ]; then
    source env/bin/activate
    echo "✅ Environnement virtuel activé"
fi

# Installer coverage si pas présent
pip install coverage pytest-cov > /dev/null 2>&1

# Lancer les tests avec couverture
echo "📊 Exécution des tests avec mesure de couverture..."

# Tests unitaires avec couverture
pytest api/tests.py \
    --cov=api \
    --cov-report=html \
    --cov-report=term \
    --cov-fail-under=80 \
    -v \
    --tb=short

# Vérifier le code de retour
if [ $? -eq 0 ]; then
    echo "✅ Tous les tests sont passés avec succès!"
    echo "📁 Rapport de couverture HTML généré dans : htmlcov/"
else
    echo "❌ Certains tests ont échoué ou la couverture est insuffisante"
    exit 1
fi

# Tests de style et qualité du code (optionnel)
if command -v flake8 &> /dev/null; then
    echo "🔍 Vérification du style de code..."
    flake8 api/ --max-line-length=120 --exclude=migrations,__pycache__
fi

echo "🎉 Tests terminés!"
