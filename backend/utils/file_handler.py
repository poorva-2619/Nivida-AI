import os
from fastapi import UploadFile, HTTPException, status
from typing import List

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx", "jpg", "jpeg", "png"}
MAX_FILE_SIZE_MB = 20
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

def get_extension(filename: str) -> str:
    return filename.split(".")[-1].lower() if "." in filename else ""

def validate_file(file: UploadFile):
    ext = get_extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {ALLOWED_EXTENSIONS}"
        )

def save_upload_file(file: UploadFile, sub_directory: str) -> str:
    validate_file(file)
    
    target_dir = os.path.join(UPLOAD_DIR, sub_directory)
    os.makedirs(target_dir, exist_ok=True)
    
    file_path = os.path.join(target_dir, file.filename)
    
    file_size = 0
    with open(file_path, "wb") as buffer:
        while chunk := file.file.read(1024 * 1024):
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE_BYTES:
                buffer.close()
                os.remove(file_path)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File size exceeds {MAX_FILE_SIZE_MB}MB limit."
                )
            buffer.write(chunk)
            
    file.file.seek(0)
    return file_path.replace("\\", "/")

def save_tender_file(tender_id: str, file: UploadFile) -> str:
    return save_upload_file(file, str(tender_id))

def save_vendor_submission_files(submission_id: str, files: List[UploadFile]) -> List[str]:
    saved_paths = []
    sub_dir = os.path.join("vendor", str(submission_id))
    for f in files:
        path = save_upload_file(f, sub_dir)
        saved_paths.append(path)
    return saved_paths
