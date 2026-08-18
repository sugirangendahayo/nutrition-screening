# Nutrition Screening Decision Support System

A machine learning-based decision support system for nutrition screening of
children under five, built around the research described in Chapter 3 (see
`docs/research/Chapter_3.md`) using the Central African Republic Multiple
Indicator Cluster Survey (MICS6) dataset context.

The system predicts two specific outcomes for each screening:

- **Stunting** risk (low height-for-age)
- **Underweight** risk (low weight-for-age)

It is a **decision-support tool**, not a diagnostic system. Every result
screen and report states this explicitly.

> **The trained machine learning models are integrated and active by
> default** (`ML_MODEL_STATUS=production`): a Random Forest for stunting and
> an XGBoost model for underweight, both trained on the CAR MICS6 dataset
> (see [`docs/MODEL_INFO.md`](docs/MODEL_INFO.md) and
> [`docs/MODEL_INTEGRATION.md`](docs/MODEL_INTEGRATION.md)). A clearly
> labeled development/mock provider is still available as a fallback (set
> `ML_MODEL_STATUS=development`) for working on the app without the trained
> artifacts present.
>
> Several raw MICS6 predictor codes (e.g. `CA31`, `HH7`, `religion`,
> `ethnicity`) could not be matched to a confirmed human-readable label
> because the CAR codebook/SPSS value labels were not available at
> integration time. These fields are shown with their raw code and a visible
> "Unverified label" badge rather than a guessed clinical label - see
> `docs/MODEL_INFO.md` section on label confidence.

---

## 1. Project overview

Healthcare workers and nutrition officers record a child's demographic,
maternal, household, and health/environment information. The system
validates the input, runs it through a machine learning model, and returns
separate risk predictions (with probabilities and an explanation) for
stunting and underweight. Results can be saved as an **assessment**, viewed
again later, compared over time as a **nutrition screening trend** for the
same child, and exported as a printable **report**.

Roles, from Chapter 3, Section 3.3.4:

| Role | Can do |
|---|---|
| **Administrator** | Manage users, manage model configuration, view model performance, view all activity |
| **Healthcare Worker** | Enter child information, run screenings, view results, view their history, generate reports |
| **Nutrition Officer** | Perform/view screenings, view prediction history, analyze trends, view/export reports |
| **Researcher** | View model performance, analyze prediction outcomes and evaluation data |

## 2. Architecture

```
React (Vite + TypeScript + Tailwind)
        |
        |  Axios, bearer token from Supabase Auth session
        v
Flask API (Python)
        |
        |  ModelProvider abstraction
        v
ML Models  (RealModelProvider: RandomForest for stunting, XGBoost for
            underweight - falls back to a labeled MockModelProvider if
            ML_MODEL_STATUS=development)
        |
        v
Supabase PostgreSQL  (via service-role key, backend-only)
```

- **Supabase Auth** issues the session/JWT the frontend attaches to every API
  call. The Flask backend independently verifies that JWT and looks up the
  caller's role from the `profiles` table - it never trusts a role claim
  from the client.
- **Flask** is the only component that talks to Postgres directly (using the
  service-role key), and is responsible for all authorization decisions,
  input validation, preprocessing, invoking the model, and persistence.
- **Row Level Security** policies exist in Postgres as defense-in-depth, in
  case anything ever queries Supabase directly, but are not the primary
  authorization mechanism.

## 3. Project structure

```
nutrition-screening/
├── backend/                    Flask API
│   ├── app/
│   │   ├── config.py            Environment-driven configuration
│   │   ├── ml/                  Model abstraction (mock/real providers, schema, explainer)
│   │   ├── routes/               Blueprints: auth/profile, children, assessments,
│   │   │                         predictions, dashboard, reports, model, users
│   │   ├── services/             Business logic (Supabase queries, trend calc, reports)
│   │   ├── schemas/              (reserved for future request/response schemas)
│   │   └── utils/                 Auth, validation, response helpers
│   ├── models/                   Trained model artifacts go here (gitignored):
│   │                             stunting_model.pkl, underweight_model.pkl
│   ├── scripts/verify_artifacts.py  Diagnostic script: loads both artifacts and
│   │                                 runs a sample prediction end-to-end
│   ├── tests/                    Pytest suite (incl. tests against the real artifacts)
│   ├── requirements.txt
│   └── run.py
├── frontend/                    React app
│   └── src/
│       ├── api/                  One module per backend resource (axios calls)
│       ├── components/ui/         Reusable design-system components
│       ├── components/layout/      Sidebar, topbar, route guards, dev-mode banner
│       ├── context/                Auth + model-info React contexts
│       ├── features/screening/      Dynamic form driven by the backend feature schema
│       ├── features/results/        Prediction result, explanation, trend components
│       ├── pages/                   Route-level pages
│       └── types/                   Shared TypeScript types
├── supabase/
│   ├── migrations/0001_init.sql              Full schema, triggers, RLS policies
│   ├── migrations/0002_per_target_model_version.sql
│   │                                          Per-target model version/threshold on predictions
│   └── seed_dev_data.sql                      Optional development-only sample data
├── docs/
│   ├── MODEL_INFO.md                Findings from inspecting the trained artifacts
│   ├── MODEL_INTEGRATION.md         Model contract + integration steps
│   └── research/Chapter_3.md        Source research chapter
└── README.md
```

