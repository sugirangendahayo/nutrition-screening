-- ============================================================================
-- Move model versioning from the assessment level to the per-target
-- prediction level.
-- ============================================================================
-- The two real trained artifacts are independent models (Random Forest for
-- stunting, XGBoost for underweight) with their own version lifecycle, so a
-- single `assessments.model_version_id` cannot correctly represent "which
-- model produced this result" once both targets are real predictions from
-- different artifacts. Each `assessment_predictions` row now records its own
-- model version and the decision threshold that was applied to derive its
-- label, so an assessment remains fully reproducible per Chapter 3's
-- requirement to preserve the exact model/version used for each prediction.
-- ============================================================================

alter table assessment_predictions
  add column if not exists model_version_id uuid references model_versions (id),
  add column if not exists decision_threshold numeric;

alter table assessments
  drop column if exists model_version_id;
