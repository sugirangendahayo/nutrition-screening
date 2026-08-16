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

> **The trained machine learning model is not yet integrated.** The system
> runs today with a clearly labeled development/mock prediction provider so
> the full application can be built, tested, and demonstrated. See
> [`docs/MODEL_INTEGRATION.md`](docs/MODEL_INTEGRATION.md) for the exact
> procedure to plug in the real model when it is ready.

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
ML Model  (Mock provider today -> Real trained artifact later)
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
│   ├── models/                   Trained model artifacts go here (gitignored)
│   ├── tests/                    Pytest suite
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
│   ├── migrations/0001_init.sql    Full schema, triggers, RLS policies
│   └── seed_dev_data.sql            Optional development-only sample data
├── docs/
│   ├── MODEL_INTEGRATION.md         Model contract + integration steps
│   └── research/Chapter_3.md        Source research chapter
└── README.md
```

## 4. Requirements

- Node.js 18+
- Python 3.11+ (tested on 3.14)
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
3. Open the **SQL Editor** and run `supabase/migrations/0001_init.sql`. This
   creates all tables, the `user_role` enum, a trigger that auto-provisions a
   default profile for every new auth user, and Row Level Security policies.
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
| `ML_MODEL_STATUS` | backend | `development` (mock) or `production` (real model required) |
| `MODEL_MODE`, `*_MODEL_PATH`, `PREPROCESSOR_PATH`, `BACKGROUND_DATA_PATH` | backend | Real model artifact configuration - see `docs/MODEL_INTEGRATION.md` |

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

The API runs at `http://localhost:5000`.

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

Leave `ML_MODEL_STATUS=development` in `backend/.env` (the default). The
backend serves predictions from `MockModelProvider`, a deterministic
placeholder function - **not** a real ML model. Every response is tagged
`mode: "mock"` and the UI shows a persistent "Development mode" banner. This
lets you exercise the entire workflow (form -> prediction -> explanation ->
save -> history -> trend -> report) before the real model exists.

## 9. Adding the trained model

Follow [`docs/MODEL_INTEGRATION.md`](docs/MODEL_INTEGRATION.md) exactly. In
short: inspect the artifact first, reconcile `backend/app/ml/feature_schema.py`
with its real expected features, place the artifact(s) in `backend/models/`,
set `ML_MODEL_STATUS=production` with the matching `MODEL_MODE`/path
variables, and test the full workflow before considering it done.

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
