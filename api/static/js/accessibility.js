// ==========================================
// HYPERION - SCRIPTS D'ACCESSIBILITÉ RGAA 4.1
// ==========================================

class AccessibilityManager {
    constructor() {
        this.initializeAccessibility();
        this.setupKeyboardNavigation();
        this.setupLiveRegions();
        this.setupFocusManagement();
        this.setupHighContrast();
        this.setupSkipLinks();
    }

    // 1. INITIALISATION
    initializeAccessibility() {
        console.log('Initialisation des fonctionnalités d\'accessibilité RGAA 4.1');
        
        // Ajouter les attributs ARIA manquants
        this.addMissingAriaAttributes();
        
        // Configurer les zones live
        this.createLiveRegions();
        
        // Améliorer les formulaires
        this.enhanceFormsAccessibility();
        
        // Configurer la navigation
        this.setupNavigationAccessibility();
    }

    // 2. ATTRIBUTS ARIA MANQUANTS
    addMissingAriaAttributes() {
        // Ajouter role="main" au contenu principal
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.setAttribute('role', 'main');
            mainContent.setAttribute('aria-label', 'Contenu principal du tableau de bord');
        }

        // Ajouter role="navigation" à la navigation
        const nav = document.querySelector('.nav-menu');
        if (nav) {
            nav.setAttribute('role', 'navigation');
            nav.setAttribute('aria-label', 'Navigation principale');
        }

        // Améliorer les boutons
        const buttons = document.querySelectorAll('button:not([aria-label]):not([aria-labelledby])');
        buttons.forEach(button => {
            const text = button.textContent.trim();
            if (text) {
                button.setAttribute('aria-label', text);
            }
        });

