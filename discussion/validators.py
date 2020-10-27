import os
from django.core.exceptions import ValidationError
def validate_file_extension(file):
    """
    Validates the file extension and type
    """

    valid_extensions = ['.pdf', '.png', '.jpg']
    valid_content_types = ['application/pdf', 'image/png', 'image/jpg']

    ext = os.path.splitext(file.name)[1]  # [0] returns path+filename
    if ext.lower() not in valid_extensions:
        raise ValidationError(f'{ext.lower()} is not a supported file extension.')

    content_type = file.content_type
    if content_type not in valid_content_types:
        raise ValidationError(f'{content_type} is not a supported file content type.')


