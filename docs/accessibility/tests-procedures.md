# Tests d'accessibilité - Procédures et outils

## Configuration de l'environnement de test

### 1. Installation des outils

```bash
# Outils d'audit automatisé
npm install -g pa11y-ci axe-core @axe-core/cli lighthouse

# Extension navigateur
# - axe DevTools (Chrome/Firefox)
# - WAVE Web Accessibility Evaluator
# - Lighthouse (intégré Chrome)

# Outils de test visuel
npm install -D puppeteer jest-puppeteer @axe-core/puppeteer
```

### 2. Configuration Jest pour tests d'accessibilité

```javascript
// jest.config.js
module.exports = {
  preset: 'jest-puppeteer',
  testEnvironment: 'node',
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  testMatch: ['<rootDir>/tests/accessibility/**/*.test.js']
};

// tests/setup.js
const { configureAxe } = require('jest-axe');
const axe = configureAxe({
  rules: {
    // Configuration spécifique RGAA
    'color-contrast': { enabled: true },
    'keyboard-navigation': { enabled: true },
    'focus-order-semantics': { enabled: true }
  }
});

global.axe = axe;
```

## Tests automatisés

### 1. Tests Pa11y pour toutes les pages

```javascript
// tests/accessibility/pa11y.test.js
const pa11y = require('pa11y');

const testUrls = [
  'http://localhost:8000/dashboard/',
  'http://localhost:8000/auth/login/',
  'http://localhost:8000/2fa/setup/',
  'http://localhost:8000/ssh/',
  'http://localhost:8000/roles/'
];

describe('Tests Pa11y RGAA', () => {
  testUrls.forEach(url => {
    test(`Accessibilité de ${url}`, async () => {
      const results = await pa11y(url, {
        standard: 'WCAG2AA',
        timeout: 30000,
        wait: 2000,
        actions: [
          'wait for element #main to be visible'
        ],
        ignore: [
          // Ignorer temporairement les problèmes connus
          'WCAG2AA.Principle1.Guideline1_4.1_4_3.G18.Fail'
        ]
      });
      
      expect(results.issues).toHaveLength(0);
    }, 45000);
  });
});
```

### 2. Tests axe-core avec Puppeteer

```javascript
// tests/accessibility/axe.test.js
const { AxePuppeteer } = require('@axe-core/puppeteer');

describe('Tests axe-core', () => {
  let page;

  beforeAll(async () => {
    page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
  });

  afterAll(async () => {
    await page.close();
  });

  test('Dashboard principal - Conformité WCAG 2.1 AA', async () => {
    await page.goto('http://localhost:8000/dashboard/');
    
    // Attendre le chargement des composants dynamiques
    await page.waitForSelector('#processesTableBody tr', { timeout: 10000 });
    
    const results = await new AxePuppeteer(page)
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze();

    expect(results.violations).toHaveLength(0);
    
    // Log des problèmes pour debugging
    if (results.violations.length > 0) {
      console.log('Violations trouvées:', 
        results.violations.map(v => ({
          id: v.id,
          impact: v.impact,
          description: v.description,
          nodes: v.nodes.length
        }))
      );
    }
  });

  test('Formulaires - Étiquetage et accessibilité', async () => {
    await page.goto('http://localhost:8000/auth/login/');
    
    const results = await new AxePuppeteer(page)
      .withTags(['wcag2a'])
      .include('form')
      .analyze();

    expect(results.violations).toHaveLength(0);
  });

  test('Navigation au clavier', async () => {
    await page.goto('http://localhost:8000/dashboard/');
    
    // Test de navigation par tabulation
    const focusableElements = await page.evaluate(() => {
      const elements = document.querySelectorAll(
        'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      return Array.from(elements).map(el => ({
        tag: el.tagName,
        id: el.id,
        className: el.className
      }));
    });
    
    expect(focusableElements.length).toBeGreaterThan(0);
    
    // Vérifier l'ordre de tabulation
    for (let i = 0; i < Math.min(5, focusableElements.length); i++) {
      await page.keyboard.press('Tab');
      const activeElement = await page.evaluate(() => 
        document.activeElement.tagName
      );
      expect(['A', 'BUTTON', 'INPUT', 'SELECT']).toContain(activeElement);
    }
  });
});
```

