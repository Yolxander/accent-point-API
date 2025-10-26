"""
Storage service for Supabase Storage operations
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.core.supabase import get_supabase_admin_client
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class StorageService:
    """Service for file storage operations with Supabase Storage"""
    
    def __init__(self):
        self.client = get_supabase_admin_client()
        self.bucket_name = settings.S3_BUCKET_NAME
    
    async def ensure_bucket_exists(self) -> bool:
        """Ensure the audio files bucket exists in Supabase Storage"""
        try:
            # Try to get bucket info
            result = self.client.storage.get_bucket(self.bucket_name)
            if result:
                logger.info(f"Bucket '{self.bucket_name}' already exists")
                return True
        except Exception:
            # Bucket doesn't exist, create it
            try:
                result = self.client.storage.create_bucket(
                    self.bucket_name,
                    options={
                        "public": True,  # Make files publicly accessible
                        "file_size_limit": 50 * 1024 * 1024,  # 50MB limit
                        "allowed_mime_types": [
                            "audio/wav",
                            "audio/mp3",
                            "audio/flac",
                            "audio/m4a",
                            "audio/ogg"
                        ]
                    }
                )
                logger.info(f"Created bucket '{self.bucket_name}'")
                return True
            except Exception as e:
                logger.error(f"Failed to create bucket '{self.bucket_name}': {e}")
                return False
    
    async def upload_audio_file(
        self,
        audio_data: bytes,
        filename: str,
        folder: str = "conversions"
    ) -> Dict[str, Any]:
        """Upload audio file to Supabase Storage"""
        try:
            # Ensure bucket exists
            await self.ensure_bucket_exists()
            
            # Generate unique filename to avoid conflicts
            file_extension = os.path.splitext(filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = f"{folder}/{unique_filename}"
            
            # Upload file to Supabase Storage
            result = self.client.storage.from_(self.bucket_name).upload(
                file_path,
                audio_data,
                file_options={
                    "content-type": "audio/wav",
                    "cache-control": "3600"
                }
            )
            
            # Check for upload errors - result is a Response object, not a dict
            if hasattr(result, 'status_code') and result.status_code != 200:
                error_text = result.text if hasattr(result, 'text') else str(result)
                raise Exception(f"Upload failed with status {result.status_code}: {error_text}")
            
            # Get public URL
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(file_path)
            
            logger.info(f"Uploaded audio file: {file_path}")
            
            return {
                "file_path": file_path,
                "filename": unique_filename,
                "original_filename": filename,
                "public_url": public_url,
                "file_size": len(audio_data),
                "uploaded_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error uploading audio file: {e}")
            raise
    
    async def get_audio_file(self, file_path: str) -> Optional[bytes]:
        """Download audio file from Supabase Storage"""
        try:
            result = self.client.storage.from_(self.bucket_name).download(file_path)
            
            if result:
                return result
            return None
            
        except Exception as e:
            logger.error(f"Error downloading audio file {file_path}: {e}")
            return None
    
    async def get_public_url(self, file_path: str) -> Optional[str]:
        """Get public URL for an audio file"""
        try:
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(file_path)
            return public_url
        except Exception as e:
            logger.error(f"Error getting public URL for {file_path}: {e}")
            return None
    
    async def delete_audio_file(self, file_path: str) -> bool:
        """Delete audio file from Supabase Storage"""
        try:
            result = self.client.storage.from_(self.bucket_name).remove([file_path])
            
            if result.get("error"):
                logger.error(f"Failed to delete file {file_path}: {result['error']}")
                return False
            
            logger.info(f"Deleted audio file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting audio file {file_path}: {e}")
            return False
    
    async def list_audio_files(self, folder: str = "conversions", limit: int = 100) -> list:
        """List audio files in a folder"""
        try:
            result = self.client.storage.from_(self.bucket_name).list(
                folder,
                options={"limit": limit}
            )
            
            return result or []
            
        except Exception as e:
            logger.error(f"Error listing audio files in {folder}: {e}")
            return []
    
    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file information from Supabase Storage"""
        try:
            # List files to get metadata
            folder = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            
            files = await self.list_audio_files(folder)
            
            for file_info in files:
                if file_info.get("name") == filename:
                    return file_info
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return None


# Global storage service instance
storage_service = StorageService()
