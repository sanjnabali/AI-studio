import base64
from io import BytesIO
from PIL import Image
import mimetypes
import re
from datetime import datetime

def image_to_base64(img: Image.Image, format: str = "PNG") -> str:
    """
    Convert a PIL Image to a base64-encoded string.
    """
    buffered = BytesIO()
    img.save(buffered, format=format)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def base64_to_image(b64_string: str) -> Image.Image:
    """
    Convert a base64-encoded string to a PIL Image.
    """
    img_data = base64.b64decode(b64_string)
    return Image.open(BytesIO(img_data))

def validate_prompt(prompt: str, max_length: int = 200) -> bool:
    """
    Validate a prompt for length and allowed characters.
    """
    if not prompt or len(prompt) > max_length:
        return False
    # Optionally, restrict to printable characters
    if not re.match(r"^[\s\S]+$", prompt):
        return False
    return True

def allowed_file(filename: str, allowed_extensions=None) -> bool:
    """
    Check if the file has an allowed extension.
    """
    if allowed_extensions is None:
        allowed_extensions = {"png", "jpg", "jpeg", "gif", "pdf", "txt", "docx", "mp3", "mp4", "json", "csv"}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_mime_type(filename: str) -> str:
    """
    Guess the MIME type of a file based on its filename.
    """
    mime, _ = mimetypes.guess_type(filename)
    return mime or "application/octet-stream"

def current_timestamp() -> str:
    """
    Return the current UTC timestamp as an ISO string.
    """
    return datetime.utcnow().isoformat() + "Z"

def safe_filename(filename: str) -> str:
    """
    Sanitize a filename for safe storage.
    """
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)

# Example: You can add more helpers as your project grows!