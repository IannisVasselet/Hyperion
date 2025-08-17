// ==========================================
// HYPERION - SCRIPTS D'ACCESSIBILITÉ DASHBOARD
// ==========================================

// Fonctions d'accessibilité spécifiques au tableau de bord
class DashboardAccessibility {
    constructor() {
        this.currentChart = 'cpu';
        this.chartData = {
            cpu: [],
            memory: [],
            network: []
        };
        this.init();
    }

    init() {
        this.setupTableAccessibility();
        this.setupChartAccessibility();
        this.setupDynamicUpdates();
        this.setupKeyboardShortcuts();
    }

    // 1. AMÉLIORATION DES TABLEAUX
    setupTableAccessibility() {
        // Ajouter des boutons de tri accessibles
        this.setupSortableHeaders();
        
        // Améliorer les cellules d'action
        this.enhanceActionCells();
        
        // Gérer les mises à jour de contenu
        this.setupTableUpdates();
    }

    setupSortableHeaders() {
        const sortButtons = document.querySelectorAll('.table-sort-button');
        sortButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const sortType = button.getAttribute('onclick').match(/sortProcesses\('([^']+)'\)/)?.[1];
                if (sortType) {
                    this.announceSort(sortType);
                    this.updateSortIndicators(button);
                }
            });
        });
    }

    announceSort(sortType) {
        const sortLabels = {
            name: 'nom',
            cpu: 'utilisation CPU',
            memory: 'utilisation mémoire'
        };
        const message = `Tableau trié par ${sortLabels[sortType] || sortType}`;
        
        if (window.accessibilityManager) {
            window.accessibilityManager.announceToScreenReader(message);
        }
    }

    updateSortIndicators(activeButton) {
        // Réinitialiser tous les indicateurs
        document.querySelectorAll('.table-sort-button i').forEach(icon => {
            icon.className = 'fas fa-sort';
        });
        
        // Activer l'indicateur du bouton actuel
        const icon = activeButton.querySelector('i');
        if (icon) {
            icon.className = 'fas fa-sort-up';
        }
        
        // Mettre à jour l'aria-label
        const currentLabel = activeButton.getAttribute('aria-label');
        activeButton.setAttribute('aria-label', `${currentLabel} - Actuellement trié`);
    }

    enhanceActionCells() {
        // Observer les changements dans les tableaux pour améliorer les boutons d'action
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    this.enhanceNewActionButtons();
                }
            });
        });

        // Observer les tbody des tableaux
        const tableBodys = document.querySelectorAll('#processesTableBody, #servicesTableBody');
        tableBodys.forEach(tbody => {
            observer.observe(tbody, { childList: true, subtree: true });
        });
    }

    enhanceNewActionButtons() {
        // Améliorer les boutons d'action dans les tableaux
        const actionButtons = document.querySelectorAll('tbody button:not([aria-label])');
        actionButtons.forEach(button => {
            const text = button.textContent.trim();
            const row = button.closest('tr');
            const processName = row?.querySelector('td:first-child')?.textContent.trim();
            
            if (processName && text) {
                const actionLabels = {
                    'Stop': `Arrêter le processus ${processName}`,
                    'Start': `Démarrer le service ${processName}`,
                    'Restart': `Redémarrer le service ${processName}`,
                    'Kill': `Terminer le processus ${processName}`
                };
                
                const label = actionLabels[text] || `${text} ${processName}`;
                button.setAttribute('aria-label', label);
                button.classList.add('accessible-button');
            }
        });
    }

    // 2. GRAPHIQUES ACCESSIBLES
    setupChartAccessibility() {
        // Surveiller les changements de graphique
        const chartSelector = document.getElementById('chartSelector');
        if (chartSelector) {
            chartSelector.addEventListener('change', (e) => {
                this.handleChartChange(e.target.value);
            });
        }

        // Ajouter des raccourcis clavier pour les graphiques
        this.setupChartKeyboardControls();
        
        // Initialiser la table de données
        this.setupChartDataTable();
    }

    handleChartChange(chartType) {
        this.currentChart = chartType;
        
        // Mettre à jour le titre
        const titleElement = document.getElementById('current-chart-title');
        if (titleElement) {
            const titles = {
                cpu: 'Graphique d\'utilisation CPU',
                memory: 'Graphique d\'utilisation mémoire',
                network: 'Graphique d\'utilisation réseau'
            };
            titleElement.textContent = titles[chartType] || 'Graphique système';
        }

        // Annoncer le changement
        const announcements = {
            cpu: 'Affichage du graphique d\'utilisation CPU',
            memory: 'Affichage du graphique d\'utilisation mémoire',
            network: 'Affichage du graphique d\'utilisation réseau'
        };
        
        if (window.accessibilityManager) {
            window.accessibilityManager.announceToScreenReader(
                announcements[chartType] || 'Graphique modifié'
            );
        }

        // Mettre à jour la table de données
        this.updateChartDataTable();
    }

    setupChartKeyboardControls() {
        const canvases = document.querySelectorAll('canvas[role="img"]');
        canvases.forEach(canvas => {
            canvas.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.toggleChartData();
                } else if (e.key === 'd' || e.key === 'D') {
                    e.preventDefault();
                    this.describeChart(canvas.id);
                }
            });
        });
    }

    setupChartDataTable() {
        // Créer la fonction toggle pour la table de données
        window.toggleChartData = () => {
            const table = document.getElementById('chart-data-table');
            const button = document.querySelector('[aria-controls="chart-data-table"]');
            
            if (table && button) {
                const isVisible = table.style.display !== 'none';
                
                table.style.display = isVisible ? 'none' : 'block';
                button.setAttribute('aria-expanded', !isVisible);
                button.querySelector('span').textContent = isVisible ? 'Voir les données' : 'Masquer les données';
                
                const message = isVisible ? 
                    'Table de données masquée' : 
                    'Table de données affichée - utilisez Tab pour naviguer';
                
                if (window.accessibilityManager) {
                    window.accessibilityManager.announceToScreenReader(message);
                }

                if (!isVisible) {
                    this.updateChartDataTable();
                }
            }
        };
    }

    updateChartDataTable() {
        const tbody = document.getElementById('chartDataTableBody');
        if (!tbody) return;

        const data = this.chartData[this.currentChart] || [];
        
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="2">Aucune donnée disponible</td></tr>';
            return;
        }

        // Prendre les 10 derniers points de données
        const recentData = data.slice(-10);
        
        tbody.innerHTML = recentData.map(point => {
            const time = new Date(point.recorded_at).toLocaleTimeString();
            const value = typeof point.usage === 'number' ? point.usage.toFixed(2) : point.usage;
            return `
                <tr>
                    <td>${time}</td>
                    <td>${value}%</td>
                </tr>
            `;
        }).join('');
    }

    describeChart(chartId) {
        const descriptions = {
            cpuChart: 'Graphique linéaire montrant l\'évolution de l\'utilisation CPU. L\'axe X représente le temps, l\'axe Y le pourcentage d\'utilisation de 0 à 100%.',
            memoryChart: 'Graphique linéaire montrant l\'évolution de l\'utilisation mémoire. L\'axe X représente le temps, l\'axe Y le pourcentage d\'utilisation de 0 à 100%.',
            networkChart: 'Graphique linéaire montrant l\'évolution du trafic réseau. L\'axe X représente le temps, l\'axe Y le pourcentage d\'utilisation de la bande passante.'
        };

        const description = descriptions[chartId] || 'Graphique système affichant des données en temps réel';
        
        if (window.accessibilityManager) {
            window.accessibilityManager.announceToScreenReader(description);
        }
    }

    // 3. MISES À JOUR DYNAMIQUES
    setupDynamicUpdates() {
        // Observer les changements dans les éléments live
        this.setupLiveRegionObserver();
        
        // Gérer les mises à jour des métriques
        this.setupMetricsUpdates();
    }

    setupLiveRegionObserver() {
        const liveElements = document.querySelectorAll('[aria-live]');
        liveElements.forEach(element => {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'childList' || mutation.type === 'characterData') {
                        this.handleLiveUpdate(element);
                    }
                });
            });

            observer.observe(element, { 
                childList: true, 
                subtree: true, 
                characterData: true 
            });
        });
    }

    handleLiveUpdate(element) {
        // Compter les éléments dans les tableaux pour annoncer les changements
        if (element.id === 'processesTableBody') {
            const count = element.querySelectorAll('tr:not(.loading-row)').length;
            if (count > 0) {
                this.announceProcessCount(count);
            }
        } else if (element.id === 'servicesTableBody') {
            const count = element.querySelectorAll('tr:not(.loading-row)').length;
            if (count > 0) {
                this.announceServiceCount(count);
            }
        }
    }

    announceProcessCount(count) {
        const message = `${count} processus ${count > 1 ? 'affichés' : 'affiché'}`;
        if (window.accessibilityManager) {
            window.accessibilityManager.announceToScreenReader(message);
        }
    }

    announceServiceCount(count) {
        const message = `${count} service${count > 1 ? 's' : ''} ${count > 1 ? 'affichés' : 'affiché'}`;
        if (window.accessibilityManager) {
            window.accessibilityManager.announceToScreenReader(message);
        }
    }

    // 4. RACCOURCIS CLAVIER
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Alt + raccourcis pour navigation rapide
            if (e.altKey) {
                switch(e.key) {
                    case '1':
                        e.preventDefault();
                        this.focusSection('processes');
                        break;
                    case '2':
                        e.preventDefault();
                        this.focusSection('services');
                        break;
                    case '3':
                        e.preventDefault();
                        this.focusSection('metrics-title');
                        break;
                    case 'c':
                        e.preventDefault();
                        this.switchToChart('cpu');
                        break;
                    case 'm':
                        e.preventDefault();
                        this.switchToChart('memory');
                        break;
                    case 'n':
                        e.preventDefault();
                        this.switchToChart('network');
                        break;
                }
            }

            // Ctrl + F pour focus sur la recherche de processus
            if (e.ctrlKey && e.key === 'f') {
                const processFilter = document.getElementById('processFilter');
                if (processFilter && !e.defaultPrevented) {
                    e.preventDefault();
                    processFilter.focus();
                    if (window.accessibilityManager) {
                        window.accessibilityManager.announceToScreenReader('Focus sur la recherche de processus');
                    }
                }
            }
        });

        // Ajouter des indications sur les raccourcis
        this.addKeyboardShortcutsHelp();
    }

    focusSection(sectionId) {
        const element = document.getElementById(sectionId) || document.querySelector(`[aria-labelledby="${sectionId}"]`);
        if (element) {
            element.focus();
            element.scrollIntoView({ behavior: 'smooth', block: 'start' });
            
            const sectionNames = {
                processes: 'section des processus',
                services: 'section des services',
                'metrics-title': 'section des métriques'
            };
            
            const message = `Navigation vers la ${sectionNames[sectionId] || 'section'}`;
            if (window.accessibilityManager) {
                window.accessibilityManager.announceToScreenReader(message);
            }
        }
    }

    switchToChart(chartType) {
        const selector = document.getElementById('chartSelector');
        if (selector) {
            selector.value = chartType;
            selector.dispatchEvent(new Event('change'));
        }
    }

    addKeyboardShortcutsHelp() {
        // Créer un bouton d'aide pour les raccourcis clavier
        const helpButton = document.createElement('button');
        helpButton.className = 'accessible-button keyboard-help-toggle';
        helpButton.innerHTML = `
            <i class="fas fa-keyboard" aria-hidden="true"></i>
            <span>Raccourcis clavier</span>
        `;
        helpButton.setAttribute('aria-label', 'Afficher l\'aide des raccourcis clavier');
        helpButton.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 999;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 50px;
            padding: 10px 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        `;

        helpButton.addEventListener('click', () => {
            this.showKeyboardHelp();
        });

        document.body.appendChild(helpButton);
    }

    showKeyboardHelp() {
        const helpModal = document.createElement('div');
        helpModal.className = 'keyboard-help-modal';
        helpModal.setAttribute('role', 'dialog');
        helpModal.setAttribute('aria-labelledby', 'keyboard-help-title');
        helpModal.setAttribute('aria-modal', 'true');
        helpModal.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            border: 2px solid #007bff;
            border-radius: 8px;
            padding: 20px;
            z-index: 1001;
            max-width: 500px;
            max-height: 70vh;
            overflow-y: auto;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        `;

        helpModal.innerHTML = `
            <h2 id="keyboard-help-title">Raccourcis clavier</h2>
            <div class="keyboard-shortcuts">
                <h3>Navigation</h3>
                <ul>
                    <li><kbd>Alt + 1</kbd> : Aller aux processus</li>
                    <li><kbd>Alt + 2</kbd> : Aller aux services</li>
                    <li><kbd>Alt + 3</kbd> : Aller aux métriques</li>
                    <li><kbd>Ctrl + F</kbd> : Rechercher un processus</li>
                </ul>
                
                <h3>Graphiques</h3>
                <ul>
                    <li><kbd>Alt + C</kbd> : Graphique CPU</li>
                    <li><kbd>Alt + M</kbd> : Graphique mémoire</li>
                    <li><kbd>Alt + N</kbd> : Graphique réseau</li>
                    <li><kbd>Entrée/Espace</kbd> : Afficher données (sur graphique)</li>
                    <li><kbd>D</kbd> : Décrire le graphique</li>
                </ul>
                
                <h3>Général</h3>
                <ul>
                    <li><kbd>Tab</kbd> : Navigation suivante</li>
                    <li><kbd>Shift + Tab</kbd> : Navigation précédente</li>
                    <li><kbd>Échap</kbd> : Fermer les dialogues</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin-top: 20px;">
                <button class="accessible-button" onclick="this.closest('.keyboard-help-modal').remove(); document.body.classList.remove('modal-open');">
                    Fermer
                </button>
            </div>
        `;

        // Overlay
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
        `;
        
        overlay.addEventListener('click', () => {
            helpModal.remove();
            overlay.remove();
            document.body.classList.remove('modal-open');
        });

        document.body.appendChild(overlay);
        document.body.appendChild(helpModal);
        document.body.classList.add('modal-open');
        
        // Focus sur le premier élément focusable
        helpModal.querySelector('button').focus();

        if (window.accessibilityManager) {
            window.accessibilityManager.announceToScreenReader('Aide des raccourcis clavier affichée');
        }
    }

    // 5. MÉTHODES UTILITAIRES
    updateChartData(chartType, data) {
        if (this.chartData[chartType]) {
            this.chartData[chartType] = data;
            
            // Mettre à jour la table si elle est visible et correspond au graphique actuel
            if (this.currentChart === chartType) {
                this.updateChartDataTable();
            }
        }
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    // Attendre que l'AccessibilityManager soit disponible
    setTimeout(() => {
        window.dashboardAccessibility = new DashboardAccessibility();
        console.log('✅ Accessibilité Dashboard initialisée');
    }, 500);
});

// Export pour utilisation globale
window.DashboardAccessibility = DashboardAccessibility;