## 4. Requirements

- Node.js 18+
- **Python 3.12 or earlier.** `scikit-learn` is pinned to `1.6.1` to exactly
  match the version used to train/pickle the supplied model artifacts (newer
  scikit-learn cannot load them - see `backend/requirements.txt` and
  `docs/MODEL_INFO.md`), and 1.6.1 has no wheels for Python 3.13/3.14.
- A Supabase project (free tier is sufficient for development)

## 5. Database setup (Supabase)

1. Create a project at [supabase.com](https://supabase.com).
2. In **Project Settings -> API**, copy:
   - **Project URL** -> `SUPABASE_URL` / `VITE_SUPABASE_URL`
   - **anon public key** -> `VITE_SUPABASE_ANON_KEY`
   - **service_role key** -> `SUPABASE_SERVICE_ROLE_KEY` (backend only - never
     expose this to the frontend)
   - **JWT Secret** (Project Settings -> API -> JWT Settings) ->
     `SUPABASE_JWT_SECRET`
3. Open the **SQL Editor** and run the three migrations in
   `supabase/migrations/`, **in numeric order**:
   `0001_init.sql`, then `0002_per_target_model_version.sql`, then
   `0003_grant_public_schema_privileges.sql`. Together they create all
   tables, the `user_role` enum, a trigger that auto-provisions a default
   profile for every new auth user, Row Level Security policies, per-target
   model version/decision-threshold tracking on each prediction, and the
   base table privileges the backend's `service_role` key needs (on newer
   projects, the "Automatically expose new tables" setting defaults to off,
   so this grant no longer happens automatically - see the comment at the
   top of `0003_grant_public_schema_privileges.sql`).
4. **Create your first user.** In Supabase Dashboard -> Authentication ->
   Users, click "Add user" and create an account with a password (or sign up
   from the app once it's running). A `profiles` row is created automatically
   with role `healthcare_worker`.
5. **Promote that user to administrator** by running this in the SQL editor
   (replace the email):

   ```sql
   update profiles
   set role = 'administrator'
   where id = (select id from auth.users where email = 'you@example.com');
   ```

6. From then on, use the in-app **Users** page (as an administrator) to
   create additional accounts with the correct role - there is no public
   self-registration, matching the "Contact Administrator" model.
7. (Optional) Run `supabase/seed_dev_data.sql` in the SQL editor to populate a
   couple of sample children/assessments for UI development. This is clearly
   development-only data and should never be run against a production
   database.

## 6. Environment variables

Copy the example files and fill them in:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

See `backend/.env.example` and `frontend/.env.example` for the full,
documented list. Key ones:

| Variable | Where | Purpose |
|---|---|---|
| `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET` | backend | Server-side Supabase access & JWT verification |
| `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` | frontend | Browser-side Supabase Auth |
| `ML_MODEL_STATUS` | backend | `production` (default; real models, requires the artifacts below) or `development` (mock) |
| `STUNTING_MODEL_PATH`, `UNDERWEIGHT_MODEL_PATH` | backend | Paths to the two trained `.pkl` artifacts (default `models/stunting_model.pkl` / `models/underweight_model.pkl`) |
| `STUNTING_MODEL_VERSION`, `UNDERWEIGHT_MODEL_VERSION` | backend | Free-text version labels stored with every prediction |
| `STUNTING_DECISION_THRESHOLD`, `UNDERWEIGHT_DECISION_THRESHOLD` | backend | `predict_proba()` cutoffs chosen during training by maximizing F1 (0.5 / 0.275 by default - see `docs/MODEL_INFO.md`) |

## 7. Installation & running

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then fill in your Supabase values
python run.py
```

The API runs at `http://localhost:5000`. On startup with the default
`ML_MODEL_STATUS=production`, place the two trained artifacts at
`backend/models/stunting_model.pkl` and `backend/models/underweight_model.pkl`
(gitignored - not committed to source control), then confirm they load
correctly with:

```bash
python scripts/verify_artifacts.py
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env            # then fill in your Supabase values
npm run dev
```

The app runs at `http://localhost:5173` and proxies `/api` to the Flask
server during development (see `vite.config.ts`).

## 8. Running without the trained model (development mode)

Set `ML_MODEL_STATUS=development` in `backend/.env` if the trained artifacts
are temporarily unavailable (e.g. working on the app without copying the
`.pkl` files). The backend then serves predictions from `MockModelProvider`,
a deterministic placeholder function - **not** a real ML model. Every
response is tagged `mode: "mock"` and the UI shows a persistent "Development
mode" banner. This lets you exercise the entire workflow (form -> prediction
-> explanation -> save -> history -> trend -> report) without the real
artifacts present.

