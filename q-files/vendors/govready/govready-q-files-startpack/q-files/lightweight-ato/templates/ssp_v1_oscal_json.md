id: ssp_v1_oscal_json
format: json
title: SSP v1 (OSCAL/JSON)
...
{
    "system-security-plan": {
        "uuid": "{{ oscal.uuid }}",
        "metadata": {
            "title": "{{ project.system_info.system_name }}",
            "last-modified": "{{ oscal.last_modified }}",
            "version": "{{ oscal.version }}",
            "oscal-version": "{{ oscal.oscal_version }}"
        },
        "import-profile": {
            "href": "{{ oscal.profile }}"
        },
        "system-characteristics": {
            "system-ids": [
                {
                    "id": "{{ oscal.system_id }}"
                }
            ],
            "system-name": "{{ project.system_info.system_name }}",
            "system-name-short": "{{ project.system_info.system_short_name }}",
            "description": "{{ project.system_info.system_description }}",
            "security-sensitivity-level": "{{ project.fisma_level.fisma_level }}",
            "system-information": {
                "information-types": {
                    "%for": "information_type in oscal.information_types",
                    "%loop": {
                        "title": "{{ information_type.title }}",
                        "description": "{{ information_type.description }}",
                        "confidentiality-impact": {
                            "base": "{{ information_type.confidentiality_impact }}"
                        },
                        "integrity-impact": {
                            "base": "{{ information_type.integrity_impact }}"
                        },
                        "availability-impact": {
                            "base": "{{ information_type.availability_impact }}"
                        }
                    }
                }
            },
            "security-impact-level": {
                "security-objective-confidentiality": "{{ oscal.system_security_impact_level_confidentiality }}",
                "security-objective-integrity": "{{ oscal.system_security_impact_level_integrity }}",
                "security-objective-availability": "{{ oscal.system_security_impact_level_availability }}"
            },
            "status": {
                "state": "{{ oscal.system_operating_status }}"
            },
            "authorization-boundary": {
                "description": "{{ oscal.system_authorization_boundary }}"
            }
        },
        "system-implementation": {
            "users": {
                "%dict": "user in project.system_info_technical.security_impact_users",
                "%value": {
                    "%key": "{{ oscal.make_uuid() }}",
                    "title": "{{ user.answer['Role'] }}"
                }
            },
            "components": {
                "%dict": "component in oscal.components",
                "%value": {
                    "%key": "{{ component.uuid }}",
                    "type": "{{ component.type }}",
                    "title": "{{ component.title }}",
                    "description": "{{ component.description }}",
                    "status": {
                        "state": "{{ component.state }}"
                    }
                }
            }
        },
        "control-implementation": {
            "description": "Control implementations",
            "implemented-requirements": {
                "%for": "requirement in oscal.implemented_requirements",
                "%loop": {
                    "uuid": "{{ requirement.uuid }}",
                    "control-id": "{{ requirement.control_id }}",
                    "parameter-settings": {
                        "%dict": "setting in requirement.parameter_settings",
                        "%value": {
                            "%key": "{{ setting.param_id }}",
                            "values": ["{{ setting.value }}"]
                        }
                    },
                    "statements": {
                        "%dict": "statement in requirement.statements",
                        "%value": {
                            "%key": "{{ statement.id }}",
                            "uuid": "{{ statement.uuid }}",
                            "by-components": {
                                "%dict": "by_component in statement.by_components",
                                "%value": {
                                    "%key": "{{ by_component.component_uuid }}",
                                    "uuid": "{{ by_component.uuid }}",
                                    "description": "{{ by_component.description }}"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
