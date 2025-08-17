# Documentation d'accessibilité Hyperion - Index

## 📋 Vue d'ensemble

Cette documentation complète d'accessibilité pour l'application Hyperion respecte les exigences du **référentiel général d'amélioration de l'accessibilité (RGAA 4.1)** et vise un niveau de conformité **AA**.

## 📁 Structure de la documentation

### 📄 Documents principaux

1. **[Déclaration d'accessibilité](declaration-accessibilite.md)**
   - Engagement d'accessibilité
   - État de conformité (75%)
   - Contenus non accessibles
   - Plan d'amélioration
   - Voies de recours

2. **[Rapport d'audit RGAA 4.1](rapport-audit-rgaa.md)**
   - Résultats détaillés par thématique (13 thématiques)
   - Environnement de test complet
   - 8 pages auditées
   - Recommandations prioritaires

3. **[Guide de mise en conformité](guide-mise-en-conformite.md)**
   - Actions correctrices par priorité
   - Exemples de code corrigé
   - Tests de validation
   - Maintenance continue

4. **[Tests et procédures](tests-procedures.md)**
   - Configuration des outils de test
   - Scripts de tests automatisés
   - Protocoles de tests manuels
   - Intégration CI/CD

## 🎯 Niveau de conformité

| Critère | Statut | Conformité |
|---------|---------|------------|
| **Niveau visé** | AA | 75% |
| **Critères respectés** | 75/106 | ✅ |
| **Impact élevé** | 12 critères | 🔴 |
| **Impact moyen** | 18 critères | 🟡 |
| **Impact faible** | 7 critères | 🟢 |

## 🔧 Technologies utilisées

- **Frontend :** HTML5, CSS3, JavaScript ES6+
- **Framework :** Django 3.2+ avec Django REST Framework  
- **Interface :** WebSockets (Django Channels), Chart.js
- **Styles :** Font Awesome 5.15.4, CSS personnalisé
- **Tests :** axe-core, Pa11y, NVDA, JAWS, VoiceOver

## 🧪 Environnement de test

### Navigateurs testés
- Firefox 118 + NVDA 2024.1 (Windows)
- Chrome 116 + JAWS 2024 (Windows)
- Safari 16 + VoiceOver (macOS)
- Edge 116 + Narrateur (Windows)

### Pages auditées (8/8)
- ✅ Dashboard principal (`/dashboard/`)
- ✅ Authentification (`/auth/login/`)
- ✅ Configuration 2FA (`/2fa/setup/`)
- ✅ Gestion processus (`/dashboard/#processes`)
- ✅ Gestion services (`/dashboard/#services`)
- ✅ Terminal SSH (`/ssh/`)
- ✅ Gestion rôles (`/roles/`)
- ✅ Administration (`/admin/`)

## 🚨 Problèmes prioritaires identifiés

### Critiques (Impact élevé)
1. **Étiquetage formulaires** - Champs sans `<label>` associé
2. **Information par couleur** - Statuts services uniquement visuels
3. **Scripts inaccessibles** - Graphiques Chart.js non compatibles
4. **Gestion erreurs** - Messages non reliés aux champs

### Importantes (Impact moyen)
1. **Structure navigation** - Zones principales non identifiées
2. **Alternatives graphiques** - Pas de descriptions textuelles
3. **Contrôle contenu** - Mises à jour temps réel non annoncées
4. **Navigation clavier** - Composants JS partiellement accessibles

## 📈 Plan d'amélioration

### Phase 1 (0-1 mois) - Critiques
- [x] Audit initial réalisé
- [ ] Corrections étiquetage formulaires
- [ ] Ajout indicateurs textuels statuts
- [ ] Alternatives graphiques temps réel

### Phase 2 (1-3 mois) - Importantes  
- [ ] Restructuration navigation (landmarks)
- [ ] Amélioration composants JavaScript
- [ ] Tests avec technologies d'assistance
- [ ] Formation équipe développement

### Phase 3 (3-6 mois) - Optimisations
- [ ] Audit expert externe
- [ ] Certification RGAA officielle
- [ ] Tests utilisateurs handicapés
- [ ] Automatisation tests CI/CD

## 🔍 Utilisation de la documentation

### Pour les développeurs
1. Consultez le **[Guide de mise en conformité](guide-mise-en-conformite.md)** pour les corrections
2. Utilisez les **[Tests et procédures](tests-procedures.md)** pour valider vos changements
3. Suivez les exemples de code accessibles fournis

### Pour les auditeurs
1. Référez-vous au **[Rapport d'audit](rapport-audit-rgaa.md)** pour l'état détaillé
2. Vérifiez la **[Déclaration d'accessibilité](declaration-accessibilite.md)** pour la conformité

### Pour les managers
1. Consultez la **Déclaration d'accessibilité** pour l'engagement global
2. Suivez le **Plan d'amélioration** pour la roadmap

## 📞 Contact et support

- **Email technique :** dev-accessibility@hyperion.local
- **Responsable accessibilité :** accessibility@hyperion.local  
- **Délai de réponse :** 3 jours ouvrables
- **Prochaine évaluation :** 16 février 2026

## 📚 Ressources externes

### Référentiels
- [RGAA 4.1](https://www.numerique.gouv.fr/publications/rgaa-accessibilite/)
- [WCAG 2.1](https://www.w3.org/WAI/WCAG21/quickref/)
- [WAI-ARIA 1.1](https://www.w3.org/TR/wai-aria-1.1/)

### Outils recommandés
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [WAVE](https://wave.webaim.org/)
- [Pa11y](https://pa11y.org/)
- [Color Contrast Analyser](https://www.tpgi.com/color-contrast-checker/)

### Technologies d'assistance
- [NVDA](https://www.nvaccess.org/) (gratuit)
- [JAWS](https://www.freedomscientific.com/products/software/jaws/)
- [VoiceOver](https://support.apple.com/guide/voiceover/) (macOS/iOS)

---

## 📊 Métriques de conformité

```
Conformité globale : 75%
├── Niveau A       : 85% (34/40 critères)
├── Niveau AA      : 71% (41/58 critères)
└── Niveau AAA     : Non audité

Répartition par impact :
├── 🔴 Bloquant    : 12 critères (11%)
├── 🟡 Gênant      : 18 critères (17%)
└── 🟢 Mineur      : 7 critères (7%)

Pages conformes    : 0/8 (0%)
Pages partielles   : 8/8 (100%)
Pages non-conformes: 0/8 (0%)
```

---

**Documentation établie le :** 16 août 2025  
**Version :** 1.0  
**Conformité RGAA :** 4.1 (Niveau AA visé)  
**Prochaine révision :** 16 novembre 2025
