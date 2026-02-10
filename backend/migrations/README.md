# Database Migrations

This directory contains SQL migration files for the VidyaMitra backend database.

## Migrations

### 001_internship_discovery_schema.sql

Creates the complete database schema for the Internship Discovery & Verification Module, including:

- **7 Tables:**
  1. `student_profiles` - Student profile information
  2. `internship_listings` - Internship opportunities
  3. `verification_results` - Verification analysis
  4. `skill_matches` - Skill matching cache
  5. `readiness_scores` - Readiness assessments
  6. `user_alerts` - User notifications
  7. `scam_reports` - Reported suspicious listings

- **Indexes:** Optimized indexes for common queries
- **Triggers:** Automatic `updated_at` timestamp updates
- **Constraints:** Data validation and referential integrity

## How to Apply Migrations

### Using Supabase Dashboard

1. Log in to your Supabase project dashboard
2. Navigate to the SQL Editor
3. Copy the contents of the migration file
4. Paste into the SQL Editor
5. Click "Run" to execute the migration

### Using Supabase CLI

```bash
# Install Supabase CLI if not already installed
npm install -g supabase

# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref your-project-ref

# Apply the migration
supabase db push
```

### Using psql (Direct PostgreSQL Connection)

```bash
# Connect to your Supabase database
psql "postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT-REF].supabase.co:5432/postgres"

# Run the migration
\i backend/migrations/001_internship_discovery_schema.sql
```

## Verification

After applying the migration, verify the tables were created:

```sql
-- List all tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'student_profiles',
    'internship_listings',
    'verification_results',
    'skill_matches',
    'readiness_scores',
    'user_alerts',
    'scam_reports'
);

-- Check indexes
SELECT tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename LIKE '%internship%' OR tablename LIKE '%student%';

-- Check triggers
SELECT trigger_name, event_object_table 
FROM information_schema.triggers 
WHERE trigger_schema = 'public';
```

## Rollback

To rollback this migration, drop the tables in reverse order:

```sql
DROP TABLE IF EXISTS scam_reports CASCADE;
DROP TABLE IF EXISTS user_alerts CASCADE;
DROP TABLE IF EXISTS readiness_scores CASCADE;
DROP TABLE IF EXISTS skill_matches CASCADE;
DROP TABLE IF EXISTS verification_results CASCADE;
DROP TABLE IF EXISTS internship_listings CASCADE;
DROP TABLE IF EXISTS student_profiles CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
```

## Notes

- The migration assumes the `auth.users` table exists (provided by Supabase Auth)
- The `uuid-ossp` extension is required for UUID generation
- All tables use UUID primary keys for better scalability
- Foreign key constraints ensure referential integrity
- Indexes are optimized for common query patterns
- Triggers automatically update `updated_at` timestamps
