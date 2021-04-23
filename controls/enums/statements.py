from siteapp.enums.base import BaseEnum


class StatementTypeEnum(BaseEnum):
    CONTROL_IMPLEMENTATION = "control_implementation"
    CONTROL_IMPLEMENTATION_PROTOTYPE = "control_implementation_prototype"
    ASSESSMENT_RESULT = "assessment_result"
    POAM = "POAM"
    FISMA_IMPACT_LEVEL = "fisma_impact_level"
