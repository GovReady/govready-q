from import_export import resources, fields
from controls.models import Statement, Element
from import_export.widgets import ForeignKeyWidget

class StatementResource(resources.ModelResource):
    """
    Provides the resource for statements and their associated system elements(components)
    """
    element_id = fields.Field(
        column_name='element_id',
    attribute='producer_element',
        widget=ForeignKeyWidget(model=Element),
    )
    element_name = fields.Field(
        column_name='element_name',
    attribute='producer_element',
        widget=ForeignKeyWidget(model=Element, field='name'),
    )
    element_description = fields.Field(
        column_name='element_description',
    attribute='producer_element',
        widget=ForeignKeyWidget(model=Element, field='description'),
    )
    element_uuid = fields.Field(
        column_name='element_uuid',
    attribute='producer_element',
        widget=ForeignKeyWidget(model=Element, field='uuid'),
    )
    element_type = fields.Field(
        column_name='element_type',
    attribute='producer_element',
        widget=ForeignKeyWidget(model=Element, field='element_type'),
    )
    class Meta:
        model = Statement