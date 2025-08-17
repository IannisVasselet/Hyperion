from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard

class CustomIndexDashboard(Dashboard):
    columns = 3

    def init_with_context(self, context):
        self.available_children.append(modules.ModelList)
        self.available_children.append(modules.RecentActions)
        self.available_children.append(modules.Feed)

        # Colonne 1
        self.children.append(modules.ModelList(
            'Administration',
            models=('django.contrib.auth.*',)
        ))

        # Colonne 2
        self.children.append(modules.ModelList(
            'Applications',
            models=('api.*',)
        ))

        # Colonne 3
        self.children.append(modules.RecentActions(
            'Actions Récentes',
            10
        ))