"""
Lab Practices API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.services.database_service import DatabaseService

router = APIRouter(prefix="/api/v1/lab-practices", tags=["Lab Practices"])

# Initialize database service
db_service = DatabaseService()


class LabPracticeCreate(BaseModel):
    target_accent: str
    practice_date: Optional[str] = None
    duration_seconds: int = 0
    status: str = "completed"


class ComparisonCreate(BaseModel):
    lab_practice_id: str
    sentence: str
    before_audio_url: Optional[str] = None
    after_audio_url: Optional[str] = None
    ideal_audio_url: Optional[str] = None
    before_audio_duration: Optional[float] = None
    after_audio_duration: Optional[float] = None
    ideal_audio_duration: Optional[float] = None
    similarity_score: Optional[float] = None
    word_pack_item_id: Optional[str] = None


@router.post("/", summary="Create Lab Practice", description="Create a new lab practice record")
async def create_lab_practice(practice_data: LabPracticeCreate):
    """Create a new lab practice record"""
    try:
        # Use admin client to bypass RLS for unauthenticated users
        practice_record = {
            "user_id": None,  # No authenticated user
            "target_accent": practice_data.target_accent,
            "practice_date": practice_data.practice_date or datetime.now().isoformat(),
            "duration_seconds": practice_data.duration_seconds,
            "status": practice_data.status
        }
        
        result = db_service.admin_client.table("lab_practices").insert(practice_record).execute()
        
        if result.data:
            return {
                "success": True,
                "data": result.data[0],
                "error": None
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create lab practice record")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating lab practice: {str(e)}")


@router.post("/comparisons", summary="Create Comparison", description="Create a new comparison record")
async def create_comparison(comparison_data: ComparisonCreate):
    """Create a new comparison record"""
    try:
        comparison_record = {
            "lab_practice_id": comparison_data.lab_practice_id,
            "sentence": comparison_data.sentence,
            "before_audio_url": comparison_data.before_audio_url,
            "after_audio_url": comparison_data.after_audio_url,
            "ideal_audio_url": comparison_data.ideal_audio_url,
            "before_audio_duration": comparison_data.before_audio_duration,
            "after_audio_duration": comparison_data.after_audio_duration,
            "ideal_audio_duration": comparison_data.ideal_audio_duration,
            "similarity_score": comparison_data.similarity_score,
            "word_pack_item_id": comparison_data.word_pack_item_id
        }
        
        result = db_service.admin_client.table("comparisons").insert(comparison_record).execute()
        
        if result.data:
            return {
                "success": True,
                "data": result.data[0],
                "error": None
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create comparison record")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating comparison: {str(e)}")


class ComparisonUpdate(BaseModel):
    before_audio_url: Optional[str] = None
    after_audio_url: Optional[str] = None
    ideal_audio_url: Optional[str] = None
    before_audio_duration: Optional[float] = None
    after_audio_duration: Optional[float] = None
    ideal_audio_duration: Optional[float] = None
    similarity_score: Optional[float] = None
    word_pack_item_id: Optional[str] = None


@router.patch("/comparisons/{comparison_id}", summary="Update Comparison", description="Update an existing comparison record")
async def update_comparison(comparison_id: str, comparison_data: ComparisonUpdate):
    """Update an existing comparison record"""
    try:
        # Build update record with only provided fields
        update_record = {}
        if comparison_data.before_audio_url is not None:
            update_record["before_audio_url"] = comparison_data.before_audio_url
        if comparison_data.after_audio_url is not None:
            update_record["after_audio_url"] = comparison_data.after_audio_url
        if comparison_data.ideal_audio_url is not None:
            update_record["ideal_audio_url"] = comparison_data.ideal_audio_url
        if comparison_data.before_audio_duration is not None:
            update_record["before_audio_duration"] = comparison_data.before_audio_duration
        if comparison_data.after_audio_duration is not None:
            update_record["after_audio_duration"] = comparison_data.after_audio_duration
        if comparison_data.ideal_audio_duration is not None:
            update_record["ideal_audio_duration"] = comparison_data.ideal_audio_duration
        if comparison_data.similarity_score is not None:
            update_record["similarity_score"] = comparison_data.similarity_score
        if comparison_data.word_pack_item_id is not None:
            update_record["word_pack_item_id"] = comparison_data.word_pack_item_id
        
        if not update_record:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        result = db_service.admin_client.table("comparisons").update(update_record).eq("id", comparison_id).execute()
        
        if result.data:
            return {
                "success": True,
                "data": result.data[0],
                "error": None
            }
        else:
            raise HTTPException(status_code=404, detail="Comparison not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating comparison: {str(e)}")


@router.get("/", summary="Get Lab Practices", description="Get all lab practice records")
async def get_lab_practices():
    """Get all lab practice records with their comparisons"""
    try:
        # Get lab practices
        practices_result = db_service.admin_client.table("lab_practices").select("*").order("practice_date", desc=True).execute()
        
        if not practices_result.data:
            return {
                "success": True,
                "data": [],
                "error": None
            }
        
        # Get comparisons for each practice
        practices_with_comparisons = []
        for practice in practices_result.data:
            practice_id = practice["id"]
            
            # Get comparisons for this practice
            comparisons_result = db_service.admin_client.table("comparisons").select("*").eq("lab_practice_id", practice_id).execute()
            
            # Add comparisons to practice data
            practice["comparisons"] = comparisons_result.data or []
            practices_with_comparisons.append(practice)
        
        return {
            "success": True,
            "data": practices_with_comparisons,
            "error": None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching lab practices: {str(e)}")


@router.get("/{practice_id}", summary="Get Lab Practice", description="Get a specific lab practice record")
async def get_lab_practice(practice_id: str):
    """Get a specific lab practice record with its comparisons"""
    try:
        result = db_service.admin_client.table("lab_practices").select("""
            *,
            comparisons (*)
        """).eq("id", practice_id).execute()
        
        if result.data:
            return {
                "success": True,
                "data": result.data[0],
                "error": None
            }
        else:
            raise HTTPException(status_code=404, detail="Lab practice not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching lab practice: {str(e)}")


@router.delete("/{practice_id}", summary="Delete Lab Practice", description="Delete a lab practice record and its comparisons")
async def delete_lab_practice(practice_id: str):
    """Delete a lab practice record and its associated comparisons"""
    try:
        # Delete comparisons first (due to foreign key constraint)
        db_service.admin_client.table("comparisons").delete().eq("lab_practice_id", practice_id).execute()
        
        # Delete the practice record
        result = db_service.admin_client.table("lab_practices").delete().eq("id", practice_id).execute()
        
        # Supabase delete returns empty array on success
        return {
            "success": True,
            "data": None,
            "error": None
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting lab practice: {str(e)}")