### 3. Tests de contraste de couleur

```javascript
// tests/accessibility/color-contrast.test.js
const { chromium } = require('playwright');

describe('Tests de contraste', () => {
  let page;

  beforeAll(async () => {
    const browser = await chromium.launch();
    page = await browser.newPage();
  });

  test('Vérification des contrastes WCAG AA', async () => {
    await page.goto('http://localhost:8000/dashboard/');
    
    // Fonction pour calculer le contraste
    const contrastResults = await page.evaluate(() => {
      const getComputedColor = (element, property) => {
        const style = window.getComputedStyle(element);
        return style.getPropertyValue(property);
      };

      const rgbToHex = (rgb) => {
        const result = rgb.match(/\d+/g);
        return result ? 
          '#' + result.map(x => parseInt(x).toString(16).padStart(2, '0')).join('') 
          : '#000000';
      };

      const calculateLuminance = (hex) => {
        const r = parseInt(hex.substr(1, 2), 16) / 255;
        const g = parseInt(hex.substr(3, 2), 16) / 255;
        const b = parseInt(hex.substr(5, 2), 16) / 255;

        const luminance = (c) => c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);

        return 0.2126 * luminance(r) + 0.7152 * luminance(g) + 0.0722 * luminance(b);
      };

      const calculateContrast = (color1, color2) => {
        const lum1 = calculateLuminance(color1);
        const lum2 = calculateLuminance(color2);
        const lighter = Math.max(lum1, lum2);
        const darker = Math.min(lum1, lum2);
        return (lighter + 0.05) / (darker + 0.05);
      };

      // Éléments à tester
      const textElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, a, button');
      const results = [];

      textElements.forEach(element => {
        const color = getComputedColor(element, 'color');
        const backgroundColor = getComputedColor(element, 'background-color');
        
        if (color && backgroundColor && color !== 'rgba(0, 0, 0, 0)' && backgroundColor !== 'rgba(0, 0, 0, 0)') {
          const colorHex = rgbToHex(color);
          const bgColorHex = rgbToHex(backgroundColor);
          const contrast = calculateContrast(colorHex, bgColorHex);
          
          results.push({
            element: element.tagName + (element.className ? '.' + element.className.split(' ')[0] : ''),
            color: colorHex,
            backgroundColor: bgColorHex,
            contrast: contrast,
            passAANormal: contrast >= 4.5,
            passAALarge: contrast >= 3.0,
            passAAANormal: contrast >= 7.0
          });
        }
      });

      return results;
    });

    // Vérifications
    const failingElements = contrastResults.filter(result => !result.passAANormal);
    
    if (failingElements.length > 0) {
      console.log('Éléments avec contraste insuffisant:');
      failingElements.forEach(element => {
        console.log(`${element.element}: ${element.contrast.toFixed(2)} (requis: 4.5)`);
      });
    }

    expect(failingElements).toHaveLength(0);
  });
});
```

## Tests manuels avec technologies d'assistance

### 1. Protocole de test NVDA

```markdown
# Checklist NVDA - Dashboard Hyperion

## Navigation générale
- [ ] Titre de page annoncé correctement
- [ ] Structure des titres cohérente (H1 > H2 > H3)
- [ ] Navigation par landmarks (NVDA+D)
- [ ] Liste des liens accessible (NVDA+F7)
- [ ] Liste des titres accessible (NVDA+F5)

## Tableaux de données
- [ ] En-têtes de tableau annoncés
- [ ] Navigation cellule par cellule (Ctrl+Alt+flèches)
- [ ] Résumé de tableau lu au focus
- [ ] Données chiffrées prononcées correctement

## Formulaires
- [ ] Étiquettes de champs annoncées
- [ ] Champs obligatoires identifiés
- [ ] Messages d'erreur associés aux champs
- [ ] Instructions de saisie données

## Composants interactifs
- [ ] États des boutons annoncés (pressé/non pressé)
- [ ] Popups et modales gérées correctement
- [ ] Changements de contexte annoncés
- [ ] Progression des tâches indiquée
```

