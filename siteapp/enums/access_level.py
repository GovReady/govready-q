from siteapp.enums.base import BaseEnum


class AccessLevelEnum(BaseEnum):
    READ_ONLY = "Read-only Access"
    WRITE_ONLY = "Write-only Access"
    READ_WRITE = "Full Access"
