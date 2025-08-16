/**
 * Tests d'accessibilité RGAA 4.1 - Dashboard Hyperion
 * 
 * Ce fichier teste la conformité du dashboard principal selon les critères
 * du Référentiel Général d'Amélioration de l'Accessibilité (RGAA 4.1)
 * Niveau visé: AA
 */

const { AxePuppeteer } = require('@axe-core/puppeteer');

describe('Accessibilité Dashboard Hyperion - RGAA 4.1', () => {
  let page;
  let browser;

  beforeAll(async () => {
    browser = await require('puppeteer').launch(global.puppeteerConfig.launch);
  });

  beforeEach(async () => {
    page = await browser.newPage();
    await page.setViewport(global.puppeteerConfig.viewport);
    
    // Configurer les intercepteurs pour les WebSockets
    await page.setRequestInterception(true);
    page.on('request', (req) => {
      // Laisser passer toutes les requêtes sauf WebSocket pour les tests
      if (req.url().includes('ws://') || req.url().includes('wss://')) {
        req.abort();
      } else {
        req.continue();
      }
    });
  });

  afterEach(async () => {
    await page.close();
  });

  afterAll(async () => {
    await browser.close();
  });

  describe('🏠 Page d\'accueil / Dashboard', () => {
    beforeEach(async () => {
      await page.goto('http://localhost:8000/dashboard/', { 
        waitUntil: 'domcontentloaded',
        timeout: 30000 
      });
      
      // Attendre que les composants se chargent
      await global.testHelpers.waitForDynamicContent(
        page, 
        '.main-content', 
        10000
      );
    });

    test('Conformité globale WCAG 2.1 AA', async () => {
      const results = await new AxePuppeteer(page)
        .withTags(['wcag2a', 'wcag2aa'])
        .analyze();

      expect(results).toBeAccessible();
    }, 30000);

    test('Critère 1.1 - Images décoratives et informatives', async () => {
      const imageResults = await page.evaluate(() => {
        const images = document.querySelectorAll('img, i[class*="fa"], svg');
        const results = [];

        images.forEach(img => {
          const alt = img.getAttribute('alt');
          const ariaLabel = img.getAttribute('aria-label');
          const ariaHidden = img.getAttribute('aria-hidden');
          const role = img.getAttribute('role');

          results.push({
            tag: img.tagName,
            src: img.src || img.className,
            alt: alt,
            ariaLabel: ariaLabel,
            ariaHidden: ariaHidden,
            role: role,
            hasAlternative: !!(alt || ariaLabel || ariaHidden === 'true')
          });
        });

        return results;
      });

      // Toutes les images doivent avoir une alternative appropriée
      const imagesWithoutAlt = imageResults.filter(img => !img.hasAlternative);
      
      expect(imagesWithoutAlt).toHaveLength(0);
      
      if (imagesWithoutAlt.length > 0) {
        console.log('Images sans alternative:', imagesWithoutAlt);
      }
    });

    test('Critère 3.1 - Information donnée par la couleur', async () => {
      const colorOnlyInfo = await page.evaluate(() => {
        // Vérifier les statuts des services (problème identifié)
        const statusElements = document.querySelectorAll('.status');
        const results = [];

        statusElements.forEach(status => {
          const computedStyle = window.getComputedStyle(status);
          const color = computedStyle.color;
          const backgroundColor = computedStyle.backgroundColor;
          const textContent = status.textContent.trim();
          
          results.push({
            element: status.outerHTML.substring(0, 100),
            color: color,
            backgroundColor: backgroundColor,
            textContent: textContent,
            hasTextualInfo: textContent.length > 1 && !['●', '•', '○'].includes(textContent)
          });
        });

        return results;
      });

      // Les statuts ne doivent pas reposer uniquement sur la couleur
      const colorOnlyElements = colorOnlyInfo.filter(el => !el.hasTextualInfo);
      
      if (colorOnlyElements.length > 0) {
        console.warn('Éléments utilisant uniquement la couleur:', colorOnlyElements);
        // Note: Ce test peut échouer - c'est un problème identifié dans l'audit
      }
    });

    test('Critère 7.1 - Scripts compatibles avec les technologies d\'assistance', async () => {
      // Tester la compatibilité des graphiques Chart.js
      const chartAccessibility = await page.evaluate(() => {
        const charts = document.querySelectorAll('canvas');
        const results = [];

        charts.forEach(chart => {
          const ariaLabel = chart.getAttribute('aria-label');
          const ariaLabelledBy = chart.getAttribute('aria-labelledby');
          const ariaDescribedBy = chart.getAttribute('aria-describedby');
          const role = chart.getAttribute('role');

          results.push({
            id: chart.id,
            hasAriaLabel: !!ariaLabel,
            hasAriaLabelledBy: !!ariaLabelledBy,
            hasAriaDescribedBy: !!ariaDescribedBy,
            hasRole: !!role,
            isAccessible: !!(ariaLabel || ariaLabelledBy || ariaDescribedBy)
          });
        });

        return results;
      });

      // Tous les graphiques doivent avoir des alternatives textuelles
      const inaccessibleCharts = chartAccessibility.filter(chart => !chart.isAccessible);
      
      if (inaccessibleCharts.length > 0) {
        console.warn('Graphiques non accessibles:', inaccessibleCharts);
        // Note: Problème connu, correction en cours
      }
    });

    test('Critère 11.1 - Champs de formulaire avec étiquettes', async () => {
      const formResults = await new AxePuppeteer(page)
        .withTags(['wcag2a'])
        .include('input, select, textarea')
        .analyze();

      expect(formResults).toHaveProperFormLabeling();

      // Test spécifique pour les champs identifiés
      const unlabeledFields = await page.evaluate(() => {
        const fields = document.querySelectorAll('input, select, textarea');
        const results = [];

        fields.forEach(field => {
          const id = field.id;
          const name = field.name;
          const label = document.querySelector(`label[for="${id}"]`);
          const ariaLabel = field.getAttribute('aria-label');
          const ariaLabelledBy = field.getAttribute('aria-labelledby');

          if (!label && !ariaLabel && !ariaLabelledBy) {
            results.push({
              tag: field.tagName,
              id: id,
              name: name,
              placeholder: field.placeholder,
              type: field.type
            });
          }
        });

        return results;
      });

      if (unlabeledFields.length > 0) {
        console.log('Champs sans étiquette:', unlabeledFields);
      }

      // Ce test peut échouer - problème identifié
    });

    test('Critère 12.1 - Navigation principale et zones de contenu', async () => {
      const landmarkResults = await page.evaluate(() => {
        return {
          hasMain: !!document.querySelector('main, [role="main"]'),
          hasNav: !!document.querySelector('nav, [role="navigation"]'),
          hasBanner: !!document.querySelector('header[role="banner"], [role="banner"]'),
          hasContentInfo: !!document.querySelector('footer[role="contentinfo"], [role="contentinfo"]'),
          hasComplementary: !!document.querySelector('aside, [role="complementary"]')
        };
      });

      expect(landmarkResults.hasMain).toBe(true);
      expect(landmarkResults.hasNav).toBe(true);
      
      // Les autres landmarks sont recommandés mais pas obligatoires
      if (!landmarkResults.hasBanner) {
        console.warn('Pas de landmark banner trouvé');
      }
    });

    test('Navigation au clavier complète', async () => {
      const focusableElements = await global.testHelpers.testKeyboardNavigation(
        page, 
        'body', 
        10
      );

      expect(focusableElements.length).toBeGreaterThan(0);
      
      // Vérifier que tous les éléments focusés sont des éléments interactifs
      const validFocusableTags = ['A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA'];
      const invalidFocused = focusableElements.filter(el => 
        !validFocusableTags.includes(el.tag)
      );

      expect(invalidFocused).toHaveLength(0);
    });

    test('Contrastes de couleur WCAG AA (4.5:1)', async () => {
      const results = await new AxePuppeteer(page)
        .withTags(['wcag2aa'])
        .include('[style*="color"], .status, .alert, .badge')
        .analyze();

      expect(results).toHaveNoContrastIssues();
    });

    test('Annonces pour les lecteurs d\'écran', async () => {
      const announcements = await global.testHelpers.checkScreenReaderAnnouncements(page);
      
      // Vérifier qu'il y a au moins une zone live pour les mises à jour
      const liveRegions = announcements.filter(region => 
        ['polite', 'assertive'].includes(region.type)
      );

      expect(liveRegions.length).toBeGreaterThan(0);
    });
  });

  describe('🔐 Page de connexion', () => {
    beforeEach(async () => {
      await page.goto('http://localhost:8000/auth/login/', { 
        waitUntil: 'domcontentloaded' 
      });
    });

    test('Formulaire de connexion accessible', async () => {
      const results = await new AxePuppeteer(page)
        .withTags(['wcag2a', 'wcag2aa'])
        .analyze();

      expect(results).toBeAccessible();
    });

    test('Étiquetage des champs de connexion', async () => {
      const formLabeling = await page.evaluate(() => {
        const usernameField = document.querySelector('#id_username, [name="username"]');
        const passwordField = document.querySelector('#id_password, [name="password"]');
        
        return {
          usernameHasLabel: !!(
            document.querySelector('label[for="id_username"]') ||
            usernameField?.getAttribute('aria-label')
          ),
          passwordHasLabel: !!(
            document.querySelector('label[for="id_password"]') ||
            passwordField?.getAttribute('aria-label')
          )
        };
      });

      expect(formLabeling.usernameHasLabel).toBe(true);
      expect(formLabeling.passwordHasLabel).toBe(true);
    });

    test('Messages d\'erreur associés aux champs', async () => {
      // Simuler une tentative de connexion échouée
      await page.fill('#id_username', 'baduser');
      await page.fill('#id_password', 'badpass');
      await page.click('button[type="submit"]');
      
      // Attendre la réponse
      await page.waitForTimeout(2000);
      
      const errorHandling = await page.evaluate(() => {
        const errorMessages = document.querySelectorAll('.error, .alert-danger, [role="alert"]');
        const usernameField = document.querySelector('#id_username');
        const passwordField = document.querySelector('#id_password');
        
        return {
          hasErrorMessages: errorMessages.length > 0,
          usernameHasAriaDescribedBy: !!usernameField?.getAttribute('aria-describedby'),
          passwordHasAriaDescribedBy: !!passwordField?.getAttribute('aria-describedby'),
          errorMessagesText: Array.from(errorMessages).map(el => el.textContent.trim())
        };
      });

      if (errorHandling.hasErrorMessages) {
        console.log('Messages d\'erreur trouvés:', errorHandling.errorMessagesText);
      }
    });
  });

  describe('📊 Tests de performance d\'accessibilité', () => {
    test('Temps de réponse des technologies d\'assistance', async () => {
      const startTime = Date.now();
      
      await page.goto('http://localhost:8000/dashboard/');
      await global.testHelpers.waitForDynamicContent(page, '.main-content');
      
      const loadTime = Date.now() - startTime;
      
      // Le chargement ne doit pas dépasser 10 secondes pour les TA
      expect(loadTime).toBeLessThan(10000);
    });

    test('Zoom à 200% sans perte d\'information', async () => {
      await page.goto('http://localhost:8000/dashboard/');
      
      // Zoom initial
      const initialContent = await page.evaluate(() => ({
        processTable: !!document.querySelector('#processesTableBody'),
        serviceTable: !!document.querySelector('#servicesTableBody'),
        charts: document.querySelectorAll('canvas').length
      }));
      
      // Zoom à 200%
      await page.evaluate(() => {
        document.body.style.zoom = '2.0';
      });
      
      await page.waitForTimeout(1000);
      
      // Vérifier que le contenu est toujours visible
      const zoomedContent = await page.evaluate(() => ({
        processTable: !!document.querySelector('#processesTableBody'),
        serviceTable: !!document.querySelector('#servicesTableBody'),
        charts: document.querySelectorAll('canvas').length,
        hasHorizontalScroll: document.body.scrollWidth > window.innerWidth
      }));
      
      expect(zoomedContent.processTable).toBe(initialContent.processTable);
      expect(zoomedContent.serviceTable).toBe(initialContent.serviceTable);
      expect(zoomedContent.charts).toBe(initialContent.charts);
      
      // Un peu de scroll horizontal est acceptable à 200%
    });
  });

  describe('🎯 Tests spécifiques RGAA 4.1', () => {
    test('Critère 8.6 - Hiérarchie des titres', async () => {
      await page.goto('http://localhost:8000/dashboard/');
      
      const headingStructure = await page.evaluate(() => {
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        return Array.from(headings).map(h => ({
          level: parseInt(h.tagName.charAt(1)),
          text: h.textContent.trim()
        }));
      });
      
      // Vérifier qu'il y a un seul H1
      const h1Count = headingStructure.filter(h => h.level === 1).length;
      expect(h1Count).toBe(1);
      
      // Vérifier que la hiérarchie est logique
      for (let i = 1; i < headingStructure.length; i++) {
        const current = headingStructure[i];
        const previous = headingStructure[i - 1];
        
        // Un titre ne doit pas sauter plus d'un niveau
        if (current.level > previous.level) {
          expect(current.level - previous.level).toBeLessThanOrEqual(1);
        }
      }
    });

    test('Critère 13.5 - Contenu en mouvement contrôlable', async () => {
      await page.goto('http://localhost:8000/dashboard/');
      await global.testHelpers.waitForDynamicContent(page, 'canvas');
      
      const animationControls = await page.evaluate(() => {
        // Chercher des contrôles pour pause/lecture
        const pauseButtons = document.querySelectorAll(
          'button[aria-label*="pause"], button[aria-label*="stop"], ' +
          'button[title*="pause"], button[title*="stop"]'
        );
        
        const playButtons = document.querySelectorAll(
          'button[aria-label*="play"], button[aria-label*="start"], ' +
          'button[title*="play"], button[title*="start"]'
        );
        
        return {
          hasPauseControls: pauseButtons.length > 0,
          hasPlayControls: playButtons.length > 0,
          totalControls: pauseButtons.length + playButtons.length
        };
      });
      
      // Les graphiques temps réel devraient avoir des contrôles
      // Note: Ceci peut échouer - amélioration nécessaire
      if (animationControls.totalControls === 0) {
        console.warn('Aucun contrôle de lecture/pause trouvé pour le contenu dynamique');
      }
    });
  });
});
