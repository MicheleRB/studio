"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'Studio.dashboard.CustomIndexDashboard'
"""

from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)


        # append an app list module for "Applications"
        self.children.append(modules.ModelList(
            _('Avvocato Sara Rossi'),
            collapsible=True,
            column=1,
            css_classes=('collapse closed',),
            exclude=('django.contrib.*','StudioLegale.models.Perce*', 'StudioLegale.models.Studi*', ),
        ))

        self.children.append(modules.LinkList(
            _('Report'),
            column=1,
            children=(
                {
                    'title': 'Report trimestrale',
                    'url': '/',
                    'external': False,
                    'description': 'Report trimestrale',
                },
            )
        ))

        self.children.append(modules.ModelList(
            _('Parametrizzazioni'),
            collapsible=True,
            column=2,
            css_classes=('collapse closed',),
            models=('StudioLegale.models.Perce*', 'StudioLegale.models.Studi*',),
            exclude=('django.contrib.*',),
        ))



        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=5,
            collapsible=False,
            column=3,
        ))
