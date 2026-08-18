-- ============================================================================
-- DEVELOPMENT SEED DATA
-- ============================================================================
-- Optional. Populates a few sample children/assessments so the dashboard and
-- history pages are not empty while developing the UI. This is clearly
-- DEVELOPMENT DATA - do not run this against a production database.
--
-- Input data uses the actual 20 raw MICS6 predictor codes expected by the
-- trained pipelines (see backend/app/ml/feature_schema.py RAW_FEATURE_ORDER),
-- NOT invented semantic field names.
--
-- Prerequisite: at least one profile must already exist (sign in once, or
-- create a user via the admin API, then run 0002_bootstrap_admin.sql). This
-- script attaches the sample records to the first administrator/healthcare
-- worker profile it finds.
-- ============================================================================

do $$
declare
  actor_id uuid;
  child_1 uuid;
  child_2 uuid;
  stunting_version_id uuid;
  underweight_version_id uuid;
  a1_id uuid;
  a2_id uuid;
  a3_id uuid;
begin
  select id into actor_id from profiles order by created_at asc limit 1;

  if actor_id is null then
    raise notice 'No profiles found - sign in at least once before seeding.';
    return;
  end if;

  insert into model_versions (version, mode, algorithm, targets)
  values ('dev-mock-1.0', 'mock', 'development-mock (deterministic seeded function)', array['stunting', 'underweight'])
  on conflict (version, mode) do update set algorithm = excluded.algorithm
  returning id into stunting_version_id;

  underweight_version_id := stunting_version_id;

  insert into children (sex, created_by) values ('male', actor_id) returning id into child_1;
  insert into children (sex, created_by) values ('female', actor_id) returning id into child_2;

  -- Child 1: two assessments showing a worsening stunting trend
  insert into assessments (child_id, performed_by, input_data, assessed_at)
  values (
    child_1, actor_id,
    '{"CAGE": 18, "HL4": "1.0", "CA31": "1.0", "IM2": "1.0", "BD2": "1.0", "cdisability": "2.0", "cinsurance": "2.0", "melevel": "1.0", "caretakerdis": "2.0", "HH6": "2.0", "HH7": "1.0", "windex5": "2.0", "religion": "1.0", "ethnicity": "1.0", "CA1": "1.0", "CA14": "1.0", "CA16": "1.0", "CA17": "1.0", "TN3": "1.0", "EC1": "1.0"}'::jsonb,
    now() - interval '60 days'
  ) returning id into a1_id;

  insert into assessment_predictions (assessment_id, target, predicted_label, probability, model_version_id, decision_threshold)
  values
    (a1_id, 'stunting', 'not_at_risk', 0.32, stunting_version_id, 0.5),
    (a1_id, 'underweight', 'not_at_risk', 0.21, underweight_version_id, 0.275);

  insert into assessments (child_id, performed_by, input_data, assessed_at)
  values (
    child_1, actor_id,
    '{"CAGE": 20, "HL4": "1.0", "CA31": "1.0", "IM2": "2.0", "BD2": "1.0", "cdisability": "2.0", "cinsurance": "2.0", "melevel": "1.0", "caretakerdis": "2.0", "HH6": "2.0", "HH7": "1.0", "windex5": "2.0", "religion": "1.0", "ethnicity": "1.0", "CA1": "1.0", "CA14": "1.0", "CA16": "1.0", "CA17": "1.0", "TN3": "1.0", "EC1": "1.0"}'::jsonb,
    now() - interval '5 days'
  ) returning id into a2_id;

  insert into assessment_predictions (assessment_id, target, predicted_label, probability, model_version_id, decision_threshold)
  values
    (a2_id, 'stunting', 'at_risk', 0.71, stunting_version_id, 0.5),
    (a2_id, 'underweight', 'not_at_risk', 0.34, underweight_version_id, 0.275);

  -- Child 2: single assessment (insufficient history for a trend)
  insert into assessments (child_id, performed_by, input_data, assessed_at)
  values (
    child_2, actor_id,
    '{"CAGE": 10, "HL4": "2.0", "CA31": "2.0", "IM2": "1.0", "BD2": "2.0", "cdisability": "2.0", "cinsurance": "1.0", "melevel": "2.0", "caretakerdis": "2.0", "HH6": "1.0", "HH7": "2.0", "windex5": "3.0", "religion": "1.0", "ethnicity": "1.0", "CA1": "2.0", "CA14": "2.0", "CA16": "2.0", "CA17": "2.0", "TN3": "2.0", "EC1": "0.0"}'::jsonb,
    now() - interval '2 days'
  ) returning id into a3_id;

  insert into assessment_predictions (assessment_id, target, predicted_label, probability, model_version_id, decision_threshold)
  values
    (a3_id, 'stunting', 'not_at_risk', 0.18, stunting_version_id, 0.5),
    (a3_id, 'underweight', 'not_at_risk', 0.15, underweight_version_id, 0.275);

  raise notice 'Seed data inserted for actor %', actor_id;
end $$;
