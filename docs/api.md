# API Reference Hyperion

## Endpoints REST

### Métriques Système
#### GET /api/system/
Retourne les métriques système actuelles

**Réponse**
```json
{
    "cpu": {
        "usage": 45.2,
        "timestamp": "2024-01-20T15:30:00Z"
    },
    "memory": {
        "total": 16384,
        "used": 8192,
        "percent": 50.0
    }
}
```

### Gestion des Processus
#### GET /api/processes/
Liste tous les processus actifs

**Paramètres**
- `sort`: Tri par (`cpu`, `memory`, `name`)
- `limit`: Nombre maximum de résultats

#### POST /api/processes/{pid}/kill/
Termine un processus spécifique

### WebSocket Events

#### ws/cpu/
```javascript
// Connection
ws = new WebSocket('ws://localhost:8000/ws/cpu/');

// Réception des données
ws.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log('CPU Usage:', data.usage);
};
```

#### ws/memory/
```javascript
// Connection
ws = new WebSocket('ws://localhost:8000/ws/memory/');

// Réception des données
ws.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log('Memory Usage:', data.usage);
};
```

### Notifications

#### POST /api/notifications/slack/
Envoie une notification Slack

**Corps de la requête**
```json
{
    "message": "Alerte CPU > 90%",
    "channel": "#monitoring"
}
```

#### POST /api/notifications/email/
Envoie une notification par email

**Corps de la requête**
```json
{
    "subject": "Alerte Système",
    "message": "Usage mémoire critique",
    "recipients": ["admin@example.com"]
}
```
