from siteapp.enums.base import BaseEnum

class ComponentTypeEnum(BaseEnum):
    HARDWARE = "hardware"
    SOFTWARE = "software"
    SERVICE = "service"
    POLICY = "policy"
    PROCESS = "process"
    PROCEDURE = "procedure"

class ComponentStateEnum(BaseEnum):
    UNDER_DEVELOPMENT = "under-development"
    OPERATIONAL = "operational"
    DISPOSITION = "disposition"
    OTHER = "other"
