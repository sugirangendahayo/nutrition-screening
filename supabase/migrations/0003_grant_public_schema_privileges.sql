-- ============================================================================
-- Grant base table privileges to the Data API roles.
-- ============================================================================
-- 0001_init.sql defines Row Level Security *policies*, but RLS policies only
-- ever narrow access that a role already has at the table-privilege level -
-- they never grant it. On older Supabase projects, newly created public
-- schema tables were automatically granted to `anon`/`authenticated`/
-- `service_role` (the "Data API" roles). Newer projects default the
-- "Automatically expose new tables" project setting to OFF (the now
-- Supabase-recommended, more secure default), so that automatic grant no
-- longer happens and every table starts with NO privileges for those roles -
-- producing `permission denied for table ...` even though the RLS policies
-- and the query itself are otherwise correct.
--
-- This backend's Flask API is the only component that talks to Postgres
-- (via the service_role key, which bypasses RLS but still requires the base
-- grant below). `authenticated` is granted the same baseline privileges the
-- 0001 RLS policies were written to filter, purely as defense-in-depth in
-- case anything ever queries Supabase directly with a user's own session
-- (see 0001's comment on this). `anon` intentionally gets nothing: no RLS
-- policy in 0001 grants it any access anyway.
-- ============================================================================

grant usage on schema public to service_role, authenticated;

grant all privileges on all tables in schema public to service_role;
grant select, insert, update, delete on all tables in schema public to authenticated;

grant usage, select on all sequences in schema public to service_role, authenticated;

-- Also cover any tables/sequences added by future migrations automatically.
alter default privileges in schema public
  grant all privileges on tables to service_role;
alter default privileges in schema public
  grant select, insert, update, delete on tables to authenticated;
alter default privileges in schema public
  grant usage, select on sequences to service_role, authenticated;
