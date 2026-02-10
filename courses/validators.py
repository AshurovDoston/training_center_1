from django.core.exceptions import ValidationError


def validate_video_file_size(file):
    """
    Validate that the uploaded video file does not exceed 500MB.

    Django validators are callables that take a value and raise
    ValidationError if the value is invalid. This validator runs
    automatically when the model form is validated (e.g., in Django
    Admin or any ModelForm).

    NOTE: The file is already fully uploaded to the server by the time
    this validator runs. For true upload-size limits at the network
    layer, configure your web server (Nginx: client_max_body_size).
    """
    max_size_mb = 500
    max_size_bytes = max_size_mb * 1024 * 1024

    if file.size > max_size_bytes:
        raise ValidationError(
            f"Video file size cannot exceed {max_size_mb}MB. "
            f"Your file is {file.size / (1024 * 1024):.1f}MB."
        )
