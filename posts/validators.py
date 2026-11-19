from django.core.exceptions import ValidationError

PDF_MAGIC = b'%PDF'
PNG_MAGIC = b'\x89PNG'
JPEG_MAGIC = b'\xff\xd8\xff'
WEBP_MAGIC = b'RIFF'
EXE_MAGIC = b'MZ'

MAX_FILE_SIZE_MB = 10


def validate_academic_attachment(file):
    """
    Validates academic document uploads against size constraints and binary file headers.
    Inspects stream magic bytes to prevent disguised executable binaries (.exe/.dll).
    """
    if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValidationError(f"File size exceeds the {MAX_FILE_SIZE_MB}MB limit.")

    initial_position = file.tell()
    file.seek(0)
    header = file.read(16)
    file.seek(initial_position)

    if header.startswith(EXE_MAGIC):
        raise ValidationError("Security Alert: Executable binaries (.exe/.dll) are strictly forbidden.")

    filename = file.name.lower()
    if filename.endswith('.pdf'):
        if not header.startswith(PDF_MAGIC):
            raise ValidationError("Invalid file content: The file extension says .pdf, but the binary signature is not a valid PDF.")
    elif filename.endswith(('.doc', '.docx', '.txt')):
        pass
    else:
        raise ValidationError("Unsupported file format. Please upload a PDF, DOC, or TXT file.")


def validate_image_upload(file):
    """
    Validates image uploads against size limits and authentic image magic byte signatures.
    """
    if file.size > 5 * 1024 * 1024:
        raise ValidationError("Image size exceeds the 5MB limit.")

    initial_position = file.tell()
    file.seek(0)
    header = file.read(16)
    file.seek(initial_position)

    if header.startswith(EXE_MAGIC):
        raise ValidationError("Security Alert: Disguised executable files are forbidden.")

    valid_image = (
        header.startswith(PNG_MAGIC) or
        header.startswith(JPEG_MAGIC) or
        header.startswith(WEBP_MAGIC)
    )

    if not valid_image:
        raise ValidationError("Invalid image content: Corrupted or spoofed image signature.")
