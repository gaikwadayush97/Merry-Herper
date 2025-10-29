# Replacement for Python 3.13 imghdr removal
import mimetypes
import os

def what(file_path):
    """Minimal replacement for imghdr.what()."""
    if not os.path.exists(file_path):
        return None
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and mime_type.startswith("image/"):
        return mime_type.split("/")[-1]
    return None
