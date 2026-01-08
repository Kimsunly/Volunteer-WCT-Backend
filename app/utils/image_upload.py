"""
Image upload utilities for Supabase Storage
Handles uploading images to the opportunity-images bucket
"""
import os
import uuid
from typing import Optional, List
from datetime import datetime
from fastapi import UploadFile, HTTPException, status

from app.database import get_supabase
from app.config import settings


# Allowed image file extensions
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Get bucket name from config
BUCKET_NAME = settings.STORAGE_OPPORTUNITY_BUCKET


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename"""
    return os.path.splitext(filename)[1].lower()


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename to prevent collisions.
    Format: timestamp_uuid_originalname.ext
    """
    ext = get_file_extension(original_filename)
    name_without_ext = os.path.splitext(original_filename)[0]
    # Clean the original filename
    clean_name = "".join(c for c in name_without_ext if c.isalnum() or c in ('-', '_'))[:50]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}_{clean_name}{ext}"


async def upload_opportunity_image(
    file: UploadFile,
    organizer_id: int
) -> str:
    """
    Upload a single image to Supabase Storage.
    
    Args:
        file: The uploaded file
        organizer_id: ID of the organizer (for organizing files)
        
    Returns:
        Public URL of the uploaded image
        
    Raises:
        HTTPException: If upload fails
    """
    supabase = get_supabase()
    
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    try:
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading file: {str(e)}"
        )
    
    # Generate unique filename
    unique_filename = generate_unique_filename(file.filename)
    
    # Create path: organizer_id/filename
    file_path = f"organizer_{organizer_id}/{unique_filename}"
    
    try:
        # Upload to Supabase Storage
        result = supabase.storage.from_(BUCKET_NAME).upload(
            path=file_path,
            file=file_content,
            file_options={
                "content-type": file.content_type or "image/jpeg",
                "cache-control": "3600",
                "upsert": "false"  # Don't overwrite existing files
            }
        )
        
        # Get public URL
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_path)
        
        return public_url
        
    except Exception as e:
        error_message = str(e)
        print(f"Upload error: {error_message}")
        
        # Handle specific errors
        if "already exists" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="File already exists. Please try again."
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {error_message}"
        )


async def upload_multiple_opportunity_images(
    files: List[UploadFile],
    organizer_id: int,
    max_files: int = 5
) -> List[str]:
    """
    Upload multiple images to Supabase Storage.
    
    Args:
        files: List of uploaded files
        organizer_id: ID of the organizer
        max_files: Maximum number of files allowed (default 5)
        
    Returns:
        List of public URLs
        
    Raises:
        HTTPException: If upload fails
    """
    if len(files) > max_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Too many files. Maximum: {max_files}"
        )
    
    urls = []
    for file in files:
        try:
            url = await upload_opportunity_image(file, organizer_id)
            urls.append(url)
        except HTTPException as e:
            # If one file fails, continue with others but track the error
            print(f"Failed to upload {file.filename}: {e.detail}")
            continue
    
    if not urls:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload any images"
        )
    
    return urls


async def delete_opportunity_image(image_url: str) -> bool:
    """
    Delete an image from Supabase Storage.
    
    Args:
        image_url: Full public URL of the image
        
    Returns:
        True if deleted successfully
    """
    supabase = get_supabase()
    
    try:
        # Extract file path from URL
        # URL format: https://xxx.supabase.co/storage/v1/object/public/opportunity-images/organizer_X/filename.jpg
        if f"/{BUCKET_NAME}/" in image_url:
            file_path = image_url.split(f"/{BUCKET_NAME}/")[1]
        else:
            raise ValueError("Invalid image URL")
        
        # Delete from storage
        supabase.storage.from_(BUCKET_NAME).remove([file_path])
        
        return True
        
    except Exception as e:
        print(f"Error deleting image: {e}")
        # Don't raise exception - image deletion is not critical
        return False


async def delete_multiple_images(image_urls: List[str]) -> int:
    """
    Delete multiple images.
    
    Args:
        image_urls: List of image URLs
        
    Returns:
        Number of successfully deleted images
    """
    deleted_count = 0
    for url in image_urls:
        if await delete_opportunity_image(url):
            deleted_count += 1
    
    return deleted_count


def get_image_urls_from_string(images_string: Optional[str]) -> List[str]:
    """
    Parse image URLs from the images field.
    Supports both comma-separated URLs and single URL.
    
    Args:
        images_string: The images field value
        
    Returns:
        List of image URLs
    """
    if not images_string:
        return []
    
    # If it's a comma-separated string
    if ',' in images_string:
        return [url.strip() for url in images_string.split(',') if url.strip()]
    
    # Single URL
    return [images_string.strip()]


def image_urls_to_string(urls: List[str]) -> str:
    """
    Convert list of URLs to comma-separated string for storage.
    
    Args:
        urls: List of image URLs
        
    Returns:
        Comma-separated string
    """
    return ','.join(urls)