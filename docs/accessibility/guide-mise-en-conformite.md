# Guide de mise en conformité RGAA 4.1 - Hyperion

## Actions correctrices par ordre de priorité

### 🚨 Priorité CRITIQUE (0-1 mois)

#### 1. Étiquetage des champs de formulaire (Critère 11.1)

**Problème :** Champs de filtrage sans `<label>` associé

**Code actuel :**
```html
<input type="text" id="processFilter" placeholder="Filter processes..." />
<select id="processSorting">
  <option value="cpu">Sort by CPU</option>
</select>
```

**Code corrigé :**
```html
<label for="processFilter">Filtrer les processus</label>
<input type="text" id="processFilter" placeholder="Ex: nginx, apache..." />

<label for="processSorting">Trier par</label>
<select id="processSorting" aria-describedby="sort-help">
  <option value="cpu">CPU</option>
  <option value="memory">Mémoire</option>
  <option value="name">Nom</option>
</select>
<div id="sort-help" class="sr-only">
  Choisir le critère de tri pour la liste des processus
</div>
```

#### 2. Information véhiculée par la couleur (Critère 3.1)

**Problème :** Statuts des services uniquement en couleur

**Code actuel :**
```html
<td class="status active">●</td>  <!-- Vert pour actif -->
<td class="status inactive">●</td> <!-- Rouge pour inactif -->
```

**Code corrigé :**
```html
<td class="status active">
  <span class="status-indicator" aria-label="Service actif">●</span>
  <span class="status-text">Actif</span>
</td>
<td class="status inactive">
  <span class="status-indicator" aria-label="Service arrêté">●</span>
  <span class="status-text">Arrêté</span>
</td>
```

#### 3. Alternatives textuelles pour graphiques (Critère 1.3)

**Problème :** Graphiques Chart.js inaccessibles

**Solution :**
```html
<div class="chart-container">
  <canvas id="cpuChart" aria-labelledby="cpu-title" aria-describedby="cpu-desc">
    <!-- Fallback pour navigateurs sans JavaScript -->
    <p>Graphique d'utilisation CPU indisponible</p>
  </canvas>
  <h3 id="cpu-title">Utilisation CPU en temps réel</h3>
  <div id="cpu-desc" class="sr-only">
    <p>Graphique linéaire montrant l'évolution du CPU sur les 30 dernières minutes.</p>
    <p>Valeur actuelle : <span id="cpu-current">45%</span></p>
    <p>Pic maximum : <span id="cpu-max">78%</span> à <span id="cpu-max-time">14:32</span></p>
  </div>
  
  <!-- Table alternative accessible -->
  <div class="chart-data-table" aria-labelledby="cpu-data-title">
    <h4 id="cpu-data-title" class="sr-only">Données CPU (tableau accessible)</h4>
    <table class="sr-only">
      <caption>Utilisation CPU par tranche de 5 minutes</caption>
      <thead>
        <tr>
          <th scope="col">Heure</th>
          <th scope="col">CPU (%)</th>
        </tr>
      </thead>
      <tbody id="cpu-data-tbody">
        <!-- Données injectées via JavaScript -->
      </tbody>
    </table>
  </div>
</div>
```

### ⚠️ Priorité IMPORTANTE (1-3 mois)

#### 4. Structure de navigation (Critère 12.1)

**Code actuel :**
```html
<div class="main-content">
  <header>
    <h1>Hyperion Dashboard</h1>
  </header>
  <main>
    <div class="container">
      <!-- Contenu -->
    </div>
  </main>
</div>
```

**Code amélioré :**
```html
<div class="main-content">
  <header role="banner">
    <h1>Hyperion Dashboard</h1>
    <nav aria-label="Fil d'Ariane">
      <ol>
        <li><a href="/">Accueil</a></li>
        <li aria-current="page">Dashboard</li>
      </ol>
    </nav>
  </header>
  
  <nav role="navigation" aria-label="Navigation principale">
    <!-- Menu principal -->
  </nav>
  
  <main role="main">
    <section aria-labelledby="processes-title">
      <h2 id="processes-title">Gestion des processus</h2>
      <!-- Contenu processus -->
    </section>
    
    <section aria-labelledby="services-title">
      <h2 id="services-title">Gestion des services</h2>
      <!-- Contenu services -->
    </section>
  </main>
  
  <aside role="complementary" aria-labelledby="monitoring-title">
    <h2 id="monitoring-title">Monitoring temps réel</h2>
    <!-- Graphiques -->
  </aside>
  
  <footer role="contentinfo">
    <!-- Pied de page -->
  </footer>
</div>
```

#### 5. Amélioration des composants JavaScript (Critère 7.4)

