-- Supabase Database Schema for OpenVoice API with Storage Integration
-- Run this in your Supabase SQL editor to create the necessary tables

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Voice Conversions Table
CREATE TABLE IF NOT EXISTS voice_conversions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    session_id TEXT,
    transformation_type TEXT NOT NULL CHECK (transformation_type IN (
        'voice_conversion', 'accent_change', 'gender_swap', 'age_change', 'emotion_change'
    )),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
        'pending', 'processing', 'completed', 'failed', 'cancelled'
    )),
    
    -- Input files
    source_audio_filename TEXT,
    source_audio_size BIGINT,
    source_audio_duration FLOAT,
    reference_audio_filename TEXT,
    reference_audio_size BIGINT,
    reference_audio_duration FLOAT,
    
    -- Processing parameters
    pitch_shift INTEGER DEFAULT 0 CHECK (pitch_shift >= -12 AND pitch_shift <= 12),
    speed_multiplier FLOAT DEFAULT 1.0 CHECK (speed_multiplier >= 0.5 AND speed_multiplier <= 2.0),
    volume_multiplier FLOAT DEFAULT 1.0 CHECK (volume_multiplier >= 0.1 AND volume_multiplier <= 3.0),
    noise_reduction BOOLEAN DEFAULT false,
    echo_removal BOOLEAN DEFAULT false,
    voice_enhancement BOOLEAN DEFAULT false,
    
    -- Output files
    output_filename TEXT,
    output_file_size BIGINT,
    output_duration FLOAT,
    output_format TEXT DEFAULT 'wav' CHECK (output_format IN ('wav', 'mp3', 'flac')),
    quality TEXT DEFAULT 'medium' CHECK (quality IN ('low', 'medium', 'high')),
    
    -- Supabase Storage fields
    output_file_path TEXT,  -- Path to file in Supabase Storage
    output_public_url TEXT, -- Public URL for direct access
    output_audio_data BYTEA,  -- Keep for backward compatibility (will be deprecated)
    
    -- Processing metadata
    processing_time_seconds FLOAT,
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Text-to-Speech Conversions Table
CREATE TABLE IF NOT EXISTS text_to_speech_conversions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    session_id TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
        'pending', 'processing', 'completed', 'failed', 'cancelled'
    )),
    
    -- Input text
    text_content TEXT NOT NULL,
    text_length INTEGER,
    language TEXT DEFAULT 'en',
    
    -- Voice characteristics
    reference_audio_filename TEXT,
    reference_audio_size BIGINT,
    reference_audio_duration FLOAT,
    
    -- Processing parameters
    pitch_shift INTEGER DEFAULT 0 CHECK (pitch_shift >= -12 AND pitch_shift <= 12),
    speed_multiplier FLOAT DEFAULT 1.0 CHECK (speed_multiplier >= 0.5 AND speed_multiplier <= 2.0),
    volume_multiplier FLOAT DEFAULT 1.0 CHECK (volume_multiplier >= 0.1 AND volume_multiplier <= 3.0),
    
    -- Output files
    output_filename TEXT,
    output_file_size BIGINT,
    output_duration FLOAT,
    output_format TEXT DEFAULT 'wav' CHECK (output_format IN ('wav', 'mp3', 'flac')),
    quality TEXT DEFAULT 'medium' CHECK (quality IN ('low', 'medium', 'high')),
    
    -- Supabase Storage fields
    output_file_path TEXT,  -- Path to file in Supabase Storage
    output_public_url TEXT, -- Public URL for direct access
    output_audio_data BYTEA,  -- Keep for backward compatibility (will be deprecated)
    
    -- Processing metadata
    processing_time_seconds FLOAT,
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Batch Processing Jobs Table
CREATE TABLE IF NOT EXISTS batch_processing_jobs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    session_id TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
        'pending', 'processing', 'completed', 'failed', 'cancelled'
    )),
    
    -- Job metadata
    total_files INTEGER NOT NULL,
    processed_files INTEGER DEFAULT 0,
    successful_files INTEGER DEFAULT 0,
    failed_files INTEGER DEFAULT 0,
    
    -- Processing parameters (same as voice_conversions)
    transformation_type TEXT NOT NULL CHECK (transformation_type IN (
        'voice_conversion', 'accent_change', 'gender_swap', 'age_change', 'emotion_change'
    )),
    pitch_shift INTEGER DEFAULT 0 CHECK (pitch_shift >= -12 AND pitch_shift <= 12),
    speed_multiplier FLOAT DEFAULT 1.0 CHECK (speed_multiplier >= 0.5 AND speed_multiplier <= 2.0),
    volume_multiplier FLOAT DEFAULT 1.0 CHECK (volume_multiplier >= 0.1 AND volume_multiplier <= 3.0),
    noise_reduction BOOLEAN DEFAULT false,
    echo_removal BOOLEAN DEFAULT false,
    voice_enhancement BOOLEAN DEFAULT false,
    
    -- Output settings
    output_format TEXT DEFAULT 'wav' CHECK (output_format IN ('wav', 'mp3', 'flac')),
    quality TEXT DEFAULT 'medium' CHECK (quality IN ('low', 'medium', 'high')),
    
    -- Processing metadata
    processing_time_seconds FLOAT,
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Batch Processing Files Table (for individual files in a batch)
CREATE TABLE IF NOT EXISTS batch_processing_files (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    batch_job_id UUID REFERENCES batch_processing_jobs(id) ON DELETE CASCADE,
    file_index INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
        'pending', 'processing', 'completed', 'failed', 'cancelled'
    )),
    
    -- Input file
    source_audio_filename TEXT,
    source_audio_size BIGINT,
    source_audio_duration FLOAT,
    reference_audio_filename TEXT,
    reference_audio_size BIGINT,
    reference_audio_duration FLOAT,
    
    -- Output file
    output_filename TEXT,
    output_file_size BIGINT,
    output_duration FLOAT,
    
    -- Supabase Storage fields
    output_file_path TEXT,  -- Path to file in Supabase Storage
    output_public_url TEXT, -- Public URL for direct access
    output_audio_data BYTEA,  -- Keep for backward compatibility (will be deprecated)
    
    -- Processing metadata
    processing_time_seconds FLOAT,
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- API Usage Statistics Table
CREATE TABLE IF NOT EXISTS api_usage_stats (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    endpoint TEXT NOT NULL,
    request_count INTEGER DEFAULT 0,
    total_processing_time_seconds FLOAT DEFAULT 0,
    total_file_size_bytes BIGINT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, date, endpoint)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_voice_conversions_user_id ON voice_conversions(user_id);
