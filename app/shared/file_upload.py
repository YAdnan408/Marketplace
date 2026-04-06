import os

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename: str) -> bool:
    """Return True if the file's extension is in the allowed set."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_extension(filename: str) -> str:
    """Return the lowercase extension of a filename (without the dot)."""
    return filename.rsplit(".", 1)[1].lower()


def save_upload(file, upload_folder: str, filename: str) -> str:
    """
    Save an uploaded FileStorage object to upload_folder/filename.
    Creates the folder if it does not already exist.
    Returns the saved filename.
    """
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, filename))
    return filename
