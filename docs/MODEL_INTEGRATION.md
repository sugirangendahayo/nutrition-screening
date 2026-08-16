# Model Integration Guide

This document describes exactly what the Flask backend expects from a trained
model artifact, and the step-by-step procedure for integrating one when it
becomes available. It exists so that a real `.pkl`/`.joblib` model can be
plugged into the system **without rewriting the frontend, database schema, or
prediction workflow.**

> Read this before touching any code when the real model arrives. Do not
> assume the artifact's shape - inspect it first (Step 1 below).

## 1. Current state (development)

Until a trained artifact is supplied, the backend runs with
`ML_MODEL_STATUS=development`, which activates `MockModelProvider`
(`backend/app/ml/mock_provider.py`). This provider:

- Produces deterministic but clinically meaningless predictions from a seeded
  toy function of the submitted form values.
- Is clearly tagged `mode: "mock"` in every API response and surfaced in the
  UI as a "Development mode" banner.
- Exists purely so the full workflow (form -> validation -> prediction ->
  explanation -> save -> history -> trend -> report) can be built and tested
  before the real model exists.

**It is never presented to end users as a real prediction, and must never be
used for `ML_MODEL_STATUS=production`.**

## 2. The provider abstraction

```
ModelProvider (backend/app/ml/base_provider.py)
    |
    +-- MockModelProvider   (backend/app/ml/mock_provider.py)
    |
    +-- RealModelProvider   (backend/app/ml/real_provider.py)
```

`app/ml/provider_factory.py` selects the active provider based on
`ML_MODEL_STATUS`. All routes and services depend only on the abstract
`ModelProvider` interface (`predict(features) -> PredictionBundle`), so
swapping providers - or upgrading the real model later - never requires
touching the API routes or the frontend.

## 3. What the backend currently assumes about the real model

These are **working assumptions only**, encoded in `real_provider.py`. They
**must be validated** against the actual artifact before enabling
`ML_MODEL_STATUS=production`:

| Assumption | Where | What to verify |
|---|---|---|
| Two binary classifiers (or one multi-output model) predicting "at risk" vs "not at risk" for stunting and underweight | `RealModelProvider` | Confirm the model's actual output structure |
| `predict_proba` is available and returns per-class probabilities | `_TargetModel.predict_proba` | Confirm the estimator supports `predict_proba`; if not, only hard labels will be used |
| The positive ("at risk") class is `1`, `"1"`, `"at_risk"`, `"yes"`, or `True`, else the last class in `classes_` | `_positive_class_index` | Confirm which label/encoding means "at risk" in the trained model |
| The model accepts a pandas DataFrame with columns exactly matching `feature_schema.FEATURE_FIELDS` keys, in that order, OR a `PREPROCESSOR_PATH` artifact transforms that raw DataFrame into the model's expected input | `real_provider.py` | Confirm what preprocessing (encoding, scaling, imputation) the model expects and whether it is bundled into the model as a `Pipeline` or must be applied separately |

## 4. Step-by-step integration procedure

### Step 1 - Inspect the artifact

Do this in a scratch script or notebook, never assume:

```python
import joblib
model = joblib.load("path/to/model.joblib")

print(type(model))                      # sklearn Pipeline? bare estimator? dict?
print(getattr(model, "classes_", None))  # class labels and their order
print(getattr(model, "feature_names_in_", None))  # expected feature names, if available
print(getattr(model, "named_steps", None))  # pipeline steps, if it's a Pipeline
print(hasattr(model, "predict_proba"))
```

Answer these questions before writing any integration code:

1. Is this one model for both targets, or two separate models?
2. Does it expose `predict_proba`? If not, only hard-label predictions are
   possible.
3. What are the exact expected input feature names, order, and types?
4. Is preprocessing (encoding/scaling/imputation) already inside the model
   (a `Pipeline`), or must it be applied separately before calling `.predict`?
