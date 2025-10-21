"""
Supabase configuration and client setup
"""

import os
from typing import Optional
from supabase import create_client, Client
from app.core.config import settings


class SupabaseConfig:
    """Supabase configuration and client management"""
    
    def __init__(self):
        self.url: str = os.getenv("SUPABASE_URL", "http://127.0.0.1:54321")
        self.anon_key: str = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0")
        self.service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU")
        self.s3_access_key: str = os.getenv("S3_ACCESS_KEY", "625729a08b95bf1b7ff351a663f3a23c")
        self.s3_secret_key: str = os.getenv("S3_SECRET_KEY", "850181e4652dd023b7a98c58ae0d2d34bd487ee0cc3254aed6eda37307425907")
        self._client: Optional[Client] = None
        self._admin_client: Optional[Client] = None
    
    @property
    def client(self) -> Client:
        """Get Supabase client with anon key"""
        if self._client is None:
            self._client = create_client(self.url, self.anon_key)
        return self._client
    
    @property
    def admin_client(self) -> Client:
        """Get Supabase admin client with service role key"""
        if self._admin_client is None:
            self._admin_client = create_client(self.url, self.service_role_key)
        return self._admin_client
    
    async def test_connection(self) -> bool:
        """Test Supabase connection"""
        try:
            # Test with a simple query
            result = self.client.table("voice_conversions").select("id").limit(1).execute()
            return True
        except Exception as e:
            print(f"Supabase connection test failed: {e}")
            return False


# Global Supabase configuration instance
supabase_config = SupabaseConfig()


def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    return supabase_config.client


def get_supabase_admin_client() -> Client:
    """Get Supabase admin client instance"""
    return supabase_config.admin_client
