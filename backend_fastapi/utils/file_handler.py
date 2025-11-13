import os
import uuid
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from pathlib import Path
import magic  # python-magic library for MIME type detection

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {
    # Documents
    '.pdf': 'application/pdf',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.ppt': 'application/vnd.ms-powerpoint',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.xls': 'application/vnd.ms-excel',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    # Images
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.svg': 'image/svg+xml',
    '.gif': 'image/gif',
    # Text
    '.txt': 'text/plain',
    '.csv': 'text/csv',
}

def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()

def is_valid_file_type(filename: str, content_type: str) -> bool:
    ext = get_file_extension(filename)
    return ext in ALLOWED_EXTENSIONS and content_type in ALLOWED_EXTENSIONS.values()

async def save_upload_file(upload_file: UploadFile, entity_type: str, entity_id: Optional[int] = None) -> dict:
    if not upload_file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Check file size
    file_size = 0
    content = await upload_file.read()
    file_size = len(content)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE/1024/1024}MB")
    
    # Reset file pointer
    await upload_file.seek(0)
    
    # Detect MIME type
    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(content)
    
    if not is_valid_file_type(upload_file.filename, mime_type):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Create unique filename
    ext = get_file_extension(upload_file.filename)
    unique_filename = f"{uuid.uuid4()}{ext}"
    
    # Ensure upload directory exists
    entity_dir = os.path.join(UPLOAD_DIR, entity_type)
    if entity_id:
        entity_dir = os.path.join(entity_dir, str(entity_id))
    os.makedirs(entity_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(entity_dir, unique_filename)
    with open(file_path, "wb") as f:
        f.write(content)
    
    return {
        "filename": unique_filename,
        "original_filename": upload_file.filename,
        "file_path": file_path,
        "file_type": ext,
        "file_size": file_size,
        "mime_type": mime_type,
        "entity_type": entity_type,
        "entity_id": entity_id
    }

async def delete_file(file_path: str):
    """Delete a file from the upload directory"""
    try:
        os.remove(file_path)
    except OSError:
        # Log error but don't raise exception
        pass