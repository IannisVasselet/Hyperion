# Guide d'Installation d'Hyperion

## Prérequis
### Système
- Python 3.8+
- Redis 6.0+
- Docker et Docker Compose (optionnel)
- Git

### Dépendances Python
Toutes les dépendances sont listées dans [requirements.txt](../requirements.txt) :
- Django 4.x
- Django REST Framework
- Django Channels
- Celery
- psutil
- paramiko

## Installation avec Docker

> ⚠️ **ATTENTION** : Beaucoup des features de l'application ne fonctionnent pas avec Docker car les services sont isolés.


1. Cloner le repository :
```bash
git clone <repository-url>
cd hyperion
```

2. Configurer les variables d'environnement :
```bash
cp .env.example .env
# Éditer .env avec vos paramètres
```

3. Lancer avec Docker Compose :
```bash
docker-compose up -d
```

L'application sera disponible sur `http://localhost:8000` 

## Installation Manuelle (Recommandé)
> ⚠️ **ATTENTION** : Un OS Linux ou macOS est recommandé pour l'installation manuelle. Windows n'est pas officiellement supporté.

1. Créer un environnement virtuel :

```bash
python -m venv env
source env/bin/activate  # Linux/Mac
# ou
.\env\Scripts\activate  # Windows
```

2. Installer les dépendances :

```bash
pip install -r requirements.txt
```

3. Configurer la base de données :
```bash
python manage.py migrate
```

4. Lancer les services (4 terminaux nécessaires) :
```bash
# Terminal 1 : Redis
redis-server

# Terminal 2 : Celery Worker
celery -A hyperion worker --loglevel=info

# Terminal 3 : Celery Beat
celery -A hyperion beat --loglevel=info

# Terminal 4 : Serveur Django
daphne -b 127.0.0.1 -p 8000 hyperion.asgi:application
```
