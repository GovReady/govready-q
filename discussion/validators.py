import os
import mimetypes

import filetype
import magic
from django.http import JsonResponse

# Dictionary of valid extensions and content types
VALID_EXTS = {
    ".zip": ("application/zip",),
    ".pdf": ("application/pdf",),
    ".png": ("image/png",),
    ".jpg": ("image/jpeg",),
    ".doc": ("application/msword",),
    ".docx": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document",
              "application/zip"),
    ".xls": ("application/vnd.ms-excel",),
    ".xlsx": ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
              "application/zip"),
    ".csv": ("application/csv", "text/csv", "text/plain"),
    ".ppt": ("application/vnd.ms-powerpoint",),
    ".pptx": ("application/vnd.openxmlformats-officedocument.presentationml.presentation",
              "application/zip"),
    ".txt": ("text/plain",),
    ".md": ("text/markdown", "text/plain"),
    ".yaml": ("text/plain",),
    ".yml": ("text/plain",),
}
# Exceptions for content types that may have multiple extensions
CONTENTTYPE_EXCEPTIONS = {
    "application/vnd.ms-powerpoint": (".ppt", ),
    "application/zip": (".docx", ".xlsx", ".pptx", ".zip",),
    "application/vnd.ms-excel": (".xls", ".xlb",),
    "text/plain": (".csv",".txt", ".yaml", ".yml", ".md")
}

def validate_file_extension(file):
    """
    Validates the file extension and type
    """

    for chunk in file.chunks():
        # Archive and image filetypes will display chunks since it only looks at the first 261 bytes
        filechunk = filetype.guess(chunk)
        err_msg = f"The file {file.name} does not have a supported file type"


        # Mime and extension
        filechunk_content_type = filechunk.mime if filechunk is not None else None
        filechunk_extension = f".{filechunk.extension}" if filechunk is not None else None

        if filechunk_content_type is None or filechunk_extension is None:
            # Get mimetype with id_buffer
            with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as buf:
                filechunk_content_type = buf.id_buffer(chunk)
                filechunk_extension = mimetypes.guess_extension(filechunk_content_type)

        _file, file_ext = os.path.splitext(file.name)

        # Mixmatch file given extension and guessed extension
        if file_ext != filechunk_extension:
            # Check if there is an exception for file extension
            if not (filechunk_content_type in CONTENTTYPE_EXCEPTIONS
                    and file_ext in CONTENTTYPE_EXCEPTIONS[filechunk_content_type]):
                return JsonResponse(status=400, data={'status': 'error', 'message': err_msg})

        # If it is not a valid mime or extension then return http response with error message.
        is_match = False
        if file_ext in VALID_EXTS:
            is_match = (filechunk_content_type in VALID_EXTS[file_ext])

        if not is_match:
            return JsonResponse(status=400, data={'status': 'error',
                                                  'message': err_msg})
        break # Stop after one chunk
    return None
