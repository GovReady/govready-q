from siteapp.enums.base import BaseEnum


class StatementTypeEnum(BaseEnum):
    CONTROL_IMPLEMENTATION = "control_implementation"
    CONTROL_IMPLEMENTATION_LEGACY = "control_implementation_legacy"
    CONTROL_IMPLEMENTATION_PROTOTYPE = "control_implementation_prototype"
    ASSESSMENT_RESULT = "assessment_result"
    POAM = "POAM"
    SECURITY_SENSITIVITY_LEVEL = "security_sensitivity_level"
    SECURITY_IMPACT_LEVEL = "security_impact_level"
    COMPONENT_APPROVAL_CRITERIA = "component_approval_criteria"
