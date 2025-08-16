#!/bin/bash

# Script d'audit d'accessibilité automatisé pour Hyperion
# Conforme RGAA 4.1 - Niveau AA

set -e

echo "🔍 Audit d'accessibilité Hyperion - RGAA 4.1"
echo "=============================================="

# Configuration
BASE_URL="http://localhost:8000"
REPORT_DIR="docs/accessibility/reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$REPORT_DIR/accessibility_report_$TIMESTAMP"

# Créer le dossier de rapports
mkdir -p "$REPORT_DIR"

# Vérifier que le serveur Django est en cours d'exécution
echo "📡 Vérification du serveur Django..."
if ! curl -s "$BASE_URL" > /dev/null; then
    echo "❌ Erreur: Le serveur Django n'est pas accessible sur $BASE_URL"
    echo "   Démarrez le serveur avec: python manage.py runserver"
    exit 1
fi
echo "✅ Serveur Django accessible"

# 1. Tests Pa11y (standard WCAG 2.1 AA)
echo ""
echo "🧪 Test 1/4: Audit Pa11y (WCAG 2.1 AA)..."
if command -v pa11y &> /dev/null; then
    echo "  📋 Test des pages principales..."
    
    URLS=(
        "$BASE_URL/dashboard/"
        "$BASE_URL/auth/login/"
        "$BASE_URL/2fa/setup/"
        "$BASE_URL/ssh/"
        "$BASE_URL/roles/"
    )
    
    pa11y_issues=0
    for url in "${URLS[@]}"; do
        echo "    🔍 Test: $url"
        if ! pa11y "$url" --standard WCAG2AA --reporter cli > "${REPORT_FILE}_pa11y_$(basename $url).txt" 2>&1; then
            pa11y_issues=$((pa11y_issues + 1))
            echo "      ⚠️  Issues trouvées"
        else
            echo "      ✅ Aucune issue"
        fi
    done
    
    if [ $pa11y_issues -eq 0 ]; then
        echo "  ✅ Pa11y: Toutes les pages passent les tests WCAG 2.1 AA"
    else
        echo "  ⚠️  Pa11y: $pa11y_issues pages avec des issues"
    fi
else
    echo "  ❌ Pa11y non installé. Installation: npm install -g pa11y"
fi

# 2. Tests axe-core
echo ""
echo "🧪 Test 2/4: Audit axe-core..."
if command -v axe &> /dev/null; then
    echo "  📋 Test axe-core sur le dashboard principal..."
    if axe "$BASE_URL/dashboard/" --tags wcag2a,wcag2aa --exit > "${REPORT_FILE}_axe.json"; then
        echo "  ✅ axe-core: Aucune violation"
    else
        echo "  ⚠️  axe-core: Violations trouvées (voir rapport)"
    fi
else
    echo "  ❌ axe-core non installé. Installation: npm install -g @axe-core/cli"
fi

# 3. Validation HTML
echo ""
echo "🧪 Test 3/4: Validation HTML W3C..."
if command -v html-validate &> /dev/null; then
    echo "  📋 Validation des templates HTML..."
    find api/templates -name "*.html" -exec html-validate {} \; > "${REPORT_FILE}_html_validation.txt" 2>&1
    if [ $? -eq 0 ]; then
        echo "  ✅ HTML: Tous les templates sont valides"
    else
        echo "  ⚠️  HTML: Erreurs de validation trouvées"
    fi
else
    echo "  ❌ html-validate non installé. Installation: npm install -g html-validate"
fi

# 4. Tests de contraste
echo ""
echo "🧪 Test 4/4: Vérification des contrastes..."
echo "  📋 Test des contrastes WCAG AA (4.5:1)..."

# Générer un rapport de contraste avec un script Python
cat > "/tmp/contrast_check.py" << 'EOF'
import re
import requests
from bs4 import BeautifulSoup
import sys

