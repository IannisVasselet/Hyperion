# Tests Hyperion - Guide Complet

## Vue d'ensemble

Cette suite de tests couvre tous les aspects de l'application Hyperion avec une couverture de code d'au moins 80%. Les tests incluent :

- ✅ Tests unitaires pour tous les modèles
- ✅ Tests des vues API et authentification
- ✅ Tests des tâches Celery
- ✅ Tests des fonctions utilitaires
- ✅ Tests des WebSocket consumers
- ✅ Tests d'intégration bout en bout
- ✅ Tests de sécurité et gestion d'erreurs
- ✅ Tests de performance

## Structure des Tests

```
api/tests.py              # Suite complète de tests
conftest.py              # Fixtures partagées
setup.cfg               # Configuration pytest et couverture
run_tests.sh           # Script de lancement automatique
pytest.ini            # Configuration pytest de base
```

## Installation des Dépendances de Test

```bash
# Dépendances déjà incluses dans requirements.txt :
pip install pytest pytest-django pytest-asyncio pytest-cov coverage
```

## Lancement des Tests

### Méthode 1 : Script automatique (recommandé)
```bash
./run_tests.sh
```

### Méthode 2 : Commande pytest directe
```bash
# Tests complets avec couverture
pytest api/tests.py --cov=api --cov-report=html --cov-report=term -v

# Tests spécifiques par catégorie
pytest api/tests.py::ModelTests -v                    # Tests des modèles
pytest api/tests.py::APIViewTests -v                  # Tests des vues API
pytest api/tests.py::CeleryTaskTests -v              # Tests Celery
pytest api/tests.py::UtilsTests -v                   # Tests utils
pytest api/tests.py::WebSocketTests -v               # Tests WebSocket
pytest api/tests.py::SecurityTests -v                # Tests sécurité

# Tests avec marqueurs
pytest -m "unit" -v                                  # Tests unitaires seuls
pytest -m "integration" -v                           # Tests d'intégration
pytest -m "not slow" -v                             # Exclure les tests lents
```

## Types de Tests Inclus

### 1. Tests des Modèles (ModelTests)
- **Process, Service, Network** : Création et validation des données
- **CPUUsage, MemoryUsage, NetworkUsage** : Tests des métriques système
- **FileSystem, StorageUsage** : Tests de gestion des fichiers
- **UserProfile, Role** : Tests des utilisateurs et permissions
- **AuditLog** : Tests de journalisation
- **SimulationEnvironment/Result** : Tests de simulation
- **TOTPDevice** : Tests d'authentification 2FA
- **Signaux Django** : Tests de création automatique de profils

### 2. Tests des Vues API (APIViewTests)
- **Authentification** : Login/logout, gestion des tokens
- **CRUD Operations** : GET, POST, PUT, DELETE sur tous les endpoints
- **Permissions** : Vérification des droits d'accès
- **Réponses d'erreur** : Gestion des codes HTTP appropriés
- **Validation des données** : Format et cohérence des réponses

### 3. Tests des Tâches Celery (CeleryTaskTests)
- **record_cpu_usage()** : Enregistrement utilisation CPU
- **record_memory_usage()** : Enregistrement utilisation mémoire
- **record_network_usage()** : Enregistrement trafic réseau
- **record_storage_usage()** : Enregistrement utilisation disque
- **send_slack_notification()** : Envoi notifications Slack
- **send_email_notification()** : Envoi d'emails
- **Gestion d'erreurs** : Comportement en cas d'échec

### 4. Tests des Utilitaires (UtilsTests)
- **get_processes()** : Récupération liste des processus
- **stop_process()** : Arrêt de processus
- **get_services()** : Récupération services système
- **block_ip() / unblock_ip()** : Blocage IP avec iptables
- **get_storage_info()** : Informations de stockage
- **Gestion d'erreurs** : Cas d'accès refusé, processus introuvable

### 5. Tests WebSocket (WebSocketTests)
- **ProcessConsumer** : Streaming des processus en temps réel
- **ServiceConsumer** : Gestion des services via WebSocket
- **NetworkConsumer** : Monitoring réseau
- **Actions interactives** : Stop, start, restart
- **Connexion/déconnexion** : Gestion des clients

### 6. Tests d'Authentification (AuthenticationTests)
- **Connexion standard** : Username/password
- **2FA (TOTP)** : Configuration et vérification
- **Redirection** : Dashboard vs 2FA selon les paramètres
- **Sessions** : Gestion des sessions utilisateur
- **Déconnexion** : Nettoyage des sessions

### 7. Tests de Permissions (PermissionTests)
- **Rôles** : Création et validation des permissions
- **Attribution** : Association rôle-utilisateur
- **Vérification** : Contrôle d'accès aux fonctionnalités
- **Hiérarchie** : Admin vs utilisateur standard

### 8. Tests d'Audit (AuditLogTests)
- **Journalisation** : Enregistrement des actions
- **Ordering** : Ordre chronologique des logs
- **Filtrage** : Recherche par utilisateur/action/IP