**Pattern pour composant accessible :**
```javascript
class AccessibleDataTable {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.table = this.container.querySelector('table');
    this.setupARIA();
    this.setupKeyboardNavigation();
    this.setupLiveRegions();
  }

  setupARIA() {
    // Configuration ARIA pour navigation au clavier
    this.table.setAttribute('role', 'grid');
    this.table.setAttribute('aria-labelledby', `${this.containerId}-title`);
    
    // En-têtes de colonnes
    const headers = this.table.querySelectorAll('th');
    headers.forEach((header, index) => {
      header.setAttribute('role', 'columnheader');
      header.setAttribute('scope', 'col');
      header.setAttribute('tabindex', '-1');
    });
  }

  setupKeyboardNavigation() {
    this.table.addEventListener('keydown', (e) => {
      const cell = e.target.closest('td, th');
      if (!cell) return;

      switch(e.key) {
        case 'ArrowUp':
          this.moveFocus(cell, 'up');
          e.preventDefault();
          break;
        case 'ArrowDown':
          this.moveFocus(cell, 'down');
          e.preventDefault();
          break;
        case 'ArrowLeft':
          this.moveFocus(cell, 'left');
          e.preventDefault();
          break;
        case 'ArrowRight':
          this.moveFocus(cell, 'right');
          e.preventDefault();
          break;
      }
    });
  }

  setupLiveRegions() {
    // Zone d'annonce pour changements dynamiques
    const liveRegion = document.createElement('div');
    liveRegion.setAttribute('aria-live', 'polite');
    liveRegion.setAttribute('aria-atomic', 'false');
    liveRegion.className = 'sr-only';
    liveRegion.id = `${this.containerId}-announcements`;
    this.container.appendChild(liveRegion);
  }

  updateData(newData) {
    // Mise à jour des données avec annonce
    this.renderData(newData);
    this.announceUpdate(`${newData.length} processus mis à jour`);
  }

  announceUpdate(message) {
    const liveRegion = document.getElementById(`${this.containerId}-announcements`);
    liveRegion.textContent = message;
  }
}
```

### 📝 Priorité MINEURE (3-6 mois)

#### 6. Optimisation CSS pour accessibilité

**Classes utilitaires :**
```css
/* Classe pour contenu réservé aux lecteurs d'écran */
.sr-only {
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  padding: 0 !important;
  margin: -1px !important;
  overflow: hidden !important;
  clip: rect(0, 0, 0, 0) !important;
  border: 0 !important;
}

/* Focus visible amélioré */
:focus-visible {
  outline: 2px solid #005fcc;
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(0, 95, 204, 0.2);
}

/* Animation respectueuse des préférences utilisateur */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Contraste élevé */
@media (prefers-contrast: high) {
  .status.active { 
    background-color: #000000;
    color: #ffffff; 
  }
  .status.inactive { 
    background-color: #ffffff;
    color: #000000;
    border: 2px solid #000000;
  }
}
```

## Tests de validation

### 1. Tests automatisés avec axe-core

```javascript
// tests/accessibility.test.js
describe('Accessibilité RGAA', () => {
  test('Dashboard principal', async () => {
    await page.goto('http://localhost:8000/dashboard/');
    const results = await new AxePuppeteer(page).analyze();
    expect(results.violations).toHaveLength(0);
  });

  test('Formulaires de connexion', async () => {
    await page.goto('http://localhost:8000/auth/login/');
    const results = await new AxePuppeteer(page)
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();
    expect(results.violations).toHaveLength(0);
  });
});
```

### 2. Tests avec technologies d'assistance

**Liste de vérification manuelle :**

- [ ] Navigation complète au clavier uniquement
- [ ] Lecture complète avec NVDA/JAWS
- [ ] Zoom à 200% sans perte d'information
- [ ] Contraste élevé fonctionnel
- [ ] Mode sombre accessible

### 3. Tests utilisateurs

**Critères de réussite :**

- [ ] Utilisateur malvoyant peut consulter les métriques
- [ ] Utilisateur moteur peut gérer les services au clavier
- [ ] Utilisateur cognitif comprend les interfaces
- [ ] Utilisateur sourd accède aux alertes visuelles

## Maintenance continue

### 1. Intégration CI/CD

```yaml
# .github/workflows/accessibility.yml
name: Tests d'accessibilité
on: [push, pull_request]

jobs:
  accessibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Tests Pa11y
        run: |
          npm install -g pa11y-ci
          pa11y-ci --sitemap http://localhost:8000/sitemap.xml
      - name: Tests axe-core
        run: npm run test:a11y
```

### 2. Documentation développeur

**Checklist avant commit :**

- [ ] Nouvelles images ont un attribut `alt` approprié
- [ ] Nouveaux formulaires ont des `<label>` associés
- [ ] Nouveaux composants JS supportent la navigation clavier
- [ ] Contrastes respectent le ratio 4.5:1
- [ ] Structure HTML est sémantiquement correcte

### 3. Formation équipe

**Modules de formation recommandés :**

1. **RGAA 4.1 fondamentaux** (8h)
2. **Tests avec technologies d'assistance** (4h)
3. **Développement accessible React/Vue** (6h)
4. **Audit d'accessibilité** (4h)

---

**Document mis à jour le :** 16 août 2025  
**Version :** 1.0  
**Prochain audit :** 16 novembre 2025
