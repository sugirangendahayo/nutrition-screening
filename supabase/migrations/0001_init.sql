-- ============================================================================
-- Nutrition Screening Decision Support System - Initial Schema
-- ============================================================================
-- Run this in the Supabase SQL editor (or via the Supabase CLI) on a fresh
-- project. See README.md "Database Setup" for the full walkthrough.
-- ============================================================================

create extension if not exists "pgcrypto";

-- ----------------------------------------------------------------------------
-- Roles
-- ----------------------------------------------------------------------------
create type user_role as enum (
  'administrator',
  'healthcare_worker',
  'nutrition_officer',
  'researcher'
);

create type prediction_target as enum ('stunting', 'underweight');
create type prediction_label as enum ('at_risk', 'not_at_risk');
create type child_sex as enum ('male', 'female');

-- ----------------------------------------------------------------------------
-- profiles: one row per Supabase Auth user, carrying role & basic metadata.
-- ----------------------------------------------------------------------------
create table if not exists profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  full_name text not null,
  role user_role not null default 'healthcare_worker',
  facility text,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

-- Auto-provision a default profile row whenever a new auth user is created,
-- so the app never encounters a signed-in user with no profile. An
-- administrator can adjust the role afterwards. The application backend
-- overwrites these defaults (full name / role / facility) via upsert when it
-- provisions a user through the admin API.
create or replace function handle_new_auth_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into profiles (id, full_name, role)
  values (new.id, coalesce(new.raw_user_meta_data ->> 'full_name', new.email), 'healthcare_worker')
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure handle_new_auth_user();

-- ----------------------------------------------------------------------------
-- children: de-identified child records (no name is stored).
-- ----------------------------------------------------------------------------
create sequence if not exists child_code_seq start 1;

create table if not exists children (
  id uuid primary key default gen_random_uuid(),
  child_code text unique not null default (
    'CH-' || to_char(now(), 'YYYY') || '-' || lpad(nextval('child_code_seq')::text, 5, '0')
  ),
  sex child_sex not null,
  created_by uuid references profiles (id),
  created_at timestamptz not null default now()
);

-- ----------------------------------------------------------------------------
-- model_versions: metadata about each distinct model deployed/used.
-- ----------------------------------------------------------------------------
create table if not exists model_versions (
  id uuid primary key default gen_random_uuid(),
  version text not null,
  mode text not null, -- 'mock' | 'real'
  algorithm text,
  targets text[] not null default array['stunting', 'underweight'],
  metrics jsonb, -- accuracy/precision/recall/f1/roc_auc/confusion_matrix once evaluated
  trained_at timestamptz,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  unique (version, mode)
);

-- ----------------------------------------------------------------------------
-- assessments: one nutrition screening event for one child.
-- ----------------------------------------------------------------------------
create table if not exists assessments (
  id uuid primary key default gen_random_uuid(),
  child_id uuid not null references children (id) on delete cascade,
  performed_by uuid not null references profiles (id),
  model_version_id uuid references model_versions (id),
  input_data jsonb not null,
  notes text,
  assessed_at timestamptz not null default now()
);

create index if not exists idx_assessments_child_id on assessments (child_id);
create index if not exists idx_assessments_performed_by on assessments (performed_by);
create index if not exists idx_assessments_assessed_at on assessments (assessed_at desc);

-- ----------------------------------------------------------------------------
-- assessment_predictions: one row per (assessment, target).
-- ----------------------------------------------------------------------------
create table if not exists assessment_predictions (
  id uuid primary key default gen_random_uuid(),
  assessment_id uuid not null references assessments (id) on delete cascade,
  target prediction_target not null,
  predicted_label prediction_label not null,
  probability numeric check (probability is null or (probability >= 0 and probability <= 1)),
  created_at timestamptz not null default now(),
  unique (assessment_id, target)
);

