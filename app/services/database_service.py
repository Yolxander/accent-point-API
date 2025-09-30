"""
Database service for Supabase operations
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from app.core.supabase import get_supabase_client, get_supabase_admin_client
from app.core.logging import get_logger

logger = get_logger(__name__)


class DatabaseService:
    """Service for database operations with Supabase"""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.admin_client = get_supabase_admin_client()
    
    async def create_voice_conversion(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        transformation_type: str = "voice_conversion",
        source_audio_filename: Optional[str] = None,
        source_audio_size: Optional[int] = None,
        source_audio_duration: Optional[float] = None,
        reference_audio_filename: Optional[str] = None,
        reference_audio_size: Optional[int] = None,
        reference_audio_duration: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new voice conversion record"""
        try:
            conversion_data = {
                "user_id": user_id,
                "session_id": session_id or str(uuid.uuid4()),
                "transformation_type": transformation_type,
                "source_audio_filename": source_audio_filename,
                "source_audio_size": source_audio_size,
                "source_audio_duration": source_audio_duration,
                "reference_audio_filename": reference_audio_filename,
                "reference_audio_size": reference_audio_size,
                "reference_audio_duration": reference_audio_duration,
                "status": "pending",
                **kwargs
            }
            
            result = self.client.table("voice_conversions").insert(conversion_data).execute()
            
            if result.data:
                logger.info(f"Created voice conversion record: {result.data[0]['id']}")
                return result.data[0]
            else:
                raise Exception("Failed to create voice conversion record")
                
        except Exception as e:
            logger.error(f"Error creating voice conversion: {e}")
            raise
    
    async def update_voice_conversion(
        self,
        conversion_id: str,
        **updates
    ) -> Dict[str, Any]:
        """Update a voice conversion record"""
        try:
            result = self.client.table("voice_conversions").update(updates).eq("id", conversion_id).execute()
            
            if result.data:
                logger.info(f"Updated voice conversion record: {conversion_id}")
                return result.data[0]
            else:
                raise Exception("Voice conversion record not found")
                
        except Exception as e:
            logger.error(f"Error updating voice conversion {conversion_id}: {e}")
            raise
    
    async def get_voice_conversion(self, conversion_id: str) -> Optional[Dict[str, Any]]:
        """Get a voice conversion record by ID"""
        try:
            result = self.client.table("voice_conversions").select("*").eq("id", conversion_id).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting voice conversion {conversion_id}: {e}")
            return None
    
    async def get_user_conversions(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get voice conversions for a user"""
        try:
            result = self.client.table("voice_conversions").select("*").eq("user_id", user_id).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting user conversions for {user_id}: {e}")
            return []
    
    async def create_text_to_speech_conversion(
        self,
        text_content: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        text_length: Optional[int] = None,
        language: str = "en",
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new text-to-speech conversion record"""
        try:
            conversion_data = {
                "user_id": user_id,
                "session_id": session_id or str(uuid.uuid4()),
                "text_content": text_content,
                "text_length": text_length or len(text_content),
                "language": language,
                "status": "pending",
                **kwargs
            }
            
            result = self.client.table("text_to_speech_conversions").insert(conversion_data).execute()
            
            if result.data:
                logger.info(f"Created TTS conversion record: {result.data[0]['id']}")
                return result.data[0]
            else:
                raise Exception("Failed to create TTS conversion record")
                
        except Exception as e:
            logger.error(f"Error creating TTS conversion: {e}")
            raise
    
    async def update_text_to_speech_conversion(
        self,
        conversion_id: str,
        **updates
    ) -> Dict[str, Any]:
        """Update a text-to-speech conversion record"""
        try:
            result = self.client.table("text_to_speech_conversions").update(updates).eq("id", conversion_id).execute()
            
            if result.data:
                logger.info(f"Updated TTS conversion record: {conversion_id}")
                return result.data[0]
            else:
                raise Exception("TTS conversion record not found")
                
        except Exception as e:
            logger.error(f"Error updating TTS conversion {conversion_id}: {e}")
            raise
    
    async def create_batch_processing_job(
        self,
        total_files: int,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        transformation_type: str = "voice_conversion",
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new batch processing job"""
        try:
            job_data = {
                "user_id": user_id,
                "session_id": session_id or str(uuid.uuid4()),
                "total_files": total_files,
                "transformation_type": transformation_type,
                "status": "pending",
                **kwargs
            }
            
            result = self.client.table("batch_processing_jobs").insert(job_data).execute()
            
            if result.data:
                logger.info(f"Created batch job record: {result.data[0]['id']}")
                return result.data[0]
            else:
                raise Exception("Failed to create batch job record")
                
        except Exception as e:
            logger.error(f"Error creating batch job: {e}")
            raise
    
    async def update_batch_processing_job(
        self,
        job_id: str,
        **updates
    ) -> Dict[str, Any]:
        """Update a batch processing job"""
        try:
            result = self.client.table("batch_processing_jobs").update(updates).eq("id", job_id).execute()
            
            if result.data:
                logger.info(f"Updated batch job record: {job_id}")
                return result.data[0]
            else:
                raise Exception("Batch job record not found")
                
        except Exception as e:
            logger.error(f"Error updating batch job {job_id}: {e}")
            raise
    
    async def create_batch_processing_file(
        self,
        batch_job_id: str,
        file_index: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a batch processing file record"""
        try:
            file_data = {
                "batch_job_id": batch_job_id,
                "file_index": file_index,
                "status": "pending",
                **kwargs
            }
            
            result = self.client.table("batch_processing_files").insert(file_data).execute()
            
            if result.data:
                logger.info(f"Created batch file record: {result.data[0]['id']}")
                return result.data[0]
            else:
                raise Exception("Failed to create batch file record")
                
        except Exception as e:
            logger.error(f"Error creating batch file: {e}")
            raise
    
    async def update_batch_processing_file(
        self,
        file_id: str,
        **updates
    ) -> Dict[str, Any]:
        """Update a batch processing file record"""
        try:
            result = self.client.table("batch_processing_files").update(updates).eq("id", file_id).execute()
            
            if result.data:
                logger.info(f"Updated batch file record: {file_id}")
                return result.data[0]
            else:
                raise Exception("Batch file record not found")
                
        except Exception as e:
            logger.error(f"Error updating batch file {file_id}: {e}")
            raise
    
    async def get_batch_processing_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get a batch processing job by ID"""
        try:
            result = self.client.table("batch_processing_jobs").select("*").eq("id", job_id).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting batch job {job_id}: {e}")
            return None
    
    async def get_batch_processing_files(self, job_id: str) -> List[Dict[str, Any]]:
        """Get all files for a batch processing job"""
        try:
            result = self.client.table("batch_processing_files").select("*").eq("batch_job_id", job_id).order("file_index").execute()
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting batch files for job {job_id}: {e}")
            return []
    
    async def update_api_usage_stats(
        self,
        user_id: Optional[str] = None,
        endpoint: str = "unknown",
        processing_time: float = 0.0,
        file_size: int = 0
    ) -> None:
        """Update API usage statistics"""
        try:
            today = datetime.now().date()
            
            # Try to update existing record
            result = self.client.table("api_usage_stats").select("*").eq("user_id", user_id).eq("date", today.isoformat()).eq("endpoint", endpoint).execute()
            
            if result.data:
                # Update existing record
                existing = result.data[0]
                updates = {
                    "request_count": existing["request_count"] + 1,
                    "total_processing_time_seconds": existing["total_processing_time_seconds"] + processing_time,
                    "total_file_size_bytes": existing["total_file_size_bytes"] + file_size
                }
                self.client.table("api_usage_stats").update(updates).eq("id", existing["id"]).execute()
            else:
                # Create new record
                stats_data = {
                    "user_id": user_id,
                    "date": today.isoformat(),
                    "endpoint": endpoint,
                    "request_count": 1,
                    "total_processing_time_seconds": processing_time,
                    "total_file_size_bytes": file_size
                }
                self.client.table("api_usage_stats").insert(stats_data).execute()
                
        except Exception as e:
            logger.error(f"Error updating API usage stats: {e}")
    
    async def test_connection(self) -> bool:
        """Test database connection"""
        try:
            result = self.client.table("voice_conversions").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


# Global database service instance
db_service = DatabaseService()