        // Améliorer les liens sans texte (icônes uniquement)
        const iconLinks = document.querySelectorAll('a > i.fas');
        iconLinks.forEach(link => {
            const parent = link.parentElement;
            if (!parent.getAttribute('aria-label') && !parent.textContent.trim()) {
                const iconClass = Array.from(link.classList).find(cls => cls.startsWith('fa-'));
                if (iconClass) {
                    const labelMap = {
                        'fa-tachometer-alt': 'Tableau de bord',
                        'fa-microchip': 'Processus système',
                        'fa-cogs': 'Services',
                        'fa-folder': 'Gestion des fichiers',
                        'fa-network-wired': 'Réseau',
                        'fa-terminal': 'Terminal',
                        'fa-shield-alt': 'Authentification à deux facteurs',
                        'fa-user-shield': 'Gestion des rôles',
                        'fa-sign-out-alt': 'Déconnexion'
                    };
                    const label = labelMap[iconClass] || 'Action non définie';
                    parent.setAttribute('aria-label', label);
                }
            }
        });
    }

    // 3. ZONES LIVE REGIONS
    createLiveRegions() {
        // Région pour les messages de statut
        let statusRegion = document.getElementById('status-messages');
        if (!statusRegion) {
            statusRegion = document.createElement('div');
            statusRegion.id = 'status-messages';
            statusRegion.setAttribute('aria-live', 'polite');
            statusRegion.setAttribute('aria-atomic', 'false');
            statusRegion.className = 'sr-only';
            document.body.appendChild(statusRegion);
        }

        // Région pour les alertes urgentes
        let alertRegion = document.getElementById('alert-messages');
        if (!alertRegion) {
            alertRegion = document.createElement('div');
            alertRegion.id = 'alert-messages';
            alertRegion.setAttribute('aria-live', 'assertive');
            alertRegion.setAttribute('aria-atomic', 'true');
            alertRegion.className = 'sr-only';
            document.body.appendChild(alertRegion);
        }

        // Région pour les données dynamiques
        const dynamicElements = document.querySelectorAll('[data-live-update]');
        dynamicElements.forEach(element => {
            element.setAttribute('aria-live', 'polite');
            element.setAttribute('aria-atomic', 'false');
        });
    }

    // 4. NAVIGATION CLAVIER
    setupKeyboardNavigation() {
        // Gestion des touches de navigation
        document.addEventListener('keydown', (e) => {
            switch(e.key) {
                case 'Tab':
                    this.handleTabNavigation(e);
                    break;
                case 'Escape':
                    this.handleEscapeKey(e);
                    break;
                case 'Enter':
                case ' ':
                    this.handleActivationKeys(e);
                    break;
                case 'ArrowUp':
                case 'ArrowDown':
                case 'ArrowLeft':
                case 'ArrowRight':
                    this.handleArrowKeys(e);
                    break;
            }
        });

        // Configuration des tabindex appropriés
        this.setupTabIndexes();
    }

    setupTabIndexes() {
        // Éléments interactifs principaux
        const interactiveElements = document.querySelectorAll(
            'a, button, input, select, textarea, [role="button"], [role="link"]'
        );
        
        interactiveElements.forEach((element, index) => {
            if (!element.hasAttribute('tabindex')) {
                element.setAttribute('tabindex', '0');
            }
        });

        // Éléments non focusables par défaut
        const nonFocusable = document.querySelectorAll('[aria-hidden="true"], .sr-only');
        nonFocusable.forEach(element => {
            element.setAttribute('tabindex', '-1');
        });
    }

    // 5. GESTION DU FOCUS
    setupFocusManagement() {
        // Sauvegarder le focus avant les changements de contenu
        this.previousFocus = null;

        // Piéger le focus dans les modales
        this.trapFocusInModals();

        // Restaurer le focus après les actions
        this.setupFocusRestoration();
    }

    trapFocusInModals() {
        const modals = document.querySelectorAll('[role="dialog"], .modal');
        modals.forEach(modal => {
            modal.addEventListener('keydown', (e) => {
                if (e.key === 'Tab') {
                    const focusableElements = modal.querySelectorAll(
                        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                    );
                    const firstElement = focusableElements[0];
                    const lastElement = focusableElements[focusableElements.length - 1];

                    if (e.shiftKey && document.activeElement === firstElement) {
                        lastElement.focus();
                        e.preventDefault();
                    } else if (!e.shiftKey && document.activeElement === lastElement) {
                        firstElement.focus();
                        e.preventDefault();
                    }
                }
            });
        });
    }

    // 6. FORMULAIRES ACCESSIBLES
    enhanceFormsAccessibility() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            // Associer les labels aux inputs
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                this.associateLabelWithInput(input);
                this.addInputValidation(input);
            });

            // Gérer la soumission
            form.addEventListener('submit', (e) => {
                this.validateFormAccessibility(form, e);
            });
        });
    }

    associateLabelWithInput(input) {
        const id = input.id || this.generateUniqueId('input');
        input.id = id;

        // Chercher un label existant
        let label = document.querySelector(`label[for="${id}"]`);
        
        if (!label) {
            // Chercher un label parent
            label = input.closest('label');
            
            if (!label) {
                // Chercher par placeholder ou name
                const labelText = input.getAttribute('placeholder') || 
                                input.getAttribute('name') || 
                                'Champ de formulaire';
                
                label = document.createElement('label');
                label.setAttribute('for', id);
                label.textContent = labelText;
                label.className = 'sr-only';
                input.parentNode.insertBefore(label, input);
            }
        }

        // Ajouter des instructions si nécessaire
        this.addInputInstructions(input);
    }

    addInputValidation(input) {
        const errorId = `${input.id}-error`;
        let errorElement = document.getElementById(errorId);

        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.id = errorId;
            errorElement.className = 'form-error';
            errorElement.setAttribute('role', 'alert');
            errorElement.setAttribute('aria-live', 'polite');
            input.parentNode.appendChild(errorElement);
        }

        input.setAttribute('aria-describedby', errorId);

        // Validation en temps réel
        input.addEventListener('blur', () => {
            this.validateInput(input, errorElement);
        });

        input.addEventListener('input', () => {
            if (errorElement.textContent) {
                this.validateInput(input, errorElement);
            }
        });
    }

    validateInput(input, errorElement) {
        let isValid = true;
        let errorMessage = '';

        // Validation required
        if (input.hasAttribute('required') && !input.value.trim()) {
            isValid = false;
            errorMessage = 'Ce champ est obligatoire.';
        }

        // Validation email
        if (input.type === 'email' && input.value && !this.isValidEmail(input.value)) {
            isValid = false;
            errorMessage = 'Veuillez saisir une adresse email valide.';
        }

        // Validation password
        if (input.type === 'password' && input.value && input.value.length < 8) {
            isValid = false;
            errorMessage = 'Le mot de passe doit contenir au moins 8 caractères.';
        }

        // Mettre à jour l'interface
        if (isValid) {
            input.classList.remove('error');
            input.removeAttribute('aria-invalid');
            errorElement.textContent = '';
            errorElement.style.display = 'none';
        } else {
            input.classList.add('error');
            input.setAttribute('aria-invalid', 'true');
            errorElement.textContent = errorMessage;
            errorElement.style.display = 'block';
        }

        return isValid;
    }

    // 7. MODE HAUTE VISIBILITÉ
    setupHighContrast() {
        // Vérifier les préférences utilisateur
        if (window.matchMedia('(prefers-contrast: high)').matches) {
            this.enableHighContrast();
        }

        // Bouton de basculement
        this.createContrastToggle();
    }

    createContrastToggle() {
        const toggle = document.createElement('button');
        toggle.id = 'contrast-toggle';
        toggle.className = 'accessible-button';
        toggle.setAttribute('aria-label', 'Activer le mode haute visibilité');
        toggle.innerHTML = '<i class="fas fa-adjust" aria-hidden="true"></i> Contraste';
        toggle.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 1000;
            padding: 8px 12px;
            background: #f8f9fa;
            border: 2px solid #ccc;
            border-radius: 4px;
        `;

        toggle.addEventListener('click', () => {
            this.toggleHighContrast();
        });

        document.body.appendChild(toggle);
    }

    toggleHighContrast() {
        const isHighContrast = document.body.classList.contains('high-contrast');
        const toggle = document.getElementById('contrast-toggle');

        if (isHighContrast) {
            document.body.classList.remove('high-contrast');
            toggle.setAttribute('aria-label', 'Activer le mode haute visibilité');
            this.announceToScreenReader('Mode normale activé');
        } else {
            document.body.classList.add('high-contrast');
            toggle.setAttribute('aria-label', 'Désactiver le mode haute visibilité');
            this.announceToScreenReader('Mode haute visibilité activé');
        }

        // Sauvegarder la préférence
        localStorage.setItem('high-contrast', !isHighContrast);
    }

    // 8. SKIP LINKS
    setupSkipLinks() {
        const skipLinks = document.createElement('div');
        skipLinks.className = 'skip-links';
        skipLinks.innerHTML = `
            <a href="#main-content" class="skip-link">Aller au contenu principal</a>
            <a href="#navigation" class="skip-link">Aller à la navigation</a>
        `;

        document.body.insertBefore(skipLinks, document.body.firstChild);

        // Ajouter les IDs correspondants
        const mainContent = document.querySelector('[role="main"], .main-content');
        if (mainContent) {
            mainContent.id = 'main-content';
        }

        const navigation = document.querySelector('[role="navigation"], nav');
        if (navigation) {
            navigation.id = 'navigation';
        }
    }

    // 9. UTILITAIRES
    announceToScreenReader(message) {
        const statusRegion = document.getElementById('status-messages');
        if (statusRegion) {
            statusRegion.textContent = message;
            setTimeout(() => {
                statusRegion.textContent = '';
            }, 1000);
        }
    }

    announceAlert(message) {
        const alertRegion = document.getElementById('alert-messages');
        if (alertRegion) {
            alertRegion.textContent = message;
            setTimeout(() => {
                alertRegion.textContent = '';
            }, 3000);
        }
    }

    generateUniqueId(prefix = 'element') {
        return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // 10. GESTION DES ÉVÉNEMENTS CLAVIER
    handleTabNavigation(e) {
        // Logique personnalisée pour Tab si nécessaire
        const focusableElements = document.querySelectorAll(
            'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        const visibleElements = Array.from(focusableElements).filter(el => {
            return el.offsetParent !== null && !el.hasAttribute('aria-hidden');
        });

        const currentIndex = visibleElements.indexOf(document.activeElement);
        
        if (e.shiftKey && currentIndex === 0) {
            // Premier élément + Shift+Tab = dernier élément
            visibleElements[visibleElements.length - 1].focus();
            e.preventDefault();
        } else if (!e.shiftKey && currentIndex === visibleElements.length - 1) {
            // Dernier élément + Tab = premier élément
            visibleElements[0].focus();
            e.preventDefault();
        }
    }

    handleEscapeKey(e) {
        // Fermer les modales ou menus ouverts
        const openModals = document.querySelectorAll('[role="dialog"]:not([aria-hidden="true"])');
        openModals.forEach(modal => {
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
            
            // Restaurer le focus
            if (this.previousFocus) {
                this.previousFocus.focus();
                this.previousFocus = null;
            }
        });
    }

    handleActivationKeys(e) {
        const target = e.target;
        
        // Activer les éléments avec role="button"
        if (target.getAttribute('role') === 'button' && !target.disabled) {
            e.preventDefault();
            target.click();
        }
    }

    handleArrowKeys(e) {
        // Navigation dans les menus ou listes
        const currentElement = e.target;
        const parent = currentElement.closest('[role="menu"], [role="menubar"], [role="listbox"]');
        
        if (parent) {
            e.preventDefault();
            const siblings = Array.from(parent.querySelectorAll('[role="menuitem"], [role="option"]'));
            const currentIndex = siblings.indexOf(currentElement);
            
            let nextIndex;
            switch(e.key) {
                case 'ArrowDown':
                    nextIndex = (currentIndex + 1) % siblings.length;
                    break;
                case 'ArrowUp':
                    nextIndex = currentIndex === 0 ? siblings.length - 1 : currentIndex - 1;
                    break;
                case 'Home':
                    nextIndex = 0;
                    break;
                case 'End':
                    nextIndex = siblings.length - 1;
                    break;
            }
            
            if (nextIndex !== undefined) {
                siblings[nextIndex].focus();
            }
        }
    }

    // 11. AMÉLIORATION DES GRAPHIQUES
    makeChartsAccessible() {
        const charts = document.querySelectorAll('canvas[id*="chart"]');
        charts.forEach(canvas => {
            this.addChartAccessibility(canvas);
        });
    }

    addChartAccessibility(canvas) {
        // Ajouter des attributs ARIA
        canvas.setAttribute('role', 'img');
        canvas.setAttribute('aria-label', 'Graphique de données système');
        
        // Créer une table de données alternative
        const container = canvas.parentElement;
        const tableId = `${canvas.id}-data-table`;
        
        let table = document.getElementById(tableId);
        if (!table) {
            table = document.createElement('table');
            table.id = tableId;
            table.className = 'accessible-table sr-only';
            table.innerHTML = `
                <caption>Données du graphique</caption>
                <thead>
                    <tr>
                        <th scope="col">Temps</th>
                        <th scope="col">Valeur</th>
                    </tr>
                </thead>
                <tbody></tbody>
            `;
            container.appendChild(table);
        }
        
        // Associer la table au canvas
        canvas.setAttribute('aria-describedby', tableId);
        
        // Bouton pour afficher/masquer les données
        const toggleButton = document.createElement('button');
        toggleButton.textContent = 'Afficher les données du graphique';
        toggleButton.className = 'accessible-button';
        toggleButton.addEventListener('click', () => {
            table.classList.toggle('sr-only');
            toggleButton.textContent = table.classList.contains('sr-only') 
                ? 'Afficher les données du graphique'
                : 'Masquer les données du graphique';
        });
        
        container.appendChild(toggleButton);
    }
}

// Initialisation automatique
document.addEventListener('DOMContentLoaded', () => {
    window.accessibilityManager = new AccessibilityManager();
    
    // Charger les préférences sauvegardées
    if (localStorage.getItem('high-contrast') === 'true') {
        document.body.classList.add('high-contrast');
    }
    
    console.log('✅ Accessibilité RGAA 4.1 initialisée');
});

// Export pour utilisation dans d'autres scripts
window.AccessibilityManager = AccessibilityManager;
