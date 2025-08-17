# api/secure_serializers.py
"""
Sérializers sécurisés avec validation stricte pour l'API Hyperion
"""
import re
import ipaddress
from rest_framework import serializers
from django.core.validators import RegexValidator
from .models import Process, Service, Network, UserProfile


class SecureIPAddressField(serializers.Field):
    """Champ IP avec validation stricte"""
    
    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError("Adresse IP requise")
        
        data = str(data).strip()
        
        try:
            # Validation avec le module ipaddress
            ip = ipaddress.ip_address(data)
            
            # Interdire les adresses privées pour certaines opérations
            if ip.is_private and hasattr(self, 'allow_private') and not self.allow_private:
                raise serializers.ValidationError("Adresse IP privée non autorisée")
            
            # Interdire les adresses de loopback
            if ip.is_loopback:
                raise serializers.ValidationError("Adresse de loopback non autorisée")
            
            return str(ip)
            
        except ValueError as e:
            raise serializers.ValidationError(f"Format d'adresse IP invalide: {e}")
    
    def to_representation(self, value):
        return str(value)


class SecurePortField(serializers.IntegerField):
    """Champ port avec validation stricte"""
    
    def __init__(self, **kwargs):
        kwargs['min_value'] = kwargs.get('min_value', 1)
        kwargs['max_value'] = kwargs.get('max_value', 65535)
        super().__init__(**kwargs)
    
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        
        # Ports critiques interdits par défaut
        critical_ports = [22, 25, 53, 80, 110, 143, 443, 993, 995, 8000]
        if hasattr(self, 'allow_critical') and not self.allow_critical:
            if value in critical_ports:
                raise serializers.ValidationError(
                    f"Le port {value} est un port critique et ne peut pas être modifié"
                )
        
        return value


class SecureProcessNameField(serializers.CharField):
    """Champ nom de processus avec validation"""
    
    def __init__(self, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 255)
        super().__init__(**kwargs)
    
    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError("Nom de processus requis")
        
        data = str(data).strip()
        
        # Validation des caractères
        if not re.match(r'^[a-zA-Z0-9_\-\.\s]+$', data):
            raise serializers.ValidationError(
                "Le nom ne peut contenir que des lettres, chiffres, tirets, underscores et espaces"
            )
        
        # Longueur minimum
        if len(data) < 2:
            raise serializers.ValidationError("Le nom doit contenir au moins 2 caractères")
        
        return data


class IPBlockSerializer(serializers.Serializer):
    """Sérializer pour bloquer une IP"""
    ip_address = SecureIPAddressField()
    reason = serializers.CharField(max_length=500, required=False, default="")
    duration = serializers.IntegerField(min_value=1, max_value=86400, required=False)  # Max 24h
    
    def validate_reason(self, value):
        if value:
            # Nettoyer et valider la raison
            value = str(value).strip()
            if len(value) > 500:
                raise serializers.ValidationError("La raison ne peut pas dépasser 500 caractères")
            
            # Interdire certains caractères
            if re.search(r'[<>&"\']', value):
                raise serializers.ValidationError("La raison contient des caractères interdits")
        
        return value


class PortBlockSerializer(serializers.Serializer):
    """Sérializer pour bloquer un port"""
    port = SecurePortField()
    protocol = serializers.ChoiceField(choices=['tcp', 'udp'], default='tcp')
    reason = serializers.CharField(max_length=500, required=False, default="")
    
    def validate_protocol(self, value):
        return value.lower()


class ProcessActionSerializer(serializers.Serializer):
    """Sérializer pour les actions sur les processus"""
    ACTION_CHOICES = [
        ('stop', 'Arrêter'),
        ('kill', 'Terminer'),
        ('pause', 'Suspendre'),
        ('resume', 'Reprendre'),
        ('priority', 'Changer priorité')
    ]
    
    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    pid = serializers.IntegerField(min_value=1, max_value=999999)
    priority = serializers.IntegerField(min_value=-20, max_value=19, required=False)
    force = serializers.BooleanField(default=False)
    
    def validate(self, data):
        # Si l'action est de changer la priorité, le champ priority est requis
        if data.get('action') == 'priority' and 'priority' not in data:
            raise serializers.ValidationError({
                'priority': 'La priorité est requise pour cette action'
            })
        
        # Validation des PID critiques
        critical_pids = [1, 2]  # init, kthreadd
        if data.get('pid') in critical_pids and data.get('action') in ['stop', 'kill']:
            raise serializers.ValidationError({
                'pid': 'Impossible d\'arrêter un processus système critique'
            })
        
        return data


