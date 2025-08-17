# PROCESSUS DE GESTION DES ANOMALIES

## 1. Processus de collecte
- **Canal de remontée** : GitHub Issues / Logs système
- **Outils** : 
  - AuditLog Django (système intégré)
  - Logs Django standard
  - Custom Exception Handler (api/utils.py)
  - Rate limiting et monitoring des tentatives
- **Responsables** : Équipe développement

## 2. Modules système surveillés
- **API** : Authentification, endpoints REST
- **Dashboard** : Interface de gestion principale
- **Authentication** : Système 2FA, login/logout, tokens
- **Monitoring** : CPU, Mémoire, Réseau, Stockage, Processus, Services
- **SSH** : Connexions et commandes distantes
- **Notifications** : Slack webhook, Email SMTP
- **File Management** : Navigation et gestion des fichiers système
- **WebSockets** : Channels Redis pour temps réel

## 3. Environnement technique
- **Framework** : Django 5.1.2
- **Base de données** : PostgreSQL (hyperion_db)
- **Cache/Broker** : Redis (127.0.0.1:6379)
- **Serveur** : Gunicorn
- **WebSockets** : Django Channels
- **Task Queue** : Celery avec django-celery-beat

## 4. Fiche type d'anomalie

### FICHE ANOMALIE #001
- **Date** : [Date au format ISO 8601]
- **Reporté par** : [Utilisateur/Admin/Système]
- **Sévérité** : 
  - Critique (système inaccessible, perte de données)
  - Majeure (fonctionnalité principale indisponible)
  - Mineure (problème cosmétique, performance)
- **Module affecté** : 
  - API / Dashboard / Authentication / Monitoring
  - SSH / Notifications / File Management / WebSockets
- **Type d'erreur** :
  - login / logout / failed_login
  - 2fa_setup / 2fa_disable
  - process_stop / service_control
  - role_created / role_deleted
  - [Autre - préciser]
- **Description** : [Description détaillée du problème]
- **Étapes de reproduction** :
  1. [Étape 1 - avec URL/endpoint si applicable]
  2. [Étape 2 - avec paramètres utilisés]
  3. [Comportement observé]
- **Comportement attendu** : [Résultat attendu selon spécifications]
- **Comportement observé** : [Résultat réel obtenu]
- **Environnement** :
  - OS : [macOS / Linux / Windows]
  - Navigateur : [Chrome / Firefox / Safari + version]
  - Version Django : 5.1.2
  - Base de données : PostgreSQL (hyperion_db)
  - Redis : 127.0.0.1:6379
- **Logs techniques** :
  - AuditLog ID : [ID de l'entrée dans AuditLog si applicable]
  - Exception traceback : [Copier le traceback complet]
  - IP address : [Adresse IP concernée]
  - Timestamp : [Horodatage précis]
- **Screenshots** : [Captures d'écran de l'interface]
- **Analyse technique** :
  - Composant défaillant : [Django view/model/task/middleware]
  - Cause probable : [Analyse du code concerné]
  - Impact utilisateur : [Description de l'impact]
- **Solution proposée** : 
  - Correction code : [Modifications nécessaires]
  - Migration DB : [Si changement base de données requis]
  - Redémarrage services : [Redis/Celery/Gunicorn si nécessaire]
- **Tests à effectuer** :
  - [ ] Tests unitaires (pytest)
  - [ ] Tests d'intégration API
  - [ ] Tests selenium interface
  - [ ] Vérification logs AuditLog
  - [ ] Test en environnement de développement
- **Statut** : Ouvert/En cours/Résolu/Fermé
- **Assigné à** : [Développeur responsable]
- **Date de résolution** : [Date de fermeture]
