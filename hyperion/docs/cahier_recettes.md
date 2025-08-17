# CAHIER DE RECETTES - HYPERION

## Version : 1.0
## Date : 17 août 2025
## Responsable : Équipe Développement Hyperion

---

## 1. Tests Fonctionnels

### Test 1.1 : Authentification Basique
- **Objectif** : Vérifier la connexion utilisateur avec identifiants classiques
- **Prérequis** : 
  - Serveur Hyperion démarré
  - Compte utilisateur créé dans la base de données
  - Base de données accessible
- **Étapes** :
  1. Accéder à `/api/auth/login/`
  2. Entrer identifiants valides (username/password)
  3. Cliquer sur "Se connecter"
  4. Vérifier la redirection
- **Données de test** :
  - Username: `testuser`
  - Password: `testpass123`
- **Résultat attendu** : 
  - Redirection vers `/api/dashboard/`
  - Session créée avec cookie de session
  - Code de statut HTTP 302
- **Résultat obtenu** : [À compléter lors des tests]
- **Statut** : [PASS/FAIL]
- **Commentaires** : _____________

### Test 1.2 : Authentification 2FA (Two-Factor Authentication)
- **Objectif** : Vérifier le processus d'authentification à double facteur
- **Prérequis** : 
  - Utilisateur avec 2FA activé
  - Application TOTP (Google Authenticator, Authy)
  - Secret 2FA configuré
- **Étapes** :
  1. Se connecter avec identifiants valides
  2. Accéder à `/api/2fa/setup/` pour la configuration initiale
  3. Scanner le QR code avec l'application TOTP
  4. Entrer le code à 6 chiffres généré
  5. Valider l'activation du 2FA
  6. Se déconnecter et se reconnecter
  7. Entrer le code TOTP à la demande
