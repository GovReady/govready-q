import filetype
from django.http import JsonResponse


def validate_file_extension(file):
    """
    Validates the file extension and type
    """

    valid_extensions = ['pdf', 'png', 'jpg', "doc", "docx", "vsd", "xls", "xlsx", "csv", "yml", "ppt", "pptx"]
    valid_content_types = ['application/pdf', 'image/png', 'image/jpg', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.visio', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv', 'text/x-yaml', 'application/x-yaml', 'application/vnd.ms-powerpoint','application/vnd.openxmlformats-officedocument.presentationml.presentation']
    for chunk in file.chunks():
        # Archive and image filetypes will display chunks since it only looks at the first 261 bytes
        filechunk = filetype.guess(chunk)
        # mime and extension
        filechunk_content_type = filechunk.mime if filechunk is not None else None
        filechunk_extension = filechunk.extension if filechunk is not None else None
        # If it is not a valid mime or extension that return http response with error message.
        if filechunk is None or filechunk_content_type not in valid_content_types or filechunk_extension not in valid_extensions:
            return JsonResponse(status=400, data={'status': 'error',
                                                  'message': f"The file {file.name} does not have a supported file type"})
