from siteapp.enums.base import BaseEnum


class RepoTypeEnum(BaseEnum):
    MAIN_CODEBASE = "main_codebase"
    ADDITIONAL_CODEBASE = "additional_codebase"
    COMPLIANCE = "compliance"
    MAIN_DOCUMENTATION = "main_documentation"
    ADDITIONAL_DOCUMENTATION = "additional_documentation"
    OTHER = "other"