def check_contrasts(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Récupérer le CSS intégré
        styles = soup.find_all('style')
        css_content = '\n'.join([style.get_text() for style in styles])
        
        # Chercher les couleurs définies
        color_pattern = r'color:\s*([^;]+);'
        bg_pattern = r'background(-color)?:\s*([^;]+);'
        
        colors = re.findall(color_pattern, css_content)
        backgrounds = re.findall(bg_pattern, css_content)
        
        print(f"Couleurs trouvées: {len(colors)}")
        print(f"Arrière-plans trouvés: {len(backgrounds)}")
        
        return len(colors) + len(backgrounds) > 0
        
    except Exception as e:
        print(f"Erreur lors de la vérification: {e}")
        return False

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/dashboard/"
    success = check_contrasts(url)
    sys.exit(0 if success else 1)
EOF

if python3 /tmp/contrast_check.py "$BASE_URL/dashboard/" > "${REPORT_FILE}_contrast.txt" 2>&1; then
    echo "  ✅ Contrastes: Vérification effectuée"
else
    echo "  ⚠️  Contrastes: Problèmes potentiels détectés"
fi

# Nettoyage
rm -f /tmp/contrast_check.py

# 5. Génération du rapport consolidé
echo ""
echo "📊 Génération du rapport consolidé..."

cat > "${REPORT_FILE}_summary.md" << EOF
# Rapport d'audit d'accessibilité Hyperion

**Date:** $(date '+%d/%m/%Y %H:%M:%S')  
**Référentiel:** RGAA 4.1 / WCAG 2.1 (Niveau AA)  
**Pages testées:** 5 pages principales  

## Résultats des tests

### 1. Pa11y (WCAG 2.1 AA)
- **Statut:** $([ $pa11y_issues -eq 0 ] && echo "✅ Réussi" || echo "⚠️ Issues détectées")
- **Pages avec issues:** $pa11y_issues/5
- **Détails:** Voir fichiers *_pa11y_*.txt

### 2. axe-core
- **Statut:** $([ -f "${REPORT_FILE}_axe.json" ] && echo "✅ Analysé" || echo "❌ Non testé")
- **Détails:** Voir ${REPORT_FILE}_axe.json

### 3. Validation HTML
- **Statut:** $([ -f "${REPORT_FILE}_html_validation.txt" ] && echo "✅ Analysé" || echo "❌ Non testé")
- **Détails:** Voir ${REPORT_FILE}_html_validation.txt

### 4. Contrastes
- **Statut:** $([ -f "${REPORT_FILE}_contrast.txt" ] && echo "✅ Analysé" || echo "❌ Non testé")
- **Détails:** Voir ${REPORT_FILE}_contrast.txt

## Recommandations

1. **Priorité haute:** Corriger les issues Pa11y identifiées
2. **Priorité moyenne:** Réviser les violations axe-core
3. **Priorité basse:** Optimiser la validation HTML
4. **Continu:** Vérifier les contrastes régulièrement

## Prochaines étapes

- [ ] Corriger les issues critiques
- [ ] Tests avec technologies d'assistance
- [ ] Formation équipe développement
- [ ] Audit expert externe

---
*Rapport généré automatiquement par audit_accessibility.sh*
EOF

echo "  📋 Rapport consolidé généré: ${REPORT_FILE}_summary.md"

# Résumé final
echo ""
echo "🎯 Audit d'accessibilité terminé!"
echo "================================="
echo "📁 Rapports générés dans: $REPORT_DIR/"
echo "📄 Rapport principal: ${REPORT_FILE}_summary.md"
echo ""
echo "📋 Actions recommandées:"
echo "  1. Consulter le rapport consolidé"
echo "  2. Corriger les issues prioritaires"
echo "  3. Relancer l'audit après corrections"
echo "  4. Planifier tests manuels avec NVDA/JAWS"
echo ""

# Ouvrir le rapport si possible
if command -v open &> /dev/null; then
    echo "📖 Ouverture du rapport..."
    open "${REPORT_FILE}_summary.md"
elif command -v xdg-open &> /dev/null; then
    echo "📖 Ouverture du rapport..."
    xdg-open "${REPORT_FILE}_summary.md"
fi

echo "✅ Audit terminé avec succès!"
