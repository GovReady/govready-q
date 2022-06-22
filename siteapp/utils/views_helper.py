from api.siteapp.serializers.projects import DetailedProjectsSerializer
from django.db import transaction
from siteapp.models import Project, ProjectMembership
from controls.models import Element, System, Statement, Deployment

import logging
logging.basicConfig()
import structlog
from structlog import get_logger
from structlog.stdlib import LoggerFactory

structlog.configure(logger_factory=LoggerFactory())
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = get_logger()

def project_context(project, is_project_page=False):
    # talk about re-naming function to accurately reflect functionality
    return {
        "is_project_page": is_project_page,
        "project": DetailedProjectsSerializer(project).data,
        "urls": {
            "home": project.get_absolute_url(),
            "controls": f"/systems/{project.system_id}/controls/selected",
            "components": f"/systems/{project.system_id}/components/selected",
            "poa_ms": f'/systems/{project.system_id}/poams',
            # "poa_ms": f'/systems/{project.system_id}/aspen/summary/poams',
            "deployments": f'/systems/{project.system_id}/deployments',
            "assesments": f"/systems/{project.system_id}/assessments",
            "export_project": f"/systems/{project.id}/export",
            "settings": f"{project.get_absolute_url()}/settings",
            "review": f'{project.get_absolute_url()}/list',
            "documents": f'{project.get_absolute_url()}/outputs',
            "apidocs": f'{project.get_absolute_url()}/api'
        }
    }

def get_compliance_apps_catalog(organization, userid):
    # Load the compliance apps available to the given organization.

    from guidedmodules.models import AppVersion
    from collections import defaultdict

    appvers = AppVersion.get_startable_apps(organization, userid)

    # Group the AppVersions into apps. An app is a unique source+appname pair.
    # For each app, one or more versions may be available.
    apps = defaultdict(lambda: [])
    for av in appvers:
        apps[(av.source, av.appname)].append(av)

    # Replace each app entry with a list of AppVersions sorted by reverse database
    # row created date (since we don't necessarily have sortable version numbers).
    apps = [
        sorted(appvers, key=lambda av: av.created, reverse=True)
        for appvers in apps.values()
    ]

    # Collect catalog display metadata for each app from the most recent version
    # of each app.
    apps = [
        render_app_catalog_entry(appvers[0], appvers, organization)
        for appvers in apps
    ]

    return apps

def get_compliance_apps_catalog_for_user(user):
    # Each organization that the user is in sees a different set of compliance
    # apps. Since a user may be a member of multiple organizations, merge the
    # catalogs across all of the organizations they are a member of, but
    # remember which organizations generated which apps.
    from siteapp.models import Organization
    catalog = {}
    for org in Organization.get_all_readable_by(user):
        apps = get_compliance_apps_catalog(org, user.id)
        for app in apps:
            # Add to merged catalog.
            catalog.setdefault(app['key'], app)

            # Merge organization list.
            catalog[app["key"]]["organizations"].add(org)

    # Turn the organization sets into a list because the templates use |first.
    catalog = catalog.values()
    for app in catalog:
        # print("\n\n app",app)
        app["organizations"] = sorted(app["organizations"], key=lambda org: org.name)

    return catalog

def render_app_catalog_entry(appversion, appversions, organization):
    from guidedmodules.module_logic import render_content
    from guidedmodules.models import image_to_dataurl

    key = "{source}/{name}".format(source=appversion.source.slug, name=appversion.appname)

    catalog = appversion.catalog_metadata
    if not isinstance(catalog, dict): catalog = {}

    app_module = appversion.modules.filter(module_name="app").first()

    return {
        # app identification
        "appversion_id": appversion.id,
        "appsource_id": appversion.source.id,
        "key": key,

        # main display fields
        "title": catalog.get('title') or appversion.appname,
        "description": {  # rendered as markdown
            "short": render_content(
                {
                    "template": catalog.get("description", {}).get("short") or "",
                    "format": "markdown",
                },
                None,
                "html",
                "%s %s" % (key, "short description")
            ),
            "long": render_content(
                {
                    "template": catalog.get("description", {}).get("long")
                                or catalog.get("description", {}).get("short")
                                or "",
                    "format": "markdown",
                },
                None,
                "html",
                "%s %s" % (key, "short description")
            )
        },

        # catalog page metadata
        "categories": catalog.get("categories", [catalog.get("category")]),
        "search_haystak": "".join([  # free text search uses this
            appversion.appname,
            catalog.get('title', ""),
            catalog.get("vendor", ""),
            catalog.get("description", {}).get("short", ""),
            catalog.get("description", {}).get("long", ""),
        ]),
        # "icon": None if "icon" not in catalog
        # else image_to_dataurl(appversion.get_asset(catalog["icon"]), 128),
        "icon": None,
        "protocol": app_module.spec.get("protocol", []) if app_module else [],

        # catalog detail page metadata
        "vendor": catalog.get("vendor"),
        "vendor_url": catalog.get("vendor_url"),
        "source_url": catalog.get("source_url"),
        "status": catalog.get("status"),
        "version": appversion.version_number,
        "recommended_for": catalog.get("recommended_for", []),

        # versions that can be started
        "versions": appversions,

        # organizations that can launch this app
        "organizations": {organization},

        # placeholder for future logic
        "authz": "none",
    }