## 9. Updating or replacing the trained model

The two trained artifacts (`stunting_model.pkl` - Random Forest,
`underweight_model.pkl` - XGBoost) are already integrated per
`docs/MODEL_INFO.md` and `docs/MODEL_INTEGRATION.md`. If a retrained or
updated artifact is supplied later, follow
[`docs/MODEL_INTEGRATION.md`](docs/MODEL_INTEGRATION.md) exactly: inspect the
new artifact first (do not assume its shape matches the current one),
reconcile `backend/app/ml/feature_schema.py` if its expected raw features
changed, replace the file(s) in `backend/models/`, run
`python scripts/verify_artifacts.py`, update the corresponding
`*_MODEL_VERSION`/`*_DECISION_THRESHOLD` env vars, and test the full workflow
before considering it done.

## 10. API endpoints

All responses use the envelope `{ "success": bool, "data": ..., "error": ... }`.

| Method & path | Auth | Purpose |
|---|---|---|
| `GET /api/profile` | any | Current user's profile/role |
| `GET /api/model/info` | any | Model status + feature schema (drives the form) |
| `GET /api/model/performance` | admin, researcher | Stored evaluation metrics per model version |
| `POST /api/predictions` | admin, HW, NO | Run a prediction - **not persisted** |
| `POST /api/assessments` | admin, HW, NO | Persist a screening (child + input + re-computed prediction) |
| `GET /api/assessments` | any | List assessments (`?mine=true`, `?childId=`) |
| `GET /api/assessments/:id` | any | Assessment detail + trend |
| `GET /api/children` | any | Search/list children (`?search=`) |
| `GET /api/children/:id/history` | any | Child's assessments + trend |
| `GET /api/dashboard` | any | Aggregate statistics (real data only) |
| `GET /api/reports` | any | Report generation log |
| `GET /api/reports/assessment/:id` | any | Report data for an assessment |
| `POST /api/reports` | admin, HW, NO | Generate (and log) a report |
| `GET /api/users` / `POST /api/users` / `PATCH /api/users/:id` | admin | User management |

## 11. Authentication & authorization

Supabase Auth handles credential storage, hashing, and session tokens - this
system never implements password hashing itself. The frontend attaches the
Supabase access token to every API call; the backend verifies it with
`SUPABASE_JWT_SECRET` and looks up the caller's role from `profiles` on every
request. Every mutating/sensitive route uses `require_role(...)` -
authorization is enforced server-side, not just by hiding buttons in the UI.

## 12. Prediction workflow

```
Enter child & screening information
        v
Client-side validation (UX) + server-side validation (authoritative)
        v
POST /api/predictions -> ModelProvider.predict()
        v
Stunting prediction + Underweight prediction (label, probability)
        v
Explanation (SHAP local, or global importance, or dev-mock - clearly labeled)
        v
Result reviewed in the UI (nothing saved yet)
        v
POST /api/assessments -> backend re-runs the model from the submitted input
        (never trusts a client-supplied result) and persists everything
        v
Prediction History / Child Nutrition Trend / Report
```

## 13. Testing

```bash
cd backend
source venv/bin/activate
pytest
```

Covers: input validation, the mock provider's behavior and determinism,
trend calculation (improving/worsening/stable/insufficient data), the
prediction and model-info endpoints (including the missing-model / 503
case), role-based authorization, and the assessment/dashboard service
persistence and data-shaping logic (via a lightweight fake Supabase client).

```bash
cd frontend
npm run build   # type-checks (tsc -b) and builds
npm run lint
```

## 14. Troubleshooting

| Symptom | Likely cause |
|---|---|
| `Server is not configured for authentication` | `SUPABASE_JWT_SECRET` missing in `backend/.env` |
| `No profile found for this account` | The `profiles` row wasn't created - re-run the migration trigger, or check Authentication -> Users in Supabase |
| Screening form is empty / "No prediction model available" | Backend can't reach Supabase, or `ML_MODEL_STATUS=production` with a missing artifact path - check the Flask logs |
| CORS errors in the browser console | `CORS_ORIGINS` in `backend/.env` doesn't include your frontend's origin |
| `pandas`/`numpy`/`shap` fail to install | Your Python version may not have prebuilt wheels yet for the pinned minimum versions - see the comment in `backend/requirements.txt` |