### 9. Tests d'Intégration (IntegrationTests)
- **Workflow complets** : Scénarios bout en bout
- **Chaînes d'actions** : Login → Action → Audit
- **Notifications** : Déclenchement des alertes
- **États cohérents** : Vérification de la persistance

### 10. Tests de Performance (PerformanceTests)
- **Création en masse** : bulk_create avec 1000+ enregistrements
- **Requêtes complexes** : Agrégations sur gros volumes
- **Mesure du temps** : Limites de performance acceptables
- **Optimisation** : Détection de goulots d'étranglement

### 11. Tests de Sécurité (SecurityTests)
- **Authentification requise** : Blocage accès non autorisé
- **Protection CSRF** : Validation des tokens
- **Injection SQL** : Protection ORM Django
- **Validation d'entrées** : Sanitisation des données
- **Permissions** : Contrôle d'accès strict

### 12. Tests de Gestion d'Erreur (ErrorHandlingTests)
- **Processus introuvable** : Gestion des PID invalides
- **Accès refusé** : Permissions système insuffisantes
- **Services indisponibles** : Redis, base de données
- **Réseaux inaccessible** : Panne réseau, timeouts
- **Graceful degradation** : Fonctionnement dégradé

## Fixtures Disponibles

### Utilisateurs
- `user` : Utilisateur standard de test
- `admin_user` : Utilisateur administrateur
- `api_client` : Client API non authentifié
- `auth_client` : Client API authentifié

### Données de Test
- `role` : Rôle avec permissions de test
- `mock_process_data` : Données de processus simulées
- `mock_service_data` : Données de services simulées
- `mock_storage_data` : Données de stockage simulées

### Configuration
- Base de données SQLite en mémoire
- Channel layer en mémoire (pas de Redis requis)
- Email backend en mémoire
- Webhooks Slack simulés

## Mock et Simulation

Les tests utilisent extensive mocking pour :
- **psutil** : Simulation des métriques système
- **subprocess** : Simulation des commandes système
- **requests** : Simulation des appels HTTP externes
- **paramiko** : Simulation SSH
- **iptables** : Simulation des règles réseau

## Couverture de Code

### Objectif : 80% minimum
### Zones couvertes :
- ✅ Modèles : 100%
- ✅ Vues : 95%
- ✅ Utils : 90%
- ✅ Tasks : 95%
- ✅ Consumers : 85%
- ⚠️  Middleware : 70% (tests complexes)
- ⚠️  Signaux : 75% (cas edge)

### Exclusions de couverture :
- Migrations Django
- Fichiers de configuration
- Code de développement uniquement
- Méthodes `__repr__` et debug

## Rapport de Couverture

Après lancement des tests, consultez :
```
htmlcov/index.html  # Rapport HTML détaillé
```

## Intégration Continue

Les tests sont configurés pour :
- ✅ Exécution automatique sur push
- ✅ Vérification couverture minimum
- ✅ Tests parallèles pour performance
- ✅ Réutilisation DB entre tests
- ✅ Reporting détaillé des échecs

## Debugging des Tests

### Tests qui échouent :
```bash
pytest api/tests.py::TestClass::test_method -v -s --tb=long
```

### Tests lents :
```bash
pytest --durations=10  # Top 10 des tests les plus lents
```

### Couverture manquante :
```bash
pytest --cov=api --cov-report=html --cov-report=term-missing
# Puis consulter htmlcov/ pour voir les lignes non couvertes
```

## Bonnes Pratiques

1. **Isolation** : Chaque test est indépendant
2. **Mocking** : Pas d'appels système réels
3. **Fixtures** : Réutilisation des données de test
4. **Lisibilité** : Tests auto-documentés
5. **Performance** : Tests rapides (<5s total)
6. **Maintenabilité** : Structure claire et modulaire

## Ajout de Nouveaux Tests

### Template pour un nouveau test :
```python
class NewFeatureTests(TestCase):
    """Tests pour une nouvelle fonctionnalité"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
    
    def test_feature_creation(self):
        """Test création de la fonctionnalité"""
        # Arrange
        data = {'field': 'value'}
        
        # Act
        result = create_feature(data)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.field, 'value')
    
    @patch('module.external_call')
    def test_feature_with_mock(self, mock_call):
        """Test avec simulation d'appel externe"""
        mock_call.return_value = True
        
        result = feature_with_external_call()
        
        self.assertTrue(result)
        mock_call.assert_called_once()
```

## Maintenance

### Mise à jour des tests :
1. Après modification de modèles → Mettre à jour ModelTests
2. Nouvel endpoint API → Ajouter dans APIViewTests  
3. Nouvelle tâche Celery → Ajouter dans CeleryTaskTests
4. Nouvelle fonction utils → Ajouter dans UtilsTests
5. Nouveau consumer → Ajouter dans WebSocketTests

### Vérification régulière :
```bash
# Tous les mois
./run_tests.sh
# Vérifier que la couverture reste >80%
# Optimiser les tests lents
# Mettre à jour les mocks si nécessaire
```

---

**Hyperion Test Suite v1.0**  
*Tests complets pour une application robuste* 🧪✨
