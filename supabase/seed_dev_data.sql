-- ============================================================================
-- DEVELOPMENT SEED DATA
-- ============================================================================
-- Optional. Populates a few sample children/assessments so the dashboard and
-- history pages are not empty while developing the UI. This is clearly
-- DEVELOPMENT DATA - do not run this against a production database.
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
  version_id uuid;
begin
  select id into actor_id from profiles order by created_at asc limit 1;

  if actor_id is null then
    raise notice 'No profiles found - sign in at least once before seeding.';
    return;
  end if;

  insert into model_versions (version, mode, algorithm, targets)
  values ('dev-mock-1.0', 'mock', 'development-mock (deterministic seeded function)', array['stunting','underweight'])
  on conflict (version, mode) do update set algorithm = excluded.algorithm
  returning id into version_id;

  insert into children (sex, created_by) values ('male', actor_id) returning id into child_1;
  insert into children (sex, created_by) values ('female', actor_id) returning id into child_2;

  -- Child 1: two assessments showing a worsening stunting trend
  with a1 as (
    insert into assessments (child_id, performed_by, model_version_id, input_data, assessed_at)
    values (
      child_1, actor_id, version_id,
      '{"child_age_months": 18, "sex": "male", "weight_kg": 9.8, "height_cm": 78.0, "breastfeeding_status": "no_longer_breastfeeding", "mother_education_level": "primary", "household_wealth_index": "poorer", "residence_type": "rural", "drinking_water_source": "unimproved", "sanitation_facility": "unimproved", "vitamin_a_supplementation": "yes", "immunization_status": "partially_immunized"}'::jsonb,
      now() - interval '60 days'
    ) returning id
  )
  insert into assessment_predictions (assessment_id, target, predicted_label, probability)
  select id, 'stunting', 'not_at_risk', 0.32 from a1
  union all
  select id, 'underweight', 'not_at_risk', 0.21 from a1;

  with a2 as (
    insert into assessments (child_id, performed_by, model_version_id, input_data, assessed_at)
    values (
      child_1, actor_id, version_id,
      '{"child_age_months": 20, "sex": "male", "weight_kg": 9.6, "height_cm": 79.0, "breastfeeding_status": "no_longer_breastfeeding", "mother_education_level": "primary", "household_wealth_index": "poorer", "residence_type": "rural", "drinking_water_source": "unimproved", "sanitation_facility": "unimproved", "vitamin_a_supplementation": "no", "immunization_status": "partially_immunized"}'::jsonb,
      now() - interval '5 days'
    ) returning id
  )
  insert into assessment_predictions (assessment_id, target, predicted_label, probability)
  select id, 'stunting', 'at_risk', 0.71 from a2
  union all
  select id, 'underweight', 'not_at_risk', 0.34 from a2;

  -- Child 2: single assessment (insufficient history for a trend)
  insert into assessments (child_id, performed_by, model_version_id, input_data, assessed_at)
  values (
    child_2, actor_id, version_id,
    '{"child_age_months": 10, "sex": "female", "weight_kg": 7.9, "height_cm": 68.0, "breastfeeding_status": "currently_breastfeeding", "mother_education_level": "secondary", "household_wealth_index": "middle", "residence_type": "urban", "drinking_water_source": "improved", "sanitation_facility": "improved", "vitamin_a_supplementation": "yes", "immunization_status": "fully_immunized"}'::jsonb,
    now() - interval '2 days'
  );

  insert into assessment_predictions (assessment_id, target, predicted_label, probability)
  select a.id, 'stunting', 'not_at_risk', 0.18 from assessments a where a.child_id = child_2
  union all
  select a.id, 'underweight', 'not_at_risk', 0.15 from assessments a where a.child_id = child_2;

  raise notice 'Seed data inserted for actor %', actor_id;
end $$;
