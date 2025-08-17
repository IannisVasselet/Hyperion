# Résumé des améliorations de sécurité - API Views

## 🛡️ Mesures de sécurité ajoutées dans `api/views.py`

### 1. **Imports de sécurité**
```python
# Décorateurs de sécurité Django
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.clickjacking import xframe_options_deny
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

# Rate limiting avec fallback
from django_ratelimit.decorators import ratelimit

# Sérializers sécurisés personnalisés
from .secure_serializers import (
    IPBlockSerializer, PortBlockSerializer, ProcessActionSerializer,
    ServiceActionSerializer, NetworkInterfaceSerializer, SecureShellCommandSerializer
)
```

### 2. **Décorateurs de sécurité personnalisés**

#### **Content Security Policy (CSP)**
```python
def csp_headers(func):
    """Ajouter les en-têtes Content Security Policy"""
    # Définit des politiques strictes pour scripts, styles, images, etc.
```

#### **En-têtes de sécurité globaux**
```python
def security_headers(func):
    """Décorateur pour ajouter tous les en-têtes de sécurité"""
    # X-Frame-Options: DENY
    # X-Content-Type-Options: nosniff
    # X-XSS-Protection: 1; mode=block
    # Referrer-Policy: strict-origin-when-cross-origin
    # Permissions-Policy: geolocation=(), microphone=(), camera=()
```

#### **Décorateurs composés**
```python
def secure_view(view_func):
    """Décorateur composite pour sécuriser les vues sensibles"""
    return method_decorator([
        csrf_protect,
        xframe_options_deny,
        never_cache,
        security_headers,
        ratelimit(group='sensitive_view', key='ip', rate='10/m', method='ALL', block=True)
    ], name='dispatch')(view_func)

def secure_api_view(view_func):
    """Décorateur composite pour sécuriser les vues API"""
    return method_decorator([
        csrf_protect,
        never_cache,
        security_headers,
        ratelimit(group='api_view', key='user_or_ip', rate='60/m', method='ALL', block=True)
    ], name='dispatch')(view_func)
```

### 3. **Utilitaires de sécurité**

#### **Obtention IP client sécurisée**
```python
def get_client_ip(request):
    """Obtenir l'IP réelle du client en gérant les proxies"""
```

#### **Journalisation sécurisée**
```python
def log_security_event(user, action, details, ip_address, success=True):
    """Journaliser un événement de sécurité avec gestion d'erreurs"""
```

### 4. **Vues sécurisées avec validation stricte**

#### **LoginAPIView améliorée**
- ✅ Rate limiting : 5 tentatives/min par IP
- ✅ Validation stricte des entrées (longueur, format)
- ✅ Protection CSRF
- ✅ Journalisation complète des tentatives
- ✅ En-têtes de sécurité
- ✅ Vérification compte actif
- ✅ Mise à jour IP dernière connexion

#### **ProcessViewSet sécurisé**
```python
@method_decorator([
    csrf_protect,
    never_cache,
    security_headers,
    ratelimit(group='process_api', key='user', rate='30/m', method='ALL', block=True)
], name='dispatch')
class ProcessViewSet(viewsets.ViewSet):
```

#### **ServiceViewSet sécurisé**
```python
@method_decorator([
    csrf_protect,
    never_cache,
    security_headers,
    ratelimit(group='service_api', key='user', rate='20/m', method='ALL', block=True)
], name='dispatch')
class ServiceViewSet(viewsets.ViewSet):
```

#### **NetworkViewSet sécurisé**
```python
@method_decorator([
    csrf_protect,
    never_cache,
    security_headers,
    ratelimit(group='network_api', key='user', rate='15/m', method='ALL', block=True)
], name='dispatch')
class NetworkViewSet(viewsets.ModelViewSet):
```

### 5. **Actions réseau sécurisées**

#### **Block IP avec validation complète**
- ✅ Sérializer `IPBlockSerializer` avec validation IP
- ✅ Rate limiting : 5/min par utilisateur
- ✅ Permission `manage_network` requise
- ✅ Protection auto-blocage
- ✅ Validation format IP avec `ipaddress`
- ✅ Journalisation complète

