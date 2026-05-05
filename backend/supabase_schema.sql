-- Run this in your Supabase SQL editor to set up the database
-- Go to: Project → SQL Editor → New query → Paste and Run

create table if not exists scans (
  id uuid default gen_random_uuid() primary key,
  repo_id text not null,
  repo_full_name text,
  pr_number integer not null,
  score integer,
  severity_counts jsonb default '{}',
  findings_count integer default 0,
  auto_fix_pr_url text,
  report_url text,
  created_at timestamptz default now()
);

create index if not exists scans_repo_id_idx on scans(repo_id);
create index if not exists scans_created_at_idx on scans(created_at desc);
create index if not exists scans_repo_pr_idx on scans(repo_id, pr_number);

-- ─── Storage Bucket ────────────────────────────────────
-- Run in Supabase dashboard: Storage → New bucket
-- Name: scan-reports
-- Set to: Public
--
-- Or run via API / psql if you have admin access:
-- insert into storage.buckets (id, name, public) values ('scan-reports', 'scan-reports', true);
