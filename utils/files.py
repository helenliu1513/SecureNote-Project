"""
SecureNote – File Utilities
=============================
Helper functions for serving uploaded or generated files.
"""

import os
from flask import send_file, abort

from config import Config


def download_file(filename: str):
    """Serve a file from the uploads directory.

    Parameters
    ----------
    filename : str
        Name (or relative path) of the requested file.
    """
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)

    if not os.path.isfile(filepath):
        abort(404, description="File not found")

    return send_file(filepath, as_attachment=True)
