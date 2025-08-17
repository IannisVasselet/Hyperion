# CHANGELOG - Hyperion

Tous les changements notables de ce projet seront documentés dans ce fichier.
Format basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/)

## [2.1.0] - 2025-08-17

### Ajouté
- Suite de tests unitaires complète avec pytest-django
- Documentation complète d'accessibilité (RGAA 4.1)
- Tests fonctionnels et cahier de recettes
- Documentation de sécurité complète

### Amélioré
- Fonctionnalités d'accessibilité dans toute l'application
- Gestion des fichiers statiques
- Interface utilisateur des templates

### Supprimé
- Script d'audit d'accessibilité automatisé

## [2.0.0] - 2025-03-18

### Ajouté
- Middleware CORS pour les requêtes cross-origin
- Gestion d'authentification basée sur les tokens
- Documentation API pour l'authentification et 2FA
- Vue API de connexion avec réponses JSON

### Sécurité
- Amélioration du middleware d'authentification
- Support des tokens d'authentification

## [1.5.0] - 2025-02-25

### Ajouté
- Documentation API complète pour les métriques système
- Documentation des endpoints WebSocket
- Mise à jour du routage SSH avec regex

## [1.2.0] - 2025-01-18

### Ajouté
- Modèle TOTP device avec migrations
- Mise à jour des URLs API
- Documentation API étendue

## [1.0.0] - 2024-12-10

### Ajouté
- Terminal SSH intégré avec suggestions d'autocomplétion
- Historique des commandes dans le terminal SSH
- Interface SSH améliorée avec coloration syntaxique
- Gestion des processus avec API et authentification
- Support 2FA complet avec TOTP
- Descriptions des fonctionnalités dans les templates
- Navigation et layout améliorés

### Amélioré
- Accessibilité des formulaires
- Structure des templates dashboard et navbar
- Expérience utilisateur du terminal SSH
- Gestion des commandes shell

### Sécurité
- Authentification à deux facteurs (2FA)
- Contrôle d'accès basé sur les rôles
- Audit logging complet
- Vérifications de permissions améliorées

## [0.9.0] - 2024-12-09

### Ajouté
- Configuration de débogage
- Fonctionnalité de déplacement de fichiers
- Modèles d'environnement de simulation
- Interface de gestion des rôles

### Amélioré
- Intervalles de mise à jour périodiques
- Affichage de sortie shell avec formatage
- Layout des tableaux du dashboard
- Consommateur shell pour l'exécution de commandes

## [0.8.0] - 2024-12-08

### Ajouté
- Configuration et gestion 2FA complète
- Contrôle d'accès basé sur les rôles
- Commande de création des profils utilisateur manquants
- Liens 2FA dans le dashboard

## [0.7.0] - 2024-12-05

### Ajouté
- Gestion des fichiers avec support WebSocket
- Opérations sur fichiers (création, suppression, déplacement)
- ShellConsumer pour exécution de commandes WebSocket
- Navigation dans les répertoires avec chemins absolus
- Monitoring mémoire avec support WebSocket
- Monitoring CPU avec support WebSocket

### Amélioré
- Style de sortie shell du dashboard
- Affichage des commandes dans l'intégration WebSocket
- Exécution de commandes dans FileSystemConsumer

## [0.6.0] - 2024-12-04

### Ajouté
- Gestion des processus et services avec support WebSocket
- Fonctionnalités de gestion réseau (blocage IP, ports)
- Configuration des interfaces réseau
- Mises à jour périodiques des données de service

### Amélioré
- Fonctionnalité dashboard avec mises à jour temps réel
- Rendu des tableaux de service avec préservation de position
- Correction des WebSockets

## [0.5.0] - 2024-12-03

### Ajouté
- Vue et template dashboard pour monitoring (CPU, mémoire, réseau)
- Tâches Celery pour monitoring système
- Endpoints de notification
- Configuration Docker mise à jour

### Amélioré
- Templates dashboard pour utiliser JSON pour les données d'usage
- Structure API avec viewsets personnalisés
- Fonctions utilitaires pour lister processus et services

## [0.1.0] - 2024-12-03

### Ajouté
- Configuration initiale du projet Django
- Structure API initiale avec modèles, vues et sérialiseurs
- Routage de base
- Architecture de base du système de monitoring