- **Données de test** :
  - Username: `testuser2fa`
  - Password: `testpass123`
  - Code TOTP: [Généré par l'app]
- **Résultat attendu** : 
  - QR code affiché correctement
  - 2FA activé avec succès
  - Authentification réussie avec code TOTP
  - Accès aux tokens de sauvegarde générés
- **Résultat obtenu** : [À compléter lors des tests]
- **Statut** : [PASS/FAIL]
- **Commentaires** : _____________

### Test 1.3 : Monitoring CPU en Temps Réel
- **Objectif** : Vérifier l'affichage et la mise à jour du monitoring CPU
- **Prérequis** : 
  - Utilisateur connecté avec permission `view_analytics`
  - WebSocket fonctionnel
  - Tâches Celery actives
- **Étapes** :
  1. Accéder au dashboard `/api/dashboard/`
  2. Vérifier l'affichage du graphique CPU
  3. Lancer une tâche CPU intensive (via htop ou stress)
  4. Observer la mise à jour en temps réel
  5. Vérifier les données historiques
- **Données de test** :
  - Charge CPU artificielle avec `stress --cpu 4 --timeout 30s`
- **Résultat attendu** : 
  - Graphique CPU mis à jour toutes les 5 secondes
  - Valeurs cohérentes avec la charge système réelle
  - Données sauvegardées en base (table CPUUsage)
- **Résultat obtenu** : [À compléter lors des tests]
- **Statut** : [PASS/FAIL]
- **Commentaires** : _____________

### Test 1.4 : Gestion des Processus
- **Objectif** : Vérifier la liste, le détail et la gestion des processus système
- **Prérequis** : 
  - Utilisateur avec permissions `view_processes` et `manage_processes`
  - Processus système en cours d'exécution
- **Étapes** :
  1. Accéder à `/api/processes/`
  2. Vérifier la liste des processus affichée
  3. Filtrer par nom de processus (ex: "python")
  4. Sélectionner un processus non critique
  5. Tenter de terminer le processus (kill)
  6. Vérifier la mise à jour de la liste
- **Données de test** :
  - Processus test créé avec `sleep 300 &`
  - PID du processus à terminer
- **Résultat attendu** : 
  - Liste complète des processus système
  - Filtrage fonctionnel
  - Terminaison de processus réussie
  - Mise à jour immédiate de l'interface
- **Résultat obtenu** : [À compléter lors des tests]
- **Statut** : [PASS/FAIL]
- **Commentaires** : _____________

### Test 1.5 : Gestion des Services Système
- **Objectif** : Vérifier la gestion des services système (start/stop/restart)
- **Prérequis** : 
  - Utilisateur avec permissions `view_services` et `manage_services`
  - Services système disponibles (nginx, ssh, etc.)
  - Droits administrateur si nécessaire
- **Étapes** :
  1. Accéder à `/api/services/`
  2. Lister les services système disponibles
  3. Sélectionner un service non critique (ex: nginx de test)
  4. Arrêter le service
  5. Vérifier le changement de statut
  6. Redémarrer le service
  7. Vérifier le retour au statut "running"
- **Données de test** :
  - Service nginx configuré pour les tests
  - Service ssh (uniquement visualisation)
- **Résultat attendu** : 
  - Liste des services avec statuts corrects
  - Actions start/stop/restart fonctionnelles
  - Messages de confirmation des actions
  - Logs des opérations enregistrés
- **Résultat obtenu** : [À compléter lors des tests]
- **Statut** : [PASS/FAIL]
- **Commentaires** : _____________

### Test 1.6 : WebSocket Temps Réel
- **Objectif** : Vérifier le fonctionnement des mises à jour WebSocket
- **Prérequis** : 
  - Redis server démarré
  - Channels configuré correctement
  - Consumer WebSocket actif
- **Étapes** :
  1. Ouvrir le dashboard dans deux onglets différents
  2. Générer une charge système (CPU/mémoire)
  3. Vérifier la synchronisation entre les onglets
  4. Tester la reconnexion automatique (couper/rétablir réseau)
  5. Vérifier la résilience de la connexion
- **Données de test** :
  - Deux sessions utilisateur simultanées
  - Simulation de perte de connexion réseau
- **Résultat attendu** : 
  - Mises à jour synchronisées entre sessions
  - Reconnexion automatique après coupure
  - Pas de perte de données lors des reconnexions
- **Résultat obtenu** : [À compléter lors des tests]
- **Statut** : [PASS/FAIL]
- **Commentaires** : _____________

### Test 1.7 : Gestion des Fichiers
- **Objectif** : Vérifier l'explorateur de fichiers et les opérations de base
- **Prérequis** : 
  - Utilisateur avec permissions `view_files` et `manage_files`
  - Système de fichiers accessible
  - Droits de lecture/écriture sur répertoire de test
- **Étapes** :
  1. Accéder au gestionnaire de fichiers
  2. Navigator dans l'arborescence
  3. Créer un nouveau dossier
  4. Créer un nouveau fichier
  5. Modifier les permissions d'un fichier
  6. Supprimer un fichier/dossier
  7. Télécharger un fichier
- **Données de test** :
  - Répertoire de test : `/tmp/hyperion_test/`
  - Fichiers de différentes tailles et types
- **Résultat attendu** : 
  - Navigation fluide dans l'arborescence
  - Opérations CRUD fonctionnelles
  - Permissions correctement modifiées
  - Téléchargement sans corruption
- **Résultat obtenu** : [À compléter lors des tests]
- **Statut** : [PASS/FAIL]
- **Commentaires** : _____________

### Test 1.8 : Terminal SSH Intégré
- **Objectif** : Vérifier le fonctionnement du terminal SSH web
- **Prérequis** : 
  - Utilisateur avec permission `use_shell`
  - Serveur SSH cible accessible
  - Clés SSH configurées ou authentification par mot de passe
- **Étapes** :
  1. Accéder à `/api/ssh/`
  2. Se connecter à un serveur distant
  3. Exécuter des commandes simples (`ls`, `pwd`, `whoami`)
  4. Exécuter une commande interactive (`top`, `vim`)
  5. Transférer un fichier (scp intégré)
  6. Fermer la session proprement
- **Données de test** :
  - Serveur SSH de test : `test.example.com`
  - Utilisateur : `testuser`
  - Commandes de base Linux
- **Résultat attendu** : 
  - Connexion SSH établie
  - Commandes exécutées correctement
  - Interface interactive fonctionnelle
  - Transfert de fichiers réussi
- **Résultat obtenu** : [À compléter lors des tests]
- **Statut** : [PASS/FAIL]
- **Commentaires** : _____________

---

## 2. Tests de Performance

### Test 2.1 : Charge CPU Monitoring
- **Objectif** : Vérifier les performances avec 100 connexions simultanées
- **Outils** : Apache JMeter, Artillery.js
- **Configuration de test** :
  - Nombre d'utilisateurs virtuels : 100
  - Durée du test : 10 minutes
  - Ramp-up period : 30 secondes
- **Métriques mesurées** :
  - Temps de réponse moyen
  - Utilisation CPU du serveur
  - Utilisation RAM du serveur
  - Nombre d'erreurs
  - Débit (requêtes/seconde)
- **Seuils acceptables** :
  - Temps de réponse < 2 secondes (95e percentile)
  - CPU serveur < 80%
  - RAM < 85%
  - Taux d'erreur < 1%
- **Résultat obtenu** : [À compléter]
- **Statut** : [PASS/FAIL]

### Test 2.2 : Charge WebSocket
- **Objectif** : Tester la scalabilité des connexions WebSocket
- **Configuration** :
  - 500 connexions WebSocket simultanées
  - Envoi de données toutes les 5 secondes
  - Durée : 15 minutes
- **Métriques** :
  - Latence des messages
  - Perte de messages
  - Consommation mémoire Redis
- **Seuils** :
  - Latence < 500ms
  - Perte de messages < 0.1%
  - Mémoire Redis stable
- **Résultat obtenu** : [À compléter]
- **Statut** : [PASS/FAIL]

### Test 2.3 : Performance Base de Données
- **Objectif** : Vérifier les performances de lecture/écriture BD
- **Configuration** :
  - 1000 insertions simultanées (monitoring data)
  - 500 requêtes de lecture simultanées
- **Métriques** :
  - Temps de réponse des requêtes
  - Utilisation CPU PostgreSQL
  - Verrous de base de données
- **Seuils** :
  - Insertion < 100ms
  - Lecture < 50ms
  - Pas de deadlock
- **Résultat obtenu** : [À compléter]
- **Statut** : [PASS/FAIL]

---

## 3. Tests de Sécurité

### Test 3.1 : Injection SQL
- **Objectif** : Vérifier la protection contre les injections SQL
- **Cas de test** :
  1. Injection dans les paramètres de recherche
  2. Injection dans les formulaires d'authentification
  3. Injection via les APIs REST
- **Payloads de test** :
  ```sql
  ' OR '1'='1
  '; DROP TABLE users; --
  ' UNION SELECT * FROM users --
  ```
- **Résultat attendu** : Toutes les tentatives bloquées
- **Résultat obtenu** : [À compléter]
- **Statut** : [PASS/FAIL]

### Test 3.2 : Cross-Site Scripting (XSS)
- **Objectif** : Vérifier la protection contre les attaques XSS
- **Cas de test** :
  1. XSS stocké dans les profils utilisateur
  2. XSS réfléchi dans les paramètres URL
  3. XSS DOM-based dans le code JavaScript
- **Payloads de test** :
  ```html
  <script>alert('XSS')</script>
  <img src=x onerror=alert('XSS')>
  ';alert('XSS');//
  ```
- **Résultat attendu** : Échappement correct, pas d'exécution de scripts
- **Résultat obtenu** : [À compléter]
- **Statut** : [PASS/FAIL]

### Test 3.3 : Cross-Site Request Forgery (CSRF)
- **Objectif** : Vérifier la protection CSRF sur les actions sensibles
- **Cas de test** :
  1. Changement de mot de passe sans token CSRF
  2. Suppression d'utilisateur via requête GET
  3. Actions administrateur via POST forgé
- **Résultat attendu** : Actions bloquées sans token CSRF valide
- **Résultat obtenu** : [À compléter]
- **Statut** : [PASS/FAIL]

### Test 3.4 : Authentification Forcée (Brute Force)
- **Objectif** : Vérifier les protections contre le brute force
- **Configuration** :
  - 100 tentatives de connexion par minute
  - Différentes adresses IP
  - Comptes utilisateur variés
- **Protections attendues** :
  - Rate limiting activé
  - Verrouillage de compte après N échecs
  - CAPTCHA après X tentatives
- **Résultat obtenu** : [À compléter]
- **Statut** : [PASS/FAIL]

### Test 3.5 : Gestion des Permissions
- **Objectif** : Vérifier l'isolation des droits utilisateur
- **Cas de test** :
  1. Utilisateur simple tentant d'accéder aux fonctions admin
  2. Escalade de privilèges via manipulation de rôles
  3. Accès direct aux URLs protégées
- **Résultat attendu** : Accès refusé (HTTP 403/401)
- **Résultat obtenu** : [À compléter]
- **Statut** : [PASS/FAIL]

---

## 4. Tests d'Interface

### Test 4.1 : Responsive Design
- **Objectif** : Vérifier l'adaptabilité sur différentes résolutions
- **Résolutions testées** :
  - Mobile : 375x667px (iPhone SE)
  - Tablette : 768x1024px (iPad)
  - Desktop : 1920x1080px
  - Ultra-wide : 2560x1440px
- **Éléments testés** :
  - Menu de navigation
  - Graphiques de monitoring
  - Tableaux de données
  - Formulaires
- **Résultat attendu** : Interface utilisable sur toutes résolutions
- **Résultat obtenu** : [À compléter]
- **Statut** : [PASS/FAIL]

### Test 4.2 : Compatibilité Navigateurs
- **Navigateurs testés** :
  - Chrome 118+ (Windows/macOS/Linux)
  - Firefox 119+ (Windows/macOS/Linux)
  - Safari 17+ (macOS)
  - Edge 118+ (Windows)
- **Fonctionnalités critiques** :
  - WebSocket
  - Graphiques en temps réel
  - Téléchargement de fichiers
  - Terminal SSH web
- **Résultat attendu** : Fonctionnement identique sur tous navigateurs
- **Résultat obtenu** : [À compléter]
- **Statut** : [PASS/FAIL]

### Test 4.3 : Mode Sombre
- **Objectif** : Vérifier le thème sombre et la transition
- **Cas de test** :
  1. Activation/désactivation du mode sombre
  2. Persistance du choix utilisateur
  3. Lisibilité des graphiques en mode sombre
  4. Contraste des couleurs conforme WCAG
- **Résultat attendu** : Transition fluide, lisibilité maintenue
- **Résultat obtenu** : [À compléter]
- **Statut** : [PASS/FAIL]

### Test 4.4 : Accessibilité WCAG 2.1
- **Objectif** : Vérifier la conformité aux standards d'accessibilité
- **Tests automatisés** : axe-core, WAVE
- **Tests manuels** :
  - Navigation au clavier uniquement
  - Lecteur d'écran (NVDA/JAWS)
  - Contraste des couleurs
  - Textes alternatifs des images
- **Niveau cible** : AA
- **Résultat obtenu** : [À compléter]
- **Statut** : [PASS/FAIL]

---

## 5. Tests d'Intégration

### Test 5.1 : Intégration Redis
- **Objectif** : Vérifier la communication avec Redis
- **Scénarios** :
  1. Connexion/déconnexion Redis
  2. Stockage/récupération de données de cache
  3. Gestion des channels WebSocket
  4. Failover en cas de panne Redis
- **Résultat attendu** : Communication stable, fallback gracieux
- **Résultat obtenu** : [À compléter]
- **Statut** : [PASS/FAIL]

### Test 5.2 : Intégration Celery
- **Objectif** : Vérifier les tâches asynchrones
- **Scénarios** :
  1. Exécution de tâches périodiques
  2. Gestion des erreurs de tâches
  3. Monitoring des workers Celery
  4. Retry automatique des tâches échouées
- **Résultat attendu** : Tâches exécutées fiablement
- **Résultat obtenu** : [À compléter]
- **Statut** : [PASS/FAIL]

### Test 5.3 : Intégration Base de Données
- **Objectif** : Vérifier la persistance des données
- **Scénarios** :
  1. Migrations de schéma
  2. Sauvegarde/restauration
  3. Intégrité référentielle
  4. Transactions ACID
- **Résultat attendu** : Données cohérentes et persistantes
- **Résultat obtenu** : [À compléter]
- **Statut** : [PASS/FAIL]

---

## 6. Matrice de Traçabilité

| Requirement | Description | Tests Associés | Statut |
|-------------|-------------|---------------|---------|
| REQ-001 | Authentification utilisateur | Test 1.1, 3.4 | [PASS/FAIL] |
| REQ-002 | Authentification 2FA | Test 1.2 | [PASS/FAIL] |
| REQ-003 | Monitoring système temps réel | Test 1.3, 2.1, 2.2 | [PASS/FAIL] |
| REQ-004 | Gestion des processus | Test 1.4, 3.5 | [PASS/FAIL] |
| REQ-005 | Gestion des services | Test 1.5, 3.5 | [PASS/FAIL] |
| REQ-006 | Terminal SSH intégré | Test 1.8 | [PASS/FAIL] |
| REQ-007 | Gestion des fichiers | Test 1.7, 3.2 | [PASS/FAIL] |
| REQ-008 | Interface responsive | Test 4.1, 4.2 | [PASS/FAIL] |
| REQ-009 | Sécurité des données | Test 3.1, 3.2, 3.3 | [PASS/FAIL] |
| REQ-010 | Performance système | Test 2.1, 2.2, 2.3 | [PASS/FAIL] |
| REQ-011 | Accessibilité WCAG | Test 4.4 | [PASS/FAIL] |
| REQ-012 | Intégrations externes | Test 5.1, 5.2, 5.3 | [PASS/FAIL] |

---

## 7. Procédure d'Exécution

### 7.1 Prérequis Environnement de Test
```bash
# Installation des outils de test
pip install pytest selenium beautifulsoup4
npm install -g artillery

# Configuration base de données de test
export DJANGO_SETTINGS_MODULE=hyperion.test_settings
python manage.py migrate --run-syncdb

# Démarrage des services
docker-compose up -d redis postgres
celery -A hyperion worker --loglevel=info &
python manage.py runserver 0.0.0.0:8000
```

### 7.2 Ordre d'Exécution des Tests
1. Tests d'intégration (services externes)
2. Tests fonctionnels (fonctionnalités core)
3. Tests de sécurité
4. Tests de performance
5. Tests d'interface

### 7.3 Critères d'Acceptation
- **Tests Fonctionnels** : 100% PASS
- **Tests de Sécurité** : 100% PASS
- **Tests de Performance** : 95% dans les seuils
- **Tests d'Interface** : 90% PASS (tolérance sur navigateurs legacy)

### 7.4 Rapport Final
- Date d'exécution : ___________
- Responsable : ___________
- Version testée : ___________
- Environnement : ___________
- Résultat global : **[PASS/FAIL]**

---

## 8. Anomalies et Suivi

| ID | Severité | Description | Statut | Assigné | Date |
|----|----------|-------------|---------|---------|------|
| ANO-001 | Critique | [Description] | [Ouvert/Fermé] | [Nom] | [Date] |
| ANO-002 | Majeure | [Description] | [Ouvert/Fermé] | [Nom] | [Date] |
| ANO-003 | Mineure | [Description] | [Ouvert/Fermé] | [Nom] | [Date] |

---

**Signatures :**

Responsable Test : _________________ Date : _________

Responsable Projet : _________________ Date : _________

Responsable Qualité : _________________ Date : _________