-- ----------------------------------------------------------------------------
-- prediction_explanations: one row per (assessment, target, feature).
-- ----------------------------------------------------------------------------
create table if not exists prediction_explanations (
  id uuid primary key default gen_random_uuid(),
  assessment_id uuid not null references assessments (id) on delete cascade,
  target prediction_target not null,
  method text not null, -- 'shap_local' | 'global_importance' | 'development_mock' | 'unavailable'
  feature_key text not null,
  feature_label text not null,
  contribution numeric not null,
  direction text not null,
  rank int not null
);

create index if not exists idx_explanations_assessment_id on prediction_explanations (assessment_id);

-- ----------------------------------------------------------------------------
-- reports: log of generated reports.
-- ----------------------------------------------------------------------------
create table if not exists reports (
  id uuid primary key default gen_random_uuid(),
  assessment_id uuid references assessments (id) on delete set null,
  child_id uuid references children (id) on delete set null,
  generated_by uuid references profiles (id),
  report_type text not null default 'assessment_summary',
  created_at timestamptz not null default now()
);

-- ============================================================================
-- Row Level Security
-- ============================================================================
-- The Flask backend uses the service-role key, which bypasses RLS entirely,
-- and performs its own authorization in app.utils.auth. These policies are a
-- defense-in-depth layer in case any client ever queries Supabase directly
-- (e.g. future direct-to-Postgres tooling) and MUST NOT be relied upon as the
-- only authorization mechanism.

alter table profiles enable row level security;
alter table children enable row level security;
alter table model_versions enable row level security;
alter table assessments enable row level security;
alter table assessment_predictions enable row level security;
alter table prediction_explanations enable row level security;
alter table reports enable row level security;

create or replace function current_user_role()
returns user_role
language sql
security definer
stable
set search_path = public
as $$
  select role from profiles where id = auth.uid();
$$;

-- profiles
create policy "profiles_select_self_or_admin" on profiles
  for select using (id = auth.uid() or current_user_role() = 'administrator');

create policy "profiles_update_admin_only" on profiles
  for update using (current_user_role() = 'administrator');

-- children: any authenticated clinical/research role may read; write limited
-- to roles that actually perform screenings.
create policy "children_select_authenticated" on children
  for select using (auth.role() = 'authenticated');

create policy "children_insert_clinical_roles" on children
  for insert with check (
    current_user_role() in ('administrator', 'healthcare_worker', 'nutrition_officer')
  );

-- model_versions: readable by everyone authenticated, writable by admin only.
create policy "model_versions_select_authenticated" on model_versions
  for select using (auth.role() = 'authenticated');

create policy "model_versions_write_admin" on model_versions
  for insert with check (current_user_role() = 'administrator');

create policy "model_versions_update_admin" on model_versions
  for update using (current_user_role() = 'administrator');

-- assessments
create policy "assessments_select_authenticated" on assessments
  for select using (auth.role() = 'authenticated');

create policy "assessments_insert_clinical_roles" on assessments
  for insert with check (
    current_user_role() in ('administrator', 'healthcare_worker', 'nutrition_officer')
  );

-- assessment_predictions / prediction_explanations follow the parent assessment
create policy "predictions_select_authenticated" on assessment_predictions
  for select using (auth.role() = 'authenticated');

create policy "predictions_insert_clinical_roles" on assessment_predictions
  for insert with check (
    current_user_role() in ('administrator', 'healthcare_worker', 'nutrition_officer')
  );

create policy "explanations_select_authenticated" on prediction_explanations
  for select using (auth.role() = 'authenticated');

create policy "explanations_insert_clinical_roles" on prediction_explanations
  for insert with check (
    current_user_role() in ('administrator', 'healthcare_worker', 'nutrition_officer')
  );

-- reports
create policy "reports_select_authenticated" on reports
  for select using (auth.role() = 'authenticated');

create policy "reports_insert_clinical_roles" on reports
  for insert with check (
    current_user_role() in ('administrator', 'healthcare_worker', 'nutrition_officer')
  );
