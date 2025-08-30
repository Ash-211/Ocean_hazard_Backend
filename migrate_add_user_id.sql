-- Migration script to add user_id column to hazard_reports table
-- and create media table

-- Add user_id column to hazard_reports table
ALTER TABLE hazard_reports 
ADD COLUMN user_id UUID REFERENCES users(id);

-- Create media table
CREATE TABLE media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    hazard_report_id UUID REFERENCES hazard_reports(id),
    filename VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    file_type VARCHAR NOT NULL,
    file_size INTEGER NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_media_user_id ON media(user_id);
CREATE INDEX idx_media_hazard_report_id ON media(hazard_report_id);
CREATE INDEX idx_hazard_reports_user_id ON hazard_reports(user_id);
