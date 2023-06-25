"""
set_baseline_controls.py
    Django management control to assign or add additional baseline controls for project.

    Usage:   manage.py set_baseline_controls --project "project name" --username user \
                --baseline catalog:baseline --overlay catalog:baseline
    Example: manage.py set_baseline_controls --project "System Security Plan" --username admin \
                --baseline JSIG_rev4:moderate --overlay CNSSI_1253F_Privacy_Overlay:mmm CMMC_ver1:"level 1"
"""
from django.core.management.base import BaseCommand

from controls.enums.statements import StatementTypeEnum
from controls.models import Statement, ImportRecord
from controls.utilities import oscalize_control_id
from siteapp.models import User, Project, Organization
import os

import logging
logging.basicConfig()
import structlog
from structlog import get_logger
from structlog.stdlib import LoggerFactory

structlog.configure(logger_factory=LoggerFactory())
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = get_logger()

# Example:
# python3 manage.py set_baseline_controls --project "project name" --username user --baseline catalog:baseline --overlay catalog:baseline
# python3 manage.py set_baseline_controls --project "System Security Plan" --username admin --baseline JSIG_rev4:moderate --overlay CNSSI_1253F_Privacy_Overlay:mmm CMMC_ver1:"level 1"

class Command(BaseCommand):
    help = 'Assign or add additional baseline controls for project'

    def add_arguments(self, parser):
        parser.add_argument('--project', nargs='?')
        parser.add_argument('--username', nargs='?')
        parser.add_argument('--baseline', nargs='?')
        parser.add_argument('--overlay', nargs='+')

    def find(self, target, prop, array):
        for i in range(len(array)):
            if getattr(array[i], prop) == target:
                return array[i]

    def handle(self, *args, **options):
        debug = True
        try:
            system_name = options['project']
            if not system_name:
                system_name = 'System Security Plan'
        except:
            system_name = 'System Security Plan'

        # Get the org, user, and project name
        try:
            org     = Organization.objects.first()
            user    = User.objects.get(username=options['username'])
            project = Project.objects.filter(system__root_element__name=system_name).first()
            if project == None:
                raise Exception('Project not found')
            print(f'Org:{org}, user:{user}, project:{project.id}') if debug else False

        except Exception as e:
            print(f'Exception: {e}')
            exit()

        # Set baseline if not set
        # baseline_name = [p for p in parameters if p['id'] == 'baseline'][0]['value']
        # Assign profile/baseline
        try:
            baselines = options['baseline']
            if baselines:
                catalog_key,baseline_name = baselines.split(':')
                if catalog_key and baseline_name:
                    assign_results = project.system.root_element.assign_baseline_controls(user, catalog_key, baseline_name)
                    print(f'Added {catalog_key} baseline {baseline_name} results: {assign_results}') if debug else False

                if assign_results:
                    # Log assign_baseline
                    logger.info(
                        event="assign_baseline",
                        object={"object": "system", "id": project.system.root_element.id, "title": project.system.root_element.name},
                        baseline={"catalog_key": catalog_key, "baseline_name": baseline_name},
                        user={"id": user.id, "username": user.username}
                    )

            overlays = options['overlay']
            if overlays:
                for overlay in overlays:
                    overlay_key, overlay_name = overlay.split(':')
                    if overlay_key and overlay_name:
                        add_results = project.system.root_element.add_baseline_controls(user, overlay_key, overlay_name)
                        print(f'Added {overlay_key} baseline {overlay_name} results: {add_results}') if debug else False

                        if add_results:
                            # Log add_overlay
                            logger.info(
                                event="add_overlay",
                                object={"object": "system", "id": project.system.root_element.id, "title": project.system.root_element.name},
                                baseline={"catalog_key": overlay_key, "baseline_name": overlay_name},
                                user={"id": user.id, "username": user.username}
                            )

        except Exception as e:
            print(f'Exception: {e}')
            exit()