5. What does the positive class ("at risk") look like in `classes_`?
6. Is the model tree-based (`feature_importances_`) or linear (`coef_`), or
   neither?

### Step 2 - Reconcile the feature schema

Update `backend/app/ml/feature_schema.py` (`FEATURE_FIELDS`) so its keys,
order, types, and allowed values **exactly** match what the model expects.
This file is the single source of truth: the frontend fetches it via
`GET /api/model/info` and renders the screening form directly from it, so a
single, well-reviewed change here keeps frontend and backend in sync.

**Do not invent or guess feature names.** If the model was trained on
different fields than the current placeholder list (which was drawn from
Chapter 3's candidate predictors for development purposes only), replace them
with the real ones.

### Step 3 - Place the artifact(s)

```
backend/models/stunting_model.joblib
backend/models/underweight_model.joblib
```

or, for a single multi-output model:

```
backend/models/model.joblib
```

and, if training used separate preprocessing:

```
backend/models/preprocessor.joblib
```

and, to enable local SHAP explanations, a small representative background
sample (30-100 rows resembling the training distribution, saved as a
joblib-pickled pandas DataFrame with the same raw columns as the feature
schema):

```
backend/models/background_sample.joblib
```

### Step 4 - Configure environment variables

In `backend/.env`:

```
ML_MODEL_STATUS=production
MODEL_MODE=dual_model            # or single_multioutput
STUNTING_MODEL_PATH=models/stunting_model.joblib
UNDERWEIGHT_MODEL_PATH=models/underweight_model.joblib
PREPROCESSOR_PATH=models/preprocessor.joblib   # leave blank if not needed
BACKGROUND_DATA_PATH=models/background_sample.joblib  # leave blank to fall back to global importance
MODEL_VERSION=v1.0-random-forest
```

### Step 5 - Test the provider in isolation

Before wiring it into the API, load `RealModelProvider` directly in a Python
shell with a handful of known sample inputs and confirm the output makes
sense (labels, probability range, explanation items).

### Step 6 - Test end-to-end

Restart the Flask server and run the full workflow from the React UI: new
screening -> run prediction -> review result -> save assessment -> view
history -> view trend -> generate report. Confirm the "Development mode"
banner has disappeared and results are tagged `mode: "real"`.

### Step 7 - Record evaluation metrics

If offline evaluation (accuracy, precision, recall, F1, ROC-AUC, confusion
matrix per Chapter 3, Section 3.3.2) has been computed, insert it into the
`model_versions.metrics` column (JSON) for the corresponding version so it
appears on the Model Performance page. Do not fabricate these numbers -
leave them null until real evaluation results exist.

## 5. Explanation method selection

`backend/app/ml/explainer.py` automatically prefers a **local SHAP
explanation** (per-prediction) when a background sample is configured, and
falls back to **global feature importance** (`feature_importances_` /
`coef_`) when it is not. The UI labels these differently and never conflates
the two:

- `shap_local` -> "Local explanation (SHAP)" - specific to this prediction.
- `global_importance` -> "Model Feature Importance" - general to the model.
- `development_mock` -> explicitly marked as a development placeholder.
- `unavailable` -> shown as such; no numbers are fabricated.

## 6. Multi-output vs dual-model support

- **`dual_model`** (default): two independent estimators, one per target.
  Simplest to reason about and to explain separately.
- **`single_multioutput`**: one estimator (e.g. `MultiOutputClassifier`) used
  for both targets. `RealModelProvider` treats it as a shared `_TargetModel`
  instance for each target; if its `predict_proba` output shape differs per
  target, this will need a small adaptation in `real_provider.py` - inspect
  the model's actual output shape first (Step 1) before assuming this works
  as-is.

## 7. What must never happen

- Never present the mock provider's output as a real prediction outside of
  development/testing.
- Never let the frontend define its own, independent list of model features.
- Never fabricate a percentage, importance value, or metric that does not
  come from the model, SHAP, or a stored evaluation result.
- Never skip Step 1 (inspection) and guess the artifact's contract.