### 2. Tests au clavier

```javascript
// Script de test navigation clavier
const keyboardTestScript = {
  // Test complet de navigation
  async runFullKeyboardTest() {
    const page = await browser.newPage();
    await page.goto('http://localhost:8000/dashboard/');
    
    // 1. Navigation séquentielle
    await this.testSequentialNavigation(page);
    
    // 2. Navigation dans les tableaux
    await this.testTableNavigation(page);
    
    // 3. Navigation dans les formulaires
    await this.testFormNavigation(page);
    
    // 4. Raccourcis clavier
    await this.testKeyboardShortcuts(page);
    
    await page.close();
  },

  async testSequentialNavigation(page) {
    let tabIndex = 0;
    const maxTabs = 20;
    
    while (tabIndex < maxTabs) {
      await page.keyboard.press('Tab');
      
      const activeElement = await page.evaluate(() => ({
        tag: document.activeElement.tagName,
        id: document.activeElement.id,
        className: document.activeElement.className,
        visible: document.activeElement.offsetParent !== null
      }));
      
      // Vérifier que l'élément focusé est visible
      expect(activeElement.visible).toBe(true);
      
      tabIndex++;
    }
  },

  async testTableNavigation(page) {
    // Naviguer vers le tableau des processus
    await page.focus('#processesTableBody tr:first-child td:first-child');
    
    // Tester navigation dans le tableau
    const tableNavKeys = ['ArrowDown', 'ArrowUp', 'ArrowLeft', 'ArrowRight'];
    
    for (const key of tableNavKeys) {
      const beforeFocus = await page.evaluate(() => ({
        row: document.activeElement.closest('tr')?.rowIndex,
        cell: document.activeElement.cellIndex
      }));
      
      await page.keyboard.press(key);
      
      const afterFocus = await page.evaluate(() => ({
        row: document.activeElement.closest('tr')?.rowIndex,
        cell: document.activeElement.cellIndex
      }));
      
      // Le focus doit avoir bougé de manière appropriée
      expect(beforeFocus).not.toEqual(afterFocus);
    }
  }
};
```

## Rapports et métriques

### 1. Génération de rapport automatique

