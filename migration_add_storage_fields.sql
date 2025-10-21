-- Migration script to add Supabase Storage fields to existing tables
-- Run this in your Supabase SQL editor to add the new storage fields

-- Add storage fields to voice_conversions table
ALTER TABLE voice_conversions 
ADD COLUMN IF NOT EXISTS output_file_path TEXT,
ADD COLUMN IF NOT EXISTS output_public_url TEXT;

-- Add storage fields to text_to_speech_conversions table
ALTER TABLE text_to_speech_conversions 
ADD COLUMN IF NOT EXISTS output_file_path TEXT,
ADD COLUMN IF NOT EXISTS output_public_url TEXT;

-- Add storage fields to batch_processing_files table
ALTER TABLE batch_processing_files 
ADD COLUMN IF NOT EXISTS output_file_path TEXT,
ADD COLUMN IF NOT EXISTS output_public_url TEXT;

-- Create indexes for the new fields for better performance
CREATE INDEX IF NOT EXISTS idx_voice_conversions_output_file_path ON voice_conversions(output_file_path);
CREATE INDEX IF NOT EXISTS idx_tts_conversions_output_file_path ON text_to_speech_conversions(output_file_path);
CREATE INDEX IF NOT EXISTS idx_batch_files_output_file_path ON batch_processing_files(output_file_path);

-- Add comments to document the new fields
COMMENT ON COLUMN voice_conversions.output_file_path IS 'Path to file in Supabase Storage';
COMMENT ON COLUMN voice_conversions.output_public_url IS 'Public URL for direct access to the file';
COMMENT ON COLUMN text_to_speech_conversions.output_file_path IS 'Path to file in Supabase Storage';
COMMENT ON COLUMN text_to_speech_conversions.output_public_url IS 'Public URL for direct access to the file';
COMMENT ON COLUMN batch_processing_files.output_file_path IS 'Path to file in Supabase Storage';
COMMENT ON COLUMN batch_processing_files.output_public_url IS 'Public URL for direct access to the file';
