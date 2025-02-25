# Contrats d'Interfaces

## 1. API REST

### Métriques Système
```http
GET /api/metrics/cpu/
Description: Obtenir l'utilisation CPU
Réponse: {
    "timestamp": "ISO-8601",
    "usage": float  // pourcentage
}

GET /api/metrics/memory/
Description: Obtenir l'utilisation mémoire
Réponse: {
    "timestamp": "ISO-8601",
    "usage": float  // pourcentage
}

GET /api/metrics/network/
Description: Obtenir les statistiques réseau
Réponse: [{
    "timestamp": "ISO-8601",
    "interface": string,
    "received": int,
    "sent": int
}]

GET /api/metrics/storage/
Description: Obtenir l'utilisation stockage
Réponse: [{
    "timestamp": "ISO-8601",
    "mount_point": string,
    "total": int,
    "used": int,
    "free": int
}]
```

## 2. WebSocket Endpoints

### Métriques en Temps Réel
```python
# URL: ws://server/ws/metrics/

# Messages envoyés par le serveur:
{
    "type": "cpu.update",
    "data": {
        "timestamp": "ISO-8601",
        "usage": float
    }
}

{
    "type": "memory.update",
    "data": {
        "timestamp": "ISO-8601",
        "usage": float
    }
}

{
    "type": "network.update",
    "data": {
        "timestamp": "ISO-8601",
        "interface": string,
        "received": int,
        "sent": int
    }
}
```

### Notifications
```python
# URL: ws://server/ws/notifications/

# Messages envoyés par le serveur:
{
    "type": "notification",
    "data": {
        "timestamp": "ISO-8601",
        "level": string,  # "info", "warning", "error"
        "message": string
    }
}
```

## 3. Tâches Périodiques

Les tâches Celery suivantes sont configurées pour s'exécuter périodiquement:

- `record_cpu_usage()`: Toutes les minutes
- `record_memory_usage()`: Toutes les minutes
- `record_network_usage()`: Toutes les minutes
- `record_storage_usage()`: Sur demande

Les notifications peuvent être déclenchées via:
- `send_slack_notification()`
- `send_email_notification()`

Toutes les données sont persistées dans PostgreSQL via les modèles Django correspondants et les mises à jour en temps réel sont diffusées via WebSocket.