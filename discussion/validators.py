import filetype
from django.http import JsonResponse


def validate_file_extension(file):
    """
    Validates the file extension and type
    """

    valid_extensions = ['.zip', '.pdf', '.png', '.jpg', ".doc", ".docx", ".vsd", ".xls", ".xlsx", ".csv", ".ppt", ".pptx"]
    valid_content_types = ['application/zip', 'application/pdf', 'image/png', 'image/jpeg', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.visio', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv', 'application/csv', 'application/vnd.ms-powerpoint','application/vnd.openxmlformats-officedocument.presentationml.presentation']
    for chunk in file.chunks():
        # Archive and image filetypes will display chunks since it only looks at the first 261 bytes
        filechunk = filetype.guess(chunk)
        # mime and extension
        filechunk_content_type = filechunk.mime if filechunk is not None else None
        filechunk_extension = f".{filechunk.extension}" if filechunk is not None else None

        if filechunk_content_type == None or filechunk_extension == None:

            import mimetypes, magic
            # Get mimetype with id_buffer
            with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
                filechunk_content_type = m.id_buffer(chunk)
                filechunk_extension = mimetypes.guess_extension(filechunk_content_type) if filechunk_content_type != 'application/csv' else '.csv'
        # If it is not a valid mime or extension that return http response with error message.
        if filechunk_content_type not in valid_content_types or filechunk_extension not in valid_extensions:
            return JsonResponse(status=400, data={'status': 'error',
                                                  'message': f"The file {file.name} does not have a supported file type"})
