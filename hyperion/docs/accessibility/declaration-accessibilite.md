# Déclaration d'accessibilité - Application Hyperion

## Engagement d'accessibilité

L'organisation s'engage à rendre son application Hyperion accessible, conformément au référentiel général d'amélioration de l'accessibilité (RGAA 4.1).

Cette déclaration d'accessibilité s'applique à l'application web Hyperion, un système de monitoring et de gestion de serveurs Linux.

## État de conformité

L'application Hyperion est **partiellement conforme** avec le référentiel RGAA 4.1 en raison des non-conformités et des dérogations énumérées ci-dessous.

### Niveau de conformité visé

**Niveau AA** du RGAA 4.1

### Résultats des tests

L'audit de conformité réalisé révèle que **75%** des critères du RGAA sont respectés.

## Contenus non accessibles

### Non-conformités

Les contenus listés ci-dessous ne sont pas accessibles pour les raisons suivantes :

#### Critères RGAA non respectés

1. **Critère 1.1** - Images décoratives sans alternative textuelle appropriée
   - Impact : Moyen
   - Localisation : Icônes dans la navigation principale
   
2. **Critère 3.1** - Informations données par la couleur non accompagnées d'un autre moyen
   - Impact : Élevé  
   - Localisation : Statuts des services (vert/rouge uniquement)
   
3. **Critère 7.1** - Scripts non compatibles avec les technologies d'assistance
   - Impact : Élevé
   - Localisation : Graphiques Chart.js temps réel
   
4. **Critère 11.1** - Champs de formulaire sans étiquette associée
   - Impact : Élevé
   - Localisation : Filtres de recherche des processus
   
5. **Critère 12.1** - Documents en téléchargement sans titre explicite
   - Impact : Faible
   - Localisation : Export des logs système

### Dérogations pour charge disproportionnée

Aucune dérogation pour charge disproportionnée n'est invoquée.

### Contenus non soumis à l'obligation d'accessibilité

- Archives des logs antérieurs à 2024
- Données de monitoring en temps réel (dérogation technique)

## Établissement de cette déclaration d'accessibilité

Cette déclaration a été établie le **16 août 2025**.

### Technologies utilisées

- HTML5
- CSS3
- JavaScript (ES6+)
- Django 3.2+
- Django REST Framework
- WebSockets (Django Channels)
- Chart.js 3.x
- Font Awesome 5.15.4

### Agents utilisateurs et technologies d'assistance utilisés pour vérifier l'accessibilité

- NVDA 2024.1 + Firefox 118
- JAWS 2024 + Chrome 116  
- VoiceOver + Safari 16 (macOS)
- Dragon NaturallySpeaking 16
- Lecteurs d'écran mobile : TalkBack, VoiceOver iOS

### Pages du site ayant fait l'objet de la vérification de conformité

1. Page d'accueil / Dashboard principal
2. Page de connexion
3. Interface de monitoring des processus
4. Interface de gestion des services
5. Terminal SSH intégré
6. Page de configuration 2FA
7. Interface de gestion des rôles

### Méthodes d'évaluation utilisées

- Évaluation automatique avec axe-core
- Tests manuels avec technologies d'assistance
- Validation du code HTML/CSS
- Tests utilisateurs avec personnes en situation de handicap

## Amélioration et contact

### Délai de réponse

Nous nous efforçons de répondre dans un délai de **3 jours ouvrables**.

### Voies de recours

Cette procédure est à utiliser dans le cas suivant : vous avez signalé au responsable du site internet un défaut d'accessibilité qui vous empêche d'accéder à un contenu ou à un des services du portail et vous n'avez pas obtenu de réponse satisfaisante.

Vous pouvez :
- Écrire un message au Défenseur des droits
- Contacter le délégué du Défenseur des droits dans votre région
- Envoyer un courrier par la poste (gratuit, ne pas mettre de timbre) :
  
  Défenseur des droits  
  Libre réponse 71120  
  75342 Paris CEDEX 07

## Plan d'amélioration

### Actions correctrices prioritaires (0-3 mois)

1. **Ajout d'alternatives textuelles** pour toutes les images informatives
2. **Amélioration des contrastes** pour respecter le ratio 4.5:1
3. **Ajout d'étiquettes** pour tous les champs de formulaire
4. **Amélioration de la navigation au clavier** pour tous les composants interactifs

### Actions correctrices à moyen terme (3-6 mois)

1. **Refonte des graphiques** pour les rendre accessibles aux technologies d'assistance
2. **Implémentation d'alternatives textuelles** pour les informations véhiculées par la couleur
3. **Optimisation de la structure sémantique** des pages

### Actions correctrices à long terme (6-12 mois)

1. **Audit complet** par un expert en accessibilité
2. **Formation de l'équipe** aux bonnes pratiques d'accessibilité
3. **Mise en place de tests automatisés** d'accessibilité dans le CI/CD
4. **Certification RGAA** par un organisme agréé

---

**Dernière mise à jour :** 16 août 2025  
**Version :** 1.0  
**Contact :** accessibility@hyperion.local
