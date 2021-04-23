from siteapp.enums.base import BaseEnum


class StatementTypeEnum(BaseEnum):
    control_implementation = "control_implementation"
    control_implementation_prototype = "control_implementation_prototype"
    assessment_result = "assessment_result"
    POAM = "POAM"
    fisma_impact_level = "fisma_impact_level"