CREATE INDEX IF NOT EXISTS idx_voice_conversions_status ON voice_conversions(status);
CREATE INDEX IF NOT EXISTS idx_voice_conversions_created_at ON voice_conversions(created_at);
CREATE INDEX IF NOT EXISTS idx_voice_conversions_session_id ON voice_conversions(session_id);

CREATE INDEX IF NOT EXISTS idx_tts_conversions_user_id ON text_to_speech_conversions(user_id);
CREATE INDEX IF NOT EXISTS idx_tts_conversions_status ON text_to_speech_conversions(status);
CREATE INDEX IF NOT EXISTS idx_tts_conversions_created_at ON text_to_speech_conversions(created_at);
CREATE INDEX IF NOT EXISTS idx_tts_conversions_session_id ON text_to_speech_conversions(session_id);

CREATE INDEX IF NOT EXISTS idx_batch_jobs_user_id ON batch_processing_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_status ON batch_processing_jobs(status);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_created_at ON batch_processing_jobs(created_at);

CREATE INDEX IF NOT EXISTS idx_batch_files_batch_job_id ON batch_processing_files(batch_job_id);
CREATE INDEX IF NOT EXISTS idx_batch_files_status ON batch_processing_files(status);

CREATE INDEX IF NOT EXISTS idx_usage_stats_user_id ON api_usage_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_stats_date ON api_usage_stats(date);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_voice_conversions_updated_at 
    BEFORE UPDATE ON voice_conversions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tts_conversions_updated_at 
    BEFORE UPDATE ON text_to_speech_conversions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_batch_jobs_updated_at 
    BEFORE UPDATE ON batch_processing_jobs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_batch_files_updated_at 
    BEFORE UPDATE ON batch_processing_files 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_usage_stats_updated_at 
    BEFORE UPDATE ON api_usage_stats 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) policies
ALTER TABLE voice_conversions ENABLE ROW LEVEL SECURITY;
ALTER TABLE text_to_speech_conversions ENABLE ROW LEVEL SECURITY;
ALTER TABLE batch_processing_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE batch_processing_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage_stats ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own conversions
CREATE POLICY "Users can view own voice conversions" ON voice_conversions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own voice conversions" ON voice_conversions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own voice conversions" ON voice_conversions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own TTS conversions" ON text_to_speech_conversions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own TTS conversions" ON text_to_speech_conversions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own TTS conversions" ON text_to_speech_conversions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own batch jobs" ON batch_processing_jobs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own batch jobs" ON batch_processing_jobs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own batch jobs" ON batch_processing_jobs
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own batch files" ON batch_processing_files
    FOR SELECT USING (auth.uid() = (SELECT user_id FROM batch_processing_jobs WHERE id = batch_job_id));

CREATE POLICY "Users can insert own batch files" ON batch_processing_files
    FOR INSERT WITH CHECK (auth.uid() = (SELECT user_id FROM batch_processing_jobs WHERE id = batch_job_id));

CREATE POLICY "Users can update own batch files" ON batch_processing_files
    FOR UPDATE USING (auth.uid() = (SELECT user_id FROM batch_processing_jobs WHERE id = batch_job_id));

CREATE POLICY "Users can view own usage stats" ON api_usage_stats
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own usage stats" ON api_usage_stats
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own usage stats" ON api_usage_stats
    FOR UPDATE USING (auth.uid() = user_id);

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
