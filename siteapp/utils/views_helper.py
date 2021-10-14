from api.siteapp.serializers.projects import DetailedProjectsSerializer


def project_context(project):
    # talk about re-naming function to accurately reflect functionality
    return {
        "project": DetailedProjectsSerializer(project).data,
        "urls": {
            "home": project.get_absolute_url(),
            "controls": f"/systems/{project.system_id}/controls/selected",
            "components": f"/systems/{project.system_id}/components/selected",
            "poa_ms": f'/systems/{project.system_id}/poams',
            "deployments": f'/systems/{project.system_id}/deployments',
            "assesments": f"/systems/{project.system_id}/assessments",
            "export_project": f"/systems/{project.id}/export",
            "settings": f"{project.get_absolute_url()}/settings",
            "review": f'{project.get_absolute_url()}/list',
            "documents": f'{project.get_absolute_url()}/outputs',
            "apidocs": f'{project.get_absolute_url()}/api',
            "Greg": f'{project.get_absolute_url()}/api'
        }
        }