class ServiceActionSerializer(serializers.Serializer):
    """Sérializer pour les actions sur les services"""
    ACTION_CHOICES = [
        ('start', 'Démarrer'),
        ('stop', 'Arrêter'),
        ('restart', 'Redémarrer'),
        ('reload', 'Recharger'),
        ('enable', 'Activer'),
        ('disable', 'Désactiver')
    ]
    
    service_name = SecureProcessNameField(max_length=100)
    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    
    def validate_service_name(self, value):
        # Liste des services critiques
        critical_services = ['ssh', 'sshd', 'network', 'systemd']
        if value.lower() in critical_services:
            # Permettre seulement certaines actions sur les services critiques
            action = self.initial_data.get('action')
            if action in ['stop', 'disable']:
                raise serializers.ValidationError(
                    f"Action '{action}' non autorisée sur le service critique '{value}'"
                )
        
        return value


class NetworkInterfaceSerializer(serializers.Serializer):
    """Sérializer pour configurer une interface réseau"""
    interface = serializers.CharField(max_length=50)
    action = serializers.ChoiceField(choices=['up', 'down', 'configure'])
    ip_address = SecureIPAddressField(required=False)
    netmask = serializers.CharField(max_length=15, required=False)
    gateway = SecureIPAddressField(required=False)
    
    def validate_interface(self, value):
        # Validation du nom d'interface
        value = str(value).strip()
        if not re.match(r'^[a-zA-Z0-9]+\d*$', value):
            raise serializers.ValidationError("Nom d'interface invalide")
        
        # Empêcher la désactivation de l'interface active
        if hasattr(self, 'context') and self.context.get('request'):
            if self.initial_data.get('action') == 'down' and value == 'eth0':
                raise serializers.ValidationError(
                    "Impossible de désactiver l'interface réseau principale"
                )
        
        return value
    
    def validate(self, data):
        action = data.get('action')
        
        # Si l'action est 'configure', les paramètres réseau sont requis
        if action == 'configure':
            required_fields = ['ip_address', 'netmask']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({
                        field: f"{field} requis pour la configuration"
                    })
        
        return data


class SecureUserInputSerializer(serializers.Serializer):
    """Sérializer générique pour valider les entrées utilisateur"""
    
    def validate_text_field(self, value, max_length=1000):
        """Validation générique pour les champs texte"""
        if not value:
            return value
        
        value = str(value).strip()
        
        # Longueur
        if len(value) > max_length:
            raise serializers.ValidationError(f"Le texte ne peut pas dépasser {max_length} caractères")
        
        # Caractères dangereux
        dangerous_patterns = [
            r'<script',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe',
            r'<object',
            r'<embed'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise serializers.ValidationError("Le texte contient du contenu potentiellement dangereux")
        
        return value


class SecureShellCommandSerializer(serializers.Serializer):
    """Sérializer pour les commandes shell (avec restrictions sévères)"""
    command = serializers.CharField(max_length=500)
    
    def validate_command(self, value):
        if not value:
            raise serializers.ValidationError("Commande requise")
        
        value = str(value).strip()
        
        # Commandes interdites
        forbidden_commands = [
            'rm', 'rmdir', 'del', 'format', 'fdisk',
            'dd', 'mkfs', 'mount', 'umount',
            'passwd', 'su', 'sudo', 'chmod 777',
            'iptables -F', 'systemctl stop ssh',
            'shutdown', 'reboot', 'halt', 'init 0'
        ]
        
        for cmd in forbidden_commands:
            if cmd in value.lower():
                raise serializers.ValidationError(f"Commande interdite détectée: {cmd}")
        
        # Caractères dangereux
        dangerous_chars = [';', '&&', '||', '|', '>', '>>', '<', '`', '$']
        for char in dangerous_chars:
            if char in value:
                raise serializers.ValidationError(f"Caractère dangereux détecté: {char}")
        
        # Longueur maximum
        if len(value) > 500:
            raise serializers.ValidationError("Commande trop longue")
        
        return value
