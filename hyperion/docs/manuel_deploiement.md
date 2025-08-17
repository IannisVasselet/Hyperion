# MANUEL DE DÉPLOIEMENT - HYPERION

## Prérequis

### Versions minimales requises
- **Python** : 3.9+ (basé sur le Dockerfile)
- **PostgreSQL** : 13+ 
- **Redis** : 6+
- **Node.js** : 14+ (pour les outils d'accessibilité uniquement)

### Packages système nécessaires
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pip python3-dev python3-venv
sudo apt install postgresql postgresql-contrib
sudo apt install redis-server
sudo apt install nginx
sudo apt install git

# CentOS/RHEL
sudo yum update
sudo yum install python3 python3-pip python3-devel
sudo yum install postgresql postgresql-server postgresql-contrib
sudo yum install redis
sudo yum install nginx
sudo yum install git
```

## Déploiement Production

### 1. Préparation du serveur

#### 1.1 Création de l'utilisateur système
```bash
# Créer un utilisateur dédié pour l'application
sudo useradd -m -s /bin/bash hyperion
sudo usermod -aG sudo hyperion

# Se connecter en tant qu'utilisateur hyperion
sudo su - hyperion
```

#### 1.2 Clonage du projet
```bash
cd /home/hyperion
git clone https://github.com/IannisVasselet/Hyperion.git
cd Hyperion/hyperion
```

#### 1.3 Création de l'environnement virtuel
```bash
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configuration base de données PostgreSQL

#### 2.1 Installation et configuration
```bash
# Démarrer PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Créer la base de données et l'utilisateur
sudo -u postgres psql
```

```sql
-- Dans le shell PostgreSQL
CREATE DATABASE hyperion_db;
CREATE USER hyperion_user WITH PASSWORD 'votre_mot_de_passe_securise';
GRANT ALL PRIVILEGES ON DATABASE hyperion_db TO hyperion_user;
ALTER USER hyperion_user CREATEDB;
\q
```

#### 2.2 Configuration de la connectivité
```bash
# Éditer pg_hba.conf pour autoriser la connexion locale
sudo nano /etc/postgresql/13/main/pg_hba.conf

# Ajouter ou modifier cette ligne :
# local   all             hyperion_user                           md5

# Redémarrer PostgreSQL
sudo systemctl restart postgresql
```

### 3. Configuration Redis

#### 3.1 Installation et démarrage
```bash
# Démarrer Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Vérifier que Redis fonctionne
redis-cli ping
# Doit retourner : PONG
```

#### 3.2 Configuration Redis pour la production
```bash
sudo nano /etc/redis/redis.conf
```

**Modifications recommandées :**
```conf
# Sécurité
bind 127.0.0.1
protected-mode yes
requirepass votre_mot_de_passe_redis

# Performance
maxmemory 256mb
maxmemory-policy allkeys-lru
```

```bash
sudo systemctl restart redis-server
```

### 4. Configuration de l'application

#### 4.1 Variables d'environnement
Créer le fichier `.env` dans le répertoire du projet :

```bash
nano /home/hyperion/Hyperion/hyperion/.env
```

```env
# Configuration Django
SECRET_KEY=votre_cle_secrete_tres_longue_et_aleatoire_ici
DEBUG=False
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com,127.0.0.1

# Base de données
DB_NAME=hyperion_db
DB_USER=hyperion_user
DB_PASSWORD=votre_mot_de_passe_securise
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://:votre_mot_de_passe_redis@127.0.0.1:6379/0

# Email (SMTP)
EMAIL_HOST=smtp.votre-fournisseur.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@domaine.com
EMAIL_HOST_PASSWORD=votre_mot_de_passe_email
DEFAULT_FROM_EMAIL=votre-email@domaine.com

# Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/VOTRE/WEBHOOK/URL
```

#### 4.2 Modification du settings.py pour la production
```bash
nano /home/hyperion/Hyperion/hyperion/hyperion/settings.py
```

**Modifications nécessaires :**

```python
import os
from dotenv import load_dotenv

load_dotenv()

# SÉCURITÉ
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Base de données
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'hyperion_db'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Redis et Celery
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')],
        },
    },
}

# Email
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Sécurité additionnelle
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
```

> **Note importante :** Il faut installer `python-dotenv` : `pip install python-dotenv`

#### 4.3 Préparation de la base de données
```bash
cd /home/hyperion/Hyperion/hyperion
source env/bin/activate

# Migrations
python manage.py makemigrations
python manage.py migrate

# Collecte des fichiers statiques
python manage.py collectstatic --noinput

# Création du superutilisateur
python manage.py createsuperuser
```

### 5. Déploiement avec Docker (Alternative)

#### 5.1 Configuration docker-compose pour production
Créer `docker-compose.prod.yml` :

```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: hyperion_db
      POSTGRES_USER: hyperion_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    restart: unless-stopped

  web:
    build: 
      context: .
      dockerfile: Dockerfile.prod
    command: gunicorn hyperion.wsgi:application --bind 0.0.0.0:8000 --workers 3
    volumes:
      - static_volume:/app/staticfiles
    expose:
      - 8000
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
      - DB_HOST=db
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped

  celery:
    build: .
    command: celery -A hyperion worker --loglevel=info
    volumes:
      - .:/app
    environment:
      - DEBUG=False
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped

  celery-beat:
    build: .
    command: celery -A hyperion beat --loglevel=info
    volumes:
      - .:/app
    environment:
      - DEBUG=False
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - static_volume:/app/staticfiles
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
  static_volume:
```

#### 5.2 Dockerfile pour la production
Créer `Dockerfile.prod` :

```dockerfile
FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn python-dotenv

# Copie du code source
COPY . /app/

# Collecte des fichiers statiques
RUN python manage.py collectstatic --noinput

# Création d'un utilisateur non-root
RUN adduser --disabled-password --gecos '' appuser
USER appuser

EXPOSE 8000

CMD ["gunicorn", "hyperion.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### 6. Configuration Nginx

#### 6.1 Configuration reverse proxy
```bash
sudo nano /etc/nginx/sites-available/hyperion
```

```nginx
upstream hyperion {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name votre-domaine.com www.votre-domaine.com;

    # Configuration SSL (à adapter selon votre certificat)
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Sécurité
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Gestion des fichiers statiques
    location /static/ {
        alias /home/hyperion/Hyperion/hyperion/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # WebSocket pour les updates temps réel
    location /ws/ {
        proxy_pass http://hyperion;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Proxy vers Django
    location / {
        proxy_pass http://hyperion;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Logs
    access_log /var/log/nginx/hyperion_access.log;
    error_log /var/log/nginx/hyperion_error.log;
}
```

#### 6.2 Activation de la configuration
```bash
# Activer le site
sudo ln -s /etc/nginx/sites-available/hyperion /etc/nginx/sites-enabled/

# Tester la configuration
sudo nginx -t

# Redémarrer Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 7. Services systemd

#### 7.1 Service principal Hyperion
```bash
sudo nano /etc/systemd/system/hyperion.service
```

```ini
[Unit]
Description=Hyperion Django App
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=hyperion
Group=hyperion
WorkingDirectory=/home/hyperion/Hyperion/hyperion
Environment=PATH=/home/hyperion/Hyperion/hyperion/env/bin
ExecStart=/home/hyperion/Hyperion/hyperion/env/bin/daphne -b 127.0.0.1 -p 8000 hyperion.asgi:application
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### 7.2 Service Celery Worker
```bash
sudo nano /etc/systemd/system/hyperion-celery.service
```

```ini
[Unit]
Description=Hyperion Celery Worker
After=network.target redis.service

[Service]
Type=exec
User=hyperion
Group=hyperion
WorkingDirectory=/home/hyperion/Hyperion/hyperion
Environment=PATH=/home/hyperion/Hyperion/hyperion/env/bin
ExecStart=/home/hyperion/Hyperion/hyperion/env/bin/celery -A hyperion worker --loglevel=info
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### 7.3 Service Celery Beat
```bash
sudo nano /etc/systemd/system/hyperion-celery-beat.service
```

```ini
[Unit]
Description=Hyperion Celery Beat
After=network.target redis.service

[Service]
Type=exec
User=hyperion
Group=hyperion
WorkingDirectory=/home/hyperion/Hyperion/hyperion
Environment=PATH=/home/hyperion/Hyperion/hyperion/env/bin
ExecStart=/home/hyperion/Hyperion/hyperion/env/bin/celery -A hyperion beat --loglevel=info
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### 7.4 Activation des services
```bash
sudo systemctl daemon-reload
sudo systemctl enable hyperion hyperion-celery hyperion-celery-beat
sudo systemctl start hyperion hyperion-celery hyperion-celery-beat

# Vérification du statut
sudo systemctl status hyperion
sudo systemctl status hyperion-celery
sudo systemctl status hyperion-celery-beat
```

### 8. Sécurisation

#### 8.1 Firewall
```bash
# UFW (Ubuntu)
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# ou iptables
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4
```

#### 8.2 Configuration SSL avec Let's Encrypt
```bash
# Installation Certbot
sudo apt install certbot python3-certbot-nginx

# Obtention du certificat
sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com

# Renouvellement automatique
sudo systemctl enable certbot.timer
```

### 9. Monitoring et logs

#### 9.1 Configuration des logs
```bash
# Rotation des logs Django
sudo nano /etc/logrotate.d/hyperion
```

```logrotate
/home/hyperion/Hyperion/hyperion/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 hyperion hyperion
    postrotate
        systemctl reload hyperion
    endscript
}
```

#### 9.2 Surveillance système
Hyperion inclut son propre système de monitoring, mais pour la surveillance de l'application elle-même :

```bash
# Installation de htop pour le monitoring système
sudo apt install htop

# Surveillance des services
sudo systemctl status hyperion hyperion-celery hyperion-celery-beat
```

### 10. Sauvegarde

#### 10.1 Script de sauvegarde base de données
```bash
sudo nano /home/hyperion/backup_db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/hyperion/backups"
DATE=$(date +"%Y%m%d_%H%M%S")
DB_NAME="hyperion_db"
DB_USER="hyperion_user"

mkdir -p $BACKUP_DIR

# Sauvegarde PostgreSQL
pg_dump -h localhost -U $DB_USER -d $DB_NAME > $BACKUP_DIR/hyperion_db_$DATE.sql

# Nettoyage des sauvegardes anciennes (garde 7 jours)
find $BACKUP_DIR -name "hyperion_db_*.sql" -mtime +7 -delete

echo "Backup completed: hyperion_db_$DATE.sql"
```

```bash
chmod +x /home/hyperion/backup_db.sh

# Crontab pour automatisation
crontab -e
# Ajouter : 0 2 * * * /home/hyperion/backup_db.sh
```

### 11. Dépannage

#### 11.1 Commandes de diagnostic
```bash
# Vérification des services
sudo systemctl status hyperion hyperion-celery hyperion-celery-beat

# Logs des services
sudo journalctl -u hyperion -f
sudo journalctl -u hyperion-celery -f

# Vérification des connexions
sudo ss -tlnp | grep :8000
sudo ss -tlnp | grep :5432
sudo ss -tlnp | grep :6379

# Test de connectivité base de données
sudo -u hyperion psql -h localhost -U hyperion_user -d hyperion_db -c "\dt"

# Test Redis
redis-cli ping
```

#### 11.2 Problèmes courants

**Erreur de connexion à la base de données :**
- Vérifier que PostgreSQL fonctionne
- Contrôler les paramètres de connexion dans `.env`
- Vérifier `pg_hba.conf`

**Problèmes WebSocket :**
- Vérifier que Redis fonctionne
- Contrôler la configuration Nginx pour les WebSockets
- Vérifier les logs de Django Channels

**Problèmes de permissions :**
- Vérifier les permissions sur les fichiers statiques
- Contrôler que l'utilisateur `hyperion` a les droits nécessaires

---

**Version du document :** 1.0  
**Dernière mise à jour :** Août 2025  
**Testé sur :** Ubuntu 20.04 LTS, Ubuntu 22.04 LTS

---