def start_app(appver, organization, user, folder, task, q, portfolio):
    # Begin a transaction to create the Module and Task instances for the app.
    with transaction.atomic():
        # Create project.
        project = Project()
        project.organization = organization
        project.portfolio = portfolio

        # Save and add to folder
        project.save()
        project.set_root_task(appver.modules.get(module_name="app"), user)
        # Update default name to be unique by using project.id
        project.root_task.title_override = project.title + " " + str(project.id)
        project.root_task.save()
        if folder:
            folder.projects.add(project)

        # Log start app / new project
        logger.info(
            event="start_app",
            object={"task": "project", "id": project.root_task.id, "title": project.root_task.title_override},
            user={"id": user.id, "username": user.username}
        )
        logger.info(
            event="new_project",
            object={"object": "project", "id": project.id, "title": project.title},
            user={"id": user.id, "username": user.username}
        )

        # Create a new System element and link to project?
        # Top level apps should be linked to a system
        # Create element to serve as system's root_element
        # Element names must be unique. Use unique project title set above.
        element = Element()
        element.name = project.title
        element.element_type = "system"
        element.save()
        # Create system
        system = System(root_element=element)
        system.save()
        system.add_event("SYS", f"Created new System in GovReady based on template '{appver.catalog_metadata['title']}'.")
        system.info == {
            "created_from_template": project.title,
            "system_description": "New system",

            "id": system.id,
            "other_id": "~",
            "name": project.root_task.title_override,
            "organization_name": "~",
            "aka": "~",
            "impact": "~",
            "status": "Planned",
            "type": "~",
            "created": "~",
            "hosting_facility": "~",
            "next_audit": "~",
            "next_scan": "~", #"05/01/22",
            "security_scan": "~",
            "pen_test": "~", #"Scheduled for 05/05/22",
            "config_scan": "~",
            "purpose": "~",
            "vuln_new_30days": "~",
            "vuln_new_rslvd_30days": "~",
            "vuln_90days": "~",
            "risk_score": "~",
            "score_1": "~",
            "score_2": "~",
            "score_3": "~",
            "score_4": "~",
            "score_5": "~",
        }
        system.save()
        # Link system to project
        project.system = system
        project.save()
        # Log start app / new project
        logger.info(
            event="new_element new_system",
            object={"object": "element", "id": element.id, "name": element.name},
            user={"id": user.id, "username": user.username}
        )

        # Add user as the first admin of project.
        ProjectMembership.objects.create(
            project=project,
            user=user,
            is_admin=True)
        # Grant owner permissions on root_element to user
        element.assign_owner_permissions(user)
        # Log ownership assignment
        logger.info(
            event="new_element new_system assign_owner_permissions",
            object={"object": "element", "id": element.id, "name": element.name},
            user={"id": user.id, "username": user.username}
        )
        system.assign_owner_permissions(user)
        # Log ownership assignment
        logger.info(
            event="new_system assign_owner_permissions",
            object={"object": "system", "id": system.root_element.id, "name": system.root_element.name},
            user={"id": user.id, "username": user.username}
        )

        # Add default deployments to system
        deployment = Deployment(name="Blueprint", description="Reference system archictecture design", system=system)
        deployment.save()
        deployment = Deployment(name="Dev", description="Development environment deployment", system=system)
        deployment.save()
        deployment = Deployment(name="Stage", description="Stage/Test environment deployment", system=system)
        deployment.save()
        deployment = Deployment(name="Prod", description="Production environment deployment", system=system)
        deployment.save()

        # Assign default control catalog and control profile
        # Use from App catalog settings
        try:
            # Get default catalog key
            parameters = project.root_task.module.app.catalog_metadata['parameters']
            catalog_key = [p for p in parameters if p['id'] == 'catalog_key'][0]['value']
            # Get default profile/baseline
            baseline_name = [p for p in parameters if p['id'] == 'baseline'][0]['value']
            # Assign profile/baseline
            assign_results = system.root_element.assign_baseline_controls(user, catalog_key, baseline_name)
            # Log result if successful
            if assign_results:
                # Log start app / new project
                logger.info(
                    event="assign_baseline",
                    object={"object": "system", "id": system.root_element.id, "title": system.root_element.name},
                    baseline={"catalog_key": catalog_key, "baseline_name": baseline_name},
                    user={"id": user.id, "username": user.username}
                )
        except:
            # TODO catch error and return error message
            print("[INFO] App could not assign catalog_key or profile/baseline.\n")

        # Assign default organization components for a system
        if user.has_perm('change_system', system):
            # Get the components from the import records of the app version
            import_records = appver.input_artifacts.all()
            for import_record in import_records:
                add_selected_components(system, import_record)

        else:
            # User does not have write permissions
            logger.info(
                event="change_system permission_denied",
                user={"id": user.id, "username": user.username}
            )

        # TODO: Assign default org parameters

        if task and q:
            # It will also answer a task's question.
            ans, is_new = task.answers.get_or_create(question=q)
            ansh = ans.get_current_answer()
            if q.spec["type"] == "module" and ansh and ansh.answered_by_task.count():
                raise ValueError('The question %s already has an app associated with it.'
                                 % q.spec["title"])
            ans.save_answer(
                None,  # not used for module-type questions
                list([] if not ansh else ansh.answered_by_task.all()) + [project.root_task],
                None,
                user,
                "web")

        return project
