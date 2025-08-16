const { configureAxe } = require('jest-axe');

// Configuration axe-core pour tests RGAA
const axe = configureAxe({
  rules: {
    // Règles WCAG 2.1 AA pour RGAA 4.1
    'color-contrast': { 
      enabled: true,
      options: {
        // Seuil WCAG AA: 4.5:1 pour texte normal
        contrastRatio: { 
          normal: 4.5, 
          large: 3.0 
        }
      }
    },
    'focus-order-semantics': { enabled: true },
    'keyboard-navigation': { enabled: true },
    'page-has-heading-one': { enabled: true },
    'landmark-one-main': { enabled: true },
    'region': { enabled: true },
    
    // Règles spécifiques aux formulaires
    'label': { enabled: true },
    'form-field-multiple-labels': { enabled: true },
    'aria-required-attr': { enabled: true },
    
    // Règles pour les tableaux
    'table-fake-caption': { enabled: true },
    'td-headers-attr': { enabled: true },
    'th-has-data-cells': { enabled: true },
    
    // Règles pour les images
    'image-alt': { enabled: true },
    'image-redundant-alt': { enabled: true },
    
    // Désactiver les règles non-RGAA temporairement
    'color-contrast-enhanced': { enabled: false }, // WCAG AAA
    'focus-order-semantics': { enabled: false } // Problème connu
  },
  
  // Tags WCAG à inclure pour RGAA 4.1
  tags: ['wcag2a', 'wcag2aa', 'wcag21aa'],
  
  // Configuration des résultats
  resultTypes: ['violations', 'incomplete'],
  
  // Règles spécifiques au contexte Hyperion
  locale: 'fr'
});

// Configuration globale pour les tests
global.axe = axe;

// Configuration Puppeteer pour les tests d'accessibilité
global.puppeteerConfig = {
  launch: {
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--no-first-run',
      '--no-zygote',
      '--disable-gpu'
    ]
  },
  viewport: {
    width: 1920,
    height: 1080
  }
};

// Timeout global pour les tests d'accessibilité
jest.setTimeout(30000);

// Configuration des matchers Jest personnalisés
expect.extend({
  toBeAccessible(received) {
    if (received && received.violations && received.violations.length === 0) {
      return {
        pass: true,
        message: () => 'La page est accessible selon les critères RGAA'
      };
    } else {
      const violations = received.violations || [];
      const violationMessages = violations.map(v => 
        `${v.id}: ${v.description} (${v.nodes.length} éléments)`
      ).join('\n');
      
      return {
        pass: false,
        message: () => 
          `La page n'est pas accessible:\n${violationMessages}`
      };
    }
  },
  
  toHaveNoContrastIssues(received) {
    const contrastIssues = received.violations.filter(v => 
      v.id.includes('color-contrast')
    );
    
    return {
      pass: contrastIssues.length === 0,
      message: () => contrastIssues.length === 0
        ? 'Tous les contrastes respectent les critères WCAG AA'
        : `${contrastIssues.length} problèmes de contraste détectés`
    };
  },
  
  toHaveProperFormLabeling(received) {
    const labelIssues = received.violations.filter(v => 
      ['label', 'form-field-multiple-labels'].includes(v.id)
    );
    
    return {
      pass: labelIssues.length === 0,
      message: () => labelIssues.length === 0
        ? 'Tous les formulaires sont correctement étiquetés'
        : `${labelIssues.length} problèmes d'étiquetage détectés`
    };
  }
});

// Helper functions pour les tests
global.testHelpers = {
  // Attendre le chargement des composants dynamiques
  async waitForDynamicContent(page, selector, timeout = 10000) {
    try {
      await page.waitForSelector(selector, { 
        visible: true, 
        timeout 
      });
      await page.waitForTimeout(1000); // Délai supplémentaire pour WebSocket
      return true;
    } catch (error) {
      console.warn(`Timeout waiting for ${selector}:`, error.message);
      return false;
    }
  },
  
  // Simuler l'authentification pour les pages protégées
  async loginUser(page, username = 'testuser', password = 'testpass123') {
    await page.goto('http://localhost:8000/auth/login/');
    await page.fill('#id_username', username);
    await page.fill('#id_password', password);
    await page.click('button[type="submit"]');
    await page.waitForNavigation();
  },
  
  // Vérifier la navigation au clavier
  async testKeyboardNavigation(page, startSelector, expectedStops = 5) {
    await page.focus(startSelector);
    const focusedElements = [];
    
    for (let i = 0; i < expectedStops; i++) {
      await page.keyboard.press('Tab');
      const activeElement = await page.evaluate(() => ({
        tag: document.activeElement.tagName,
        id: document.activeElement.id,
        className: document.activeElement.className,
        text: document.activeElement.textContent?.trim().substring(0, 50)
      }));
      
      focusedElements.push(activeElement);
    }
    
    return focusedElements;
  },
  
  // Vérifier les annonces des lecteurs d'écran
  async checkScreenReaderAnnouncements(page) {
    return page.evaluate(() => {
      const liveRegions = document.querySelectorAll('[aria-live]');
      return Array.from(liveRegions).map(region => ({
        type: region.getAttribute('aria-live'),
        content: region.textContent.trim(),
        visible: region.offsetParent !== null
      }));
    });
  }
};

console.log('🔧 Configuration des tests d\'accessibilité chargée (RGAA 4.1)');
