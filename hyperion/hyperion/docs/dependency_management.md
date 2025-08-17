# PROCESSUS DE GESTION DES DÉPENDANCES

## 1. Fréquence de mise à jour
- Sécurité critique : Immédiat
- Sécurité majeure : Sous 48h
- Mise à jour mineure : Mensuel
- Mise à jour majeure : Trimestriel

## 2. Processus
1. Audit avec `pip-audit`
2. Test en environnement de staging
3. Validation des tests
4. Mise à jour production

## 3. Outils
- Dependabot (GitHub)
- pip-audit pour sécurité
- pip-review pour versions