```javascript
// scripts/generate-accessibility-report.js
const fs = require('fs');
const pa11y = require('pa11y');
const { AxePuppeteer } = require('@axe-core/puppeteer');

class AccessibilityReporter {
  constructor() {
    this.results = {
      timestamp: new Date().toISOString(),
      pages: [],
      summary: {}
    };
  }

  async generateReport() {
    const urls = [
      'http://localhost:8000/dashboard/',
      'http://localhost:8000/auth/login/',
      'http://localhost:8000/2fa/setup/'
    ];

    for (const url of urls) {
      console.log(`Test de ${url}...`);
      const pageResult = await this.testPage(url);
      this.results.pages.push(pageResult);
    }

    this.generateSummary();
    this.saveReport();
  }

  async testPage(url) {
    const pa11yResults = await pa11y(url, {
      standard: 'WCAG2AA',
      includeNotices: false,
      includeWarnings: true
    });

    return {
      url,
      issues: pa11yResults.issues,
      issueCount: pa11yResults.issues.length,
      errors: pa11yResults.issues.filter(i => i.type === 'error'),
      warnings: pa11yResults.issues.filter(i => i.type === 'warning')
    };
  }

  generateSummary() {
    const totalIssues = this.results.pages.reduce((sum, page) => sum + page.issueCount, 0);
    const totalErrors = this.results.pages.reduce((sum, page) => sum + page.errors.length, 0);
    
    this.results.summary = {
      totalPages: this.results.pages.length,
      totalIssues,
      totalErrors,
      averageIssuesPerPage: totalIssues / this.results.pages.length,
      conformityRate: Math.max(0, 100 - (totalErrors / this.results.pages.length * 10))
    };
  }

  saveReport() {
    const reportPath = `reports/accessibility-${Date.now()}.json`;
    fs.writeFileSync(reportPath, JSON.stringify(this.results, null, 2));
    
    // Générer aussi un rapport HTML
    this.generateHTMLReport(reportPath.replace('.json', '.html'));
    
    console.log(`Rapport sauvegardé: ${reportPath}`);
  }

  generateHTMLReport(path) {
    const html = `
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Rapport d'accessibilité Hyperion</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; }
    .summary { background: #f5f5f5; padding: 20px; margin: 20px 0; }
    .page-result { margin: 20px 0; border-left: 4px solid #007cba; padding-left: 20px; }
    .error { color: #d63384; }
    .warning { color: #fd7e14; }
    .success { color: #198754; }
  </style>
</head>
<body>
  <h1>Rapport d'accessibilité RGAA 4.1 - Hyperion</h1>
  
  <div class="summary">
    <h2>Résumé</h2>
    <p><strong>Date:</strong> ${new Date(this.results.timestamp).toLocaleString('fr-FR')}</p>
    <p><strong>Pages testées:</strong> ${this.results.summary.totalPages}</p>
    <p><strong>Issues totales:</strong> ${this.results.summary.totalIssues}</p>
    <p><strong>Erreurs:</strong> ${this.results.summary.totalErrors}</p>
    <p><strong>Taux de conformité:</strong> ${this.results.summary.conformityRate.toFixed(1)}%</p>
  </div>

  ${this.results.pages.map(page => `
    <div class="page-result">
      <h3>${page.url}</h3>
      <p>${page.errors.length} erreurs, ${page.warnings.length} avertissements</p>
      
      ${page.errors.length > 0 ? `
        <h4 class="error">Erreurs</h4>
        <ul>
          ${page.errors.map(error => `
            <li class="error">${error.message} (${error.selector})</li>
          `).join('')}
        </ul>
      ` : ''}
      
      ${page.warnings.length > 0 ? `
        <h4 class="warning">Avertissements</h4>
        <ul>
          ${page.warnings.map(warning => `
            <li class="warning">${warning.message} (${warning.selector})</li>
          `).join('')}
        </ul>
      ` : ''}
    </div>
  `).join('')}
  
</body>
</html>`;
    
    fs.writeFileSync(path, html);
  }
}

// Exécution
if (require.main === module) {
  new AccessibilityReporter().generateReport().catch(console.error);
}

module.exports = AccessibilityReporter;
```

### 2. Intégration CI/CD

```yaml
# .github/workflows/accessibility.yml
name: Tests d'accessibilité
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  accessibility:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '16'
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        npm install -g pa11y-ci @axe-core/cli
        
    - name: Run Django migrations
      run: |
        python manage.py migrate
        python manage.py collectstatic --noinput
        
    - name: Start Django server
      run: |
        python manage.py runserver 0.0.0.0:8000 &
        sleep 10
        
    - name: Run Pa11y tests
      run: |
        pa11y-ci --sitemap http://localhost:8000/sitemap.xml \
                 --standard WCAG2AA \
                 --threshold 5
                 
    - name: Run axe-core tests
      run: |
        axe http://localhost:8000/dashboard/ \
            --tags wcag2a,wcag2aa \
            --exit
            
    - name: Generate accessibility report
      run: |
        node scripts/generate-accessibility-report.js
        
    - name: Upload reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: accessibility-reports
        path: reports/
```

---

**Guide mis à jour le :** 16 août 2025  
**Version :** 1.0  
**Outils testés avec :** Pa11y 6.2.3, axe-core 4.7.2, NVDA 2024.1