#### **Block Port avec validation stricte**
- ✅ Sérializer `PortBlockSerializer` avec validation port/protocole
- ✅ Rate limiting : 5/min par utilisateur
- ✅ Permission `manage_network` requise
- ✅ Protection ports critiques (22, 80, 443, 8000)
- ✅ Validation plage ports (1-65535)
- ✅ Protocoles autorisés : TCP/UDP uniquement

#### **Dashboard sécurisé**
- ✅ Authentification obligatoire (`login_required`)
- ✅ Protection CSRF + XSS + Clickjacking
- ✅ Rate limiting : 60 accès/heure
- ✅ Contrôle d'accès basé sur permissions
- ✅ Limitation données selon rôle utilisateur
- ✅ Journalisation accès + erreurs
- ✅ Gestion d'erreurs sécurisée (pas d'exposition détails)

### 6. **Sérializers sécurisés personnalisés** (fichier séparé)

#### **SecureIPAddressField**
- Validation format IP avec module `ipaddress`
- Blocage adresses privées (configurable)
- Blocage adresses loopback

#### **SecurePortField**
- Validation plage 1-65535
- Protection ports critiques (configurable)

#### **IPBlockSerializer**
- Validation IP + raison + durée
- Nettoyage caractères dangereux
- Limitation longueur texte

#### **PortBlockSerializer**
- Validation port + protocole + raison
- Choix protocole limité (TCP/UDP)

#### **ProcessActionSerializer**
- Actions limitées (stop, kill, pause, resume, priority)
- Validation PID + priorité
- Protection processus système critiques

#### **SecureShellCommandSerializer**
- **Validation ultra-stricte pour commandes shell**
- Blacklist commandes dangereuses (rm, dd, shutdown, etc.)
- Blocage caractères dangereux (;, &&, ||, |, >, <, `, $)
- Limitation longueur commande

### 7. **Configuration Rate Limiting par groupe**

| Groupe | Limite | Clé | Méthodes |
|--------|--------|-----|----------|
| `login` | 5/min | IP | POST |
| `process_api` | 30/min | user | ALL |
| `service_api` | 20/min | user | ALL |
| `network_api` | 15/min | user | ALL |
| `block_ip` | 5/min | user | POST |
| `block_port` | 5/min | user | POST |
| `dashboard` | 60/h | user | GET |

### 8. **En-têtes de sécurité appliqués**

```http
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; ...
```

### 9. **Journalisation de sécurité complète**

Actions loggées automatiquement :
- ✅ Tentatives de connexion (réussies/échouées)
- ✅ Accès aux ressources sensibles
- ✅ Actions de blocage IP/Port
- ✅ Tentatives d'actions interdites
- ✅ Erreurs de validation
- ✅ Accès au dashboard

### 10. **Validation stricte des entrées**

- ✅ Longueur maximum des champs
- ✅ Caractères autorisés (regex)
- ✅ Types de données validés
- ✅ Plages numériques respectées
- ✅ Protection contre injection
- ✅ Nettoyage automatique (strip, escape)

## 🎯 **Résultat final**

### **Sécurité OWASP Top 10 renforcée :**
1. **Injection** → Validation stricte + sérializers sécurisés
2. **Authentification** → Rate limiting + journalisation + 2FA
3. **Exposition données** → Permissions + limitation accès données
4. **XXE** → Validation types contenu + parsers sécurisés
5. **Contrôle accès** → Permissions granulaires + décorateurs
6. **Configuration** → En-têtes sécurité + settings produit
7. **XSS** → CSRF protection + CSP + validation entrées
8. **Désérialisation** → Sérializers Django + validation stricte
9. **Composants** → Dépendances à jour + audits sécurité
10. **Journalisation** → AuditLog complet + monitoring

### **Performance et utilisabilité :**
- Rate limiting intelligent (pas trop restrictif)
- Messages d'erreur clairs mais sécurisés
- Fallback si rate limiting non disponible
- Gestion d'erreurs robuste

### **Maintenabilité :**
- Code modulaire avec décorateurs réutilisables
- Sérializers séparés pour validation
- Configuration centralisée
- Documentation complète
