### Structure du Projet

Votre projet Hyperion est structuré de la manière suivante :

```
hyperion/
├── api/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── consumers.py
│   ├── models.py
│   ├── routing.py
│   ├── serializers.py
│   ├── tasks.py
│   ├── tests.py
│   ├── urls.py
│   ├── utils.py
│   ├── views.py
│   └── templates/
│       └── dashboard.html
├── hyperion/
│   ├── __init__.py
│   ├── asgi.py
│   ├── celery.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── env/
    ├── bin/
    ├── include/
    ├── lib/
    └── pyvenv.cfg
```

### Description des Composants

1. **api/** : Contient les applications spécifiques au projet.
   - **consumers.py** : Contient les consommateurs WebSocket pour les mises à jour en temps réel.
   - **models.py** : Définit les modèles de données pour les processus, services, utilisation du CPU, mémoire, réseau, etc.
   - **routing.py** : Définit les routes WebSocket.
   - **serializers.py** : Sérialise les données des modèles pour les API.
   - **tasks.py** : Contient les tâches Celery pour enregistrer les données historiques.
   - **urls.py** : Définit les routes pour les API.
   - **utils.py** : Contient des fonctions utilitaires pour interagir avec le système et exécuter des commandes SSH.
   - **views.py** : Contient les vues pour les API et le tableau de bord.
   - **templates/** : Contient les templates HTML pour le frontend.

2. **hyperion/** : Contient les configurations globales du projet.
   - **asgi.py** : Configuration ASGI pour Django Channels.
   - **celery.py** : Configuration de Celery pour les tâches en arrière-plan.
   - **settings.py** : Configuration des paramètres Django.
   - **urls.py** : Définit les routes globales du projet.
   - **wsgi.py** : Configuration WSGI pour le déploiement.

3. **manage.py** : Script de gestion de Django.

4. **Dockerfile** : Définit l'image Docker pour le projet.

5. **docker-compose.yml** : Définit les services Docker pour le projet.

6. **requirements.txt** : Liste des dépendances Python pour le projet.

7. **env/** : Environnement virtuel Python.

### Commande de lancement en developpement
   
Terminal 1 : Lancer Redis
```bash
redis-server
```
Terminal 2 : Lancer le worker Celery
```bash
celery -A hyperion worker --loglevel=info
```
Terminal 3 : Lancer le beat Celery pour les tâches périodiques
```bash
celery -A hyperion beat --loglevel=info
```
Terminal 4 : Lancer le serveur Django avec Daphne
```bash
daphne -b 127.0.0.1 -p 8000 hyperion.asgi:application
```