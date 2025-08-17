# MANUEL D'UTILISATION - HYPERION

## 1. Connexion

### 1.1 Accès à l'application
- **URL** : http://localhost:8000
- **Page de connexion** : http://localhost:8000/api/auth/login/

### 1.2 Identifiants
**Pour les tests de développement :**
- Utilisateur test : `testuser` / `testpass123`
- Utilisateur 2FA : `testuser2fa` / `testpass123`
- Administrateur : `admin` / `admin123`

> **Note importante** : Ces identifiants sont destinés aux tests uniquement. En production, utilisez des comptes créés via l'interface d'administration Django.

### 1.3 Configuration 2FA (Première connexion)
Si l'authentification à deux facteurs (2FA) est activée pour votre compte :

1. **Configuration initiale :**
   - Après la première connexion, accédez à `/api/2fa/setup/`
   - Scannez le QR code avec une application d'authentification (Google Authenticator, Authy, etc.)
   - Saisissez le code à 6 chiffres généré par l'application

2. **Tokens de sauvegarde :**
   - Consultez `/api/2fa/backup-tokens/` pour obtenir vos codes de récupération
   - Conservez ces tokens en sécurité pour accéder en cas de perte de votre appareil

3. **Gestion 2FA :**
   - Gérez vos paramètres 2FA via `/api/auth/2fa/manage/`

## 2. Dashboard

### 2.1 Vue d'ensemble
Le tableau de bord principal (`/api/dashboard/`) centralise toutes les fonctionnalités de monitoring système.

**Fonctionnalités principales :**
- Monitoring temps réel des ressources système
- Gestion des processus et services
- Navigation dans le système de fichiers
- Supervision réseau
- Terminal SSH intégré

### 2.2 Monitoring système en temps réel

#### Graphiques de performance
Le dashboard affiche des graphiques interactifs pour :
- **CPU** : Utilisation processeur en pourcentage
- **Mémoire** : Consommation RAM en pourcentage  
- **Réseau** : Trafic entrant/sortant par interface

**Mise à jour :** Les données se rafraîchissent automatiquement toutes les minutes via WebSocket.

#### Sélection des métriques
- Utilisez les contrôles pour filtrer les métriques affichées
- Possibilité de zoom et navigation dans l'historique
- Données historiques conservées pour analyse de tendances

### 2.3 Gestion des processus

#### Affichage et filtrage
- **Liste complète** : Tous les processus système avec PID, statut, CPU% et mémoire%
- **Filtre par nom** : Saisissez un nom dans le champ "Filtrer les processus"
- **Tri** : Par CPU, mémoire ou nom de processus

#### Actions disponibles
Sur chaque processus, vous pouvez :
- **Arrêter** : Terminer le processus (avec confirmation)
- **Modifier la priorité** : Ajuster la priorité d'exécution
- **Voir les détails** : Informations complètes du processus

**Permissions requises :** `view_processes` pour la consultation, `manage_processes` pour les actions.

### 2.4 Gestion des services

#### Contrôle des services système
- **Démarrer/Arrêter** : Contrôle des services système
- **Redémarrer** : Redémarrage des services
- **Statut** : Surveillance en temps réel de l'état des services

**Permissions requises :** `view_services` pour la consultation, `manage_services` pour les actions.

### 2.5 Navigation dans les fichiers

#### Explorateur de fichiers intégré
- **Navigation** : Parcourir l'arborescence du système
- **Gestion** : Créer, déplacer, renommer, supprimer des fichiers/dossiers
- **Détails** : Permissions, propriétaire, taille, date de modification
- **Glisser-déposer** : Interface intuitive pour la gestion

**Permissions requises :** `view_files` pour la consultation, `manage_files` pour les modifications.

## 3. Supervision réseau

### 3.1 Interfaces réseau
- **Visualisation** : Liste des interfaces réseau actives
- **Statistiques** : Données reçues/envoyées par interface
- **Monitoring** : Surveillance du trafic en temps réel

### 3.2 Sécurité réseau
> **Information manquante** : Les fonctionnalités de blocage IP/ports nécessitent une vérification de l'implémentation actuelle.

**Permissions requises :** `manage_network` pour les actions réseau.

## 4. Terminal SSH

