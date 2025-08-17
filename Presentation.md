# Présentation Détaillée d'Hyperion - Introduction

## Contexte et Objectifs

### Présentation générale
Hyperion est une solution de monitoring et gestion système complète développée avec Django, destinée à centraliser et simplifier l'administration système.

### Problématiques résolues
1. **Fragmentation des outils**
   - Centralisation des fonctionnalités d'administration
   - Interface unifiée pour le monitoring
   - Gestion centralisée des systèmes

2. **Surveillance en temps réel**
   - Monitoring continu des ressources système
   - Alertes proactives
   - Visualisation des performances

### Public cible
- Administrateurs systèmes
- Équipes DevOps
- Responsables infrastructure

## Stack Technique
Structure du projet visible dans HYPERION.md :

### Backend
```python
# api/views.py
from django.views import View
from rest_framework import viewsets
```

### Technologies clés
1. **Framework principal**
   - Django + Django REST Framework
   - Celery pour les tâches asynchrones
   - Redis comme broker de messages

2. **Infrastructure**
   - Docker pour la conteneurisation
   - WebSockets pour le temps réel
   - Base de données PostgreSQL

### Points forts
1. Architecture modulaire
2. Scalabilité native
3. Sécurité renforcée
4. Interface intuitive

# Fonctionnalités Détaillées d'Hyperion

## 1. Monitoring Système en Temps Réel

### Collecte des Métriques (api/tasks.py)
- **CPU** : 

record_cpu_usage()
  - Utilisation par cœur
  - Température
  - Charge moyenne

- **Mémoire** : 

record_memory_usage()
  - RAM utilisée/disponible
  - Swap
  - Cache

- **Réseau** : 

record_network_usage()
  - Bande passante
  - Paquets envoyés/reçus
  - Erreurs/pertes

- **Stockage** : 

record_storage_usage()
  - Espace disque
  - I/O
  - IOPS

## 2. Gestion Système

### Processus
- Liste des processus actifs
- Contrôle (arrêt, redémarrage)
- Tri et filtrage
- Priorité et ressources

### Services
- État des services
- Démarrage/arrêt
- Configuration
- Journaux

## 3. Sécurité

### Authentification
- 2FA via django-two-factor-auth
- Gestion des rôles
- Journalisation des accès

### Supervision SSH
- Connexion distante sécurisée
- Exécution de commandes
- Transfert de fichiers

## 4. Notifications

### Alertes
- send_slack_notification()
- send_email_notification()
- Seuils personnalisables
- Priorités d'alertes

# Fonctionnement Général d'Hyperion

## 1. Architecture Système

### Services Principaux
L'application nécessite 4 composants principaux qui tournent simultanément:

```bash
# 1. Redis Server - Broker de messages
redis-server

# 2. Celery Worker - Gestion des tâches asynchrones
celery -A hyperion worker --loglevel=info

# 3. Celery Beat - Planification des tâches périodiques
celery -A hyperion beat --loglevel=info

# 4. Django Server - Application web avec Daphne (ASGI)
daphne -b 127.0.0.1 -p 8000 hyperion.asgi:application
```

## 2. Flux de Données

### Collecte des Métriques
- tasks.py contient les tâches Celery qui collectent périodiquement les métriques système
- Les données sont stockées dans une base de données PostgreSQL via models.py
- Celery Beat planifie ces tâches selon une fréquence définie

### Communication en Temps Réel
- consumers.py gère les WebSockets pour la mise à jour en temps réel
- Les clients se connectent via Django Channels
- Les données sont poussées aux clients dès qu'elles sont disponibles

## 3. Interfaces

### Backend API
- views.py définit les endpoints REST
- urls.py gère le routage des requêtes
- Authentification via Django et 2FA

### Frontend
- Interface web responsive dans `templates/`
- Graphiques temps réel avec WebSocket
- Dashboard centralisé