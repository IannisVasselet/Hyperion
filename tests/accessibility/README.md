# Tests d'accessibilité Hyperion

Ce dossier contient tous les tests automatisés d'accessibilité pour l'application Hyperion, conformes au référentiel RGAA 4.1.

## 🚀 Démarrage rapide

### Installation des dépendances

```bash
# Installer les outils Node.js d'accessibilité
npm run install:a11y-tools

# Ou individuellement
npm install -g pa11y pa11y-ci @axe-core/cli html-validate lighthouse
```

### Lancer l'audit complet

```bash
# Audit automatisé complet (recommandé)
npm run audit:a11y

# Ou directement avec le script
./scripts/audit_accessibility.sh
```

### Tests spécifiques

```bash
# Tests Jest avec Puppeteer
npm run test:a11y

# Tests Pa11y uniquement  
npm run test:pa11y

# Tests axe-core uniquement
npm run test:axe
```

## 📁 Structure des tests

```
tests/accessibility/
├── setup.js              # Configuration Jest + axe-core
├── dashboard.test.js      # Tests du dashboard principal
├── auth.test.js          # Tests des pages d'authentification
├── forms.test.js         # Tests spécifiques aux formulaires
└── components.test.js    # Tests des composants React/JS
```

## 🎯 Types de tests

### 1. Tests automatisés (Jest + Puppeteer)

Tests complets avec simulation de navigateur :

- **Conformité WCAG 2.1 AA** avec axe-core
- **Navigation au clavier** complète
- **Contraste des couleurs** (ratio 4.5:1)
- **Structure sémantique** HTML
- **Étiquetage des formulaires**
- **Compatibilité technologies d'assistance**

### 2. Tests Pa11y (CLI)

Audit rapide de conformité :

```bash
pa11y http://localhost:8000/dashboard/ --standard WCAG2AA
```

### 3. Tests axe-core (CLI)

Validation des règles WCAG :

```bash
axe http://localhost:8000/dashboard/ --tags wcag2a,wcag2aa
```

### 4. Tests de performance

- **Temps de chargement** pour technologies d'assistance
- **Zoom à 200%** sans perte d'information  
- **Navigation sans souris**
- **Lecteurs d'écran** (simulation)

## 📊 Interprétation des résultats

### Niveaux de conformité

- ✅ **Conforme** : 0 violation
- ⚠️ **Partiellement conforme** : Violations mineures ou moyennes
- ❌ **Non conforme** : Violations critiques

### Types d'impact

- 🔴 **Critical** : Bloque l'accès (à corriger immédiatement)
- 🟡 **Serious** : Gêne significative (à corriger rapidement)  
- 🟠 **Moderate** : Amélioration recommandée
- 🟢 **Minor** : Optimisation possible

### Exemples de violations courantes

```javascript
// Violation : Champ sans étiquette
<input type="text" placeholder="Nom d'utilisateur" />

// Correction
<label for="username">Nom d'utilisateur</label>
<input type="text" id="username" placeholder="Ex: jdupont" />

// Violation : Information par couleur uniquement  
<span style="color: red;">●</span> Service arrêté

// Correction
<span style="color: red;" aria-label="Service arrêté">
  ● Arrêté
</span>
```

## 🔧 Configuration avancée

### Personnaliser les règles axe-core

```javascript
// tests/accessibility/setup.js
const axe = configureAxe({
  rules: {
    'color-contrast': { 
      enabled: true,
      options: { contrastRatio: { normal: 4.5, large: 3.0 } }
    },
    'focus-order-semantics': { enabled: false } // Désactiver si problématique
  }
});
```

### Configuration Pa11y

```json
// .pa11yci
{
  "urls": ["http://localhost:8000/dashboard/"],
  "defaults": {
    "standard": "WCAG2AA", 
    "timeout": 30000,
    "wait": 2000
  },
  "ignore": [
    "WCAG2AA.Principle1.Guideline1_1.1_1_1.H67.2"
  ]
}
```

## 🐛 Debugging

### Tests qui échouent

1. **Vérifier le serveur Django**
   ```bash
   python manage.py runserver 8000
   curl http://localhost:8000/dashboard/
   ```

2. **Mode debug Puppeteer**
   ```javascript
   const browser = await puppeteer.launch({ 
     headless: false, 
     devtools: true 
   });
   ```

3. **Capturer les violations**
   ```javascript
   const results = await axe.analyze();
   console.log('Violations:', results.violations);
   ```

### Problèmes courants

| Erreur | Solution |
|--------|----------|
| `TimeoutError: Navigation timeout` | Augmenter le timeout ou vérifier le serveur |
| `axe-core not found` | `npm install -g @axe-core/cli` |
| `No tests found` | Vérifier le pattern dans `jest.config.js` |
| `WebSocket connection failed` | Normal en mode test, ignoré automatiquement |

## 📈 Intégration CI/CD

### GitHub Actions

```yaml
# .github/workflows/accessibility.yml
- name: Tests d'accessibilité
  run: |
    npm run test:a11y
    npm run audit:a11y
```

### Pre-commit hooks

```bash
# .pre-commit-config.yaml  
- repo: local
  hooks:
    - id: accessibility-check
      name: Vérification accessibilité
      entry: npm run test:a11y
      language: system
```

## 📚 Ressources

### Documentation RGAA

- [RGAA 4.1 officiel](https://www.numerique.gouv.fr/publications/rgaa-accessibilite/)
- [Critères RGAA détaillés](https://accessibilite.numerique.gouv.fr/)
- [Guide d'audit RGAA](https://github.com/DISIC/guide-auditeur)

### Outils recommandés

- [axe DevTools](https://www.deque.com/axe/devtools/) - Extension navigateur
- [WAVE](https://wave.webaim.org/) - Évaluateur web
- [Colour Contrast Analyser](https://www.tpgi.com/color-contrast-checker/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)

### Technologies d'assistance

- [NVDA](https://www.nvaccess.org/) - Lecteur d'écran gratuit
- [JAWS](https://www.freedomscientific.com/products/software/jaws/) - Lecteur professionnel
- [VoiceOver](https://support.apple.com/guide/voiceover/) - macOS/iOS

## 🤝 Contribution

### Ajouter de nouveaux tests

1. Créer un fichier `*.test.js` dans `tests/accessibility/`
2. Suivre la structure des tests existants
3. Utiliser les helpers disponibles dans `setup.js`
4. Documenter les cas de test spécifiques

### Exemple de nouveau test

```javascript
describe('Nouvelle fonctionnalité', () => {
  test('Conformité RGAA', async () => {
    await page.goto('http://localhost:8000/nouvelle-page/');
    
    const results = await new AxePuppeteer(page)
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();
      
    expect(results).toBeAccessible();
  });
});
```

---

**Dernière mise à jour :** 16 août 2025  
**Version des tests :** 1.0  
**Compatibilité :** RGAA 4.1 / WCAG 2.1 AA