### 4.1 Accès
- **URL** : `/api/ssh/`
- **Interface** : Terminal web intégré pour connexions SSH distantes

### 4.2 Utilisation
1. Saisissez les paramètres de connexion SSH
2. Établissez la connexion
3. Exécutez vos commandes dans le terminal intégré

**Permissions requises :** `use_shell` pour accéder au terminal SSH.

## 5. Système de rôles et permissions

### 5.1 Permissions disponibles
- `view_processes` : Visualiser les processus système
- `manage_processes` : Gérer les processus système  
- `view_services` : Visualiser les services système
- `manage_services` : Gérer les services système
- `view_files` : Visualiser les fichiers
- `manage_files` : Gérer les fichiers
- `manage_network` : Gérer les paramètres réseau
- `manage_roles` : Gérer les rôles utilisateur
- `manage_users` : Gérer les utilisateurs
- `use_shell` : Utiliser les commandes shell
- `view_analytics` : Visualiser les analyses système

### 5.2 Gestion des rôles
- **URL** : `/api/roles/`
- **Administration** : Création et attribution des rôles
- **Permissions granulaires** : Contrôle précis des accès par fonctionnalité

## 6. Notifications et alertes

### 6.1 Notifications Slack
- **Configuration** : Webhook URL dans les paramètres
- **Endpoint** : `/api/notify/slack/`
- **Usage** : Alertes automatiques sur dépassement de seuils

### 6.2 Notifications Email  
- **Configuration** : SMTP dans les paramètres
- **Endpoint** : `/api/notify/email/`
- **Usage** : Notifications par email des événements critiques

## 7. Administration

### 7.1 Interface d'administration Django
- **URL** : http://localhost:8000/admin/
- **Accès** : Compte superuser requis
- **Fonctionnalités** : Gestion complète des utilisateurs, processus, logs d'audit

### 7.2 Logs d'audit
Toutes les actions sont enregistrées dans les logs d'audit avec :
- Utilisateur
- Action effectuée
- Détails de l'opération  
- Adresse IP
- Horodatage

## 8. Démarrage de l'application

### 8.1 Prérequis
- Python 3.x avec environnement virtuel activé
- Redis server
- PostgreSQL (optionnel, SQLite par défaut)

### 8.2 Commandes de lancement

**Terminal 1 - Redis :**
```bash
redis-server
```

**Terminal 2 - Worker Celery :**
```bash
celery -A hyperion worker --loglevel=info
```

**Terminal 3 - Beat Celery :**
```bash
celery -A hyperion beat --loglevel=info  
```

**Terminal 4 - Serveur Django :**
```bash
daphne -b 127.0.0.1 -p 8000 hyperion.asgi:application
```

## 9. Sécurité

### 9.1 Mesures de sécurité implémentées
- **Rate limiting** : Protection contre les attaques par force brute
- **CSRF Protection** : Protection contre les attaques CSRF
- **Authentification 2FA** : Double authentification optionnelle
- **Audit logging** : Traçabilité complète des actions
- **Validation des entrées** : Validation des données utilisateur
- **Contrôle d'accès** : Système de permissions granulaires

### 9.2 Bonnes pratiques
- Activez le 2FA pour tous les comptes administrateur
- Changez les mots de passe par défaut en production
- Surveillez régulièrement les logs d'audit
- Limitez les permissions aux besoins stricts des utilisateurs

## 10. Dépannage

### 10.1 Problèmes courants
- **Connexion impossible** : Vérifiez que tous les services (Redis, base de données) sont démarrés
- **Graphiques non mis à jour** : Vérifiez le worker Celery et les tâches périodiques
- **Erreurs WebSocket** : Contrôlez la configuration Channels et Redis

### 10.2 Logs système
- **Localisation** : Consultez les logs Django et Celery
- **Niveau de détail** : Ajustez `DEBUG = True` pour plus d'informations en développement

---

**Version du document :** 1.0  
**Dernière mise à jour :** Août 2025  
**Contact support :** [À définir selon l'organisation]

---

> **Note :** Ce manuel est basé sur l'analyse du code source. Certaines fonctionnalités peuvent nécessiter une validation pratique. En cas de divergence entre la documentation et le comportement réel, le test pratique fait référence.
