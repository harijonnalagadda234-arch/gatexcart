from io import BytesIO
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.utils.text import get_valid_filename

MAX_IMAGE_BYTES = 10 * 1024 * 1024
ALLOWED_FORMATS = {"JPEG"}

def validate_jpeg_image(upload):
    """Accept genuine JPEG/JPG images only, with a 10 MB upload limit."""
    if not upload:
        return
    if upload.size > MAX_IMAGE_BYTES:
        raise ValidationError("Image must be 10 MB or smaller.")
    name = (getattr(upload, "name", "") or "").lower()
    if not name.endswith((".jpg", ".jpeg")):
        raise ValidationError("Upload a JPG or JPEG image only.")
    try:
        upload.seek(0)
        image = Image.open(upload)
        image.verify()
        upload.seek(0)
        if image.format not in ALLOWED_FORMATS:
            raise ValidationError("The uploaded file is not a valid JPEG image.")
    except ValidationError:
        raise
    except Exception:
        raise ValidationError("The uploaded file is not a readable JPEG image.")
    finally:
        try:
            upload.seek(0)
        except Exception:
            pass

def fit_and_reencode_jpeg(field_file, size, quality=92):
    """Center-crop to an exact pixel size and re-encode as optimized JPEG."""
    if not field_file:
        return None
    try:
        field_file.open("rb")
        with Image.open(field_file) as source:
            source.load()
            image = ImageOps.exif_transpose(source).convert("RGB")
            image = ImageOps.fit(image, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            output = BytesIO()
            image.save(output, format="JPEG", quality=quality, optimize=True, progressive=True, subsampling=0)
            output.seek(0)
            original_name = get_valid_filename(field_file.name.rsplit("/", 1)[-1])
            stem = original_name.rsplit(".", 1)[0] or "image"
            return ContentFile(output.read(), name=f"{stem}.jpg")
    finally:
        try:
            field_file.close()
        except Exception:
            pass
