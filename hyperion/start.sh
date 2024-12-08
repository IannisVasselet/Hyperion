# Script lancement du du worker Celery, du beat Celery et du serveur daphne

source env/bin/activate
# Lancement du worker Celery
celery -A hyperion worker --loglevel=info &
# Lancement du beat Celery
celery -A hyperion beat --loglevel=info &
# Lancement du serveur daphne
daphne -b 127.0.0.1 -p 8000 hyperion.asgi:application