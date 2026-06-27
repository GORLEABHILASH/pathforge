-- PathForge Supabase Schema
-- Run this in the Supabase SQL Editor (supabase.com → your project → SQL Editor)

-- Users table
create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  email text unique not null,
  created_at timestamptz default now()
);

-- Profiles table — stores the assessed profile per user
create table if not exists profiles (
  id uuid primary key default gen_random_uuid(),
  user_email text not null references users(email) on delete cascade,
  profile_json jsonb not null,        -- full ExtractedProfile
  onboarding_json jsonb not null,     -- full OnboardingInput
  employability_score integer not null,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
create index if not exists profiles_email_idx on profiles(user_email);

-- Skill progress table — tracks what the user has learned
create table if not exists skill_progress (
  id uuid primary key default gen_random_uuid(),
  user_email text not null,
  skill text not null,
  completed_steps integer[] default '{}',   -- array of step order numbers completed
  notes text default '',
  updated_at timestamptz default now(),
  unique(user_email, skill)
);
create index if not exists skill_progress_email_idx on skill_progress(user_email);

-- Job applications table — tracks what the user has applied to
create table if not exists job_applications (
  id uuid primary key default gen_random_uuid(),
  user_email text not null,
  job_id text not null,
  company text not null,
  title text not null,
  apply_link text,
  match_score integer,
  status text default 'applied',   -- applied | interviewing | offer | rejected | ghosted
  applied_at timestamptz default now(),
  updated_at timestamptz default now(),
  unique(user_email, job_id)
);
create index if not exists applications_email_idx on job_applications(user_email);

-- Auto-update updated_at on skill_progress
create or replace function update_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger skill_progress_updated_at
  before update on skill_progress
  for each row execute function update_updated_at();

create trigger profiles_updated_at
  before update on profiles
  for each row execute function update_updated_at();

-- Enable Row Level Security (good practice — lock down direct client access)
alter table users enable row level security;
alter table profiles enable row level security;
alter table skill_progress enable row level security;
alter table job_applications enable row level security;

-- For now: allow all operations via service role key (backend uses this)
-- When you add auth, replace these with user-specific policies
create policy "service_all" on users for all using (true);
create policy "service_all" on profiles for all using (true);
create policy "service_all" on skill_progress for all using (true);
create policy "service_all" on job_applications for all using (true);
