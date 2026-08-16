import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, PlayCircle, Save } from "lucide-react";

import { saveAssessment } from "@/api/assessments";
import { runPrediction } from "@/api/predictions";
import { ApiError } from "@/lib/apiClient";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { PageSpinner } from "@/components/ui/Spinner";
import { ChildSelector } from "@/features/screening/ChildSelector";
import {
  groupFieldsBySection,
  initialValues,
  toInputData,
  validateForm,
  type FormValues,
} from "@/features/screening/formHelpers";
import { ScreeningFormFields } from "@/features/screening/ScreeningFormFields";
import { PredictionResultView } from "@/features/results/PredictionResultView";
import { useModelInfo } from "@/context/ModelInfoContext";
import type { Child, PredictionResponse } from "@/types";

export function NewScreeningPage() {
  const { modelInfo, isLoading } = useModelInfo();
  const navigate = useNavigate();

  const [childMode, setChildMode] = useState<"new" | "existing">("new");
  const [selectedChild, setSelectedChild] = useState<Child | null>(null);
  const [values, setValues] = useState<FormValues>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [notes, setNotes] = useState("");
  const [stage, setStage] = useState<"form" | "review">("form");
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  if (isLoading) return <PageSpinner label="Loading screening form..." />;
  if (!modelInfo) {
    return <Alert tone="danger">We couldn't load the screening form. Please try again later.</Alert>;
  }
  if (!modelInfo.available) {
    return (
      <Alert tone="danger" title="No prediction model available">
        An administrator needs to install a trained model before screenings can be run.
      </Alert>
    );
  }

  const grouped = groupFieldsBySection(modelInfo.schema);
  const currentValues = Object.keys(values).length ? values : initialValues(modelInfo.schema);

  function handleChange(key: string, value: string) {
    setValues((prev) => ({ ...(Object.keys(prev).length ? prev : initialValues(modelInfo!.schema)), [key]: value }));
  }

  async function handleRunPrediction() {
    setFormError(null);
    const validationErrors = validateForm(modelInfo!.schema, currentValues);

    if (childMode === "existing" && !selectedChild) {
      setFormError("Please select an existing child, or switch to creating a new child record.");
      return;
    }

    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      setFormError("Please correct the highlighted fields before running the screening.");
      return;
    }

    setErrors({});
    setIsRunning(true);
    try {
      const inputData = toInputData(modelInfo!.schema, currentValues);
      const prediction = await runPrediction(inputData, selectedChild?.id);
      setResult(prediction);
      setStage("review");
    } catch (error) {
      if (error instanceof ApiError && error.details) {
        setErrors(error.details);
        setFormError("Please correct the highlighted fields before running the screening.");
      } else {
        setFormError(
          "We couldn't complete the screening. Please check the entered information and try again."
        );
      }
    } finally {
      setIsRunning(false);
    }
  }

  async function handleSave() {
    if (!result) return;
    setIsSaving(true);
    setFormError(null);
    try {
      const detail = await saveAssessment({
        childId: selectedChild?.id,
        inputData: result.inputData,
        notes: notes || undefined,
      });
      navigate(`/assessments/${detail.id}`);
    } catch {
      setFormError("We couldn't save this assessment. Please try again.");
    } finally {
      setIsSaving(false);
    }
  }

  if (stage === "review" && result) {
    return (
      <div className="flex flex-col gap-6">
        <Button variant="ghost" size="sm" className="w-fit" onClick={() => setStage("form")}>
          <ArrowLeft className="size-4" aria-hidden="true" />
          Back to edit input
        </Button>

        <PredictionResultView result={result} />

        <Card>
          <CardHeader>
            <CardTitle>Save this assessment</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <label className="flex flex-col gap-1.5 text-sm font-medium text-ink-800">
              Notes (optional)
              <textarea
                className="min-h-20 rounded-md border border-ink-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Any additional context for this screening..."
              />
            </label>
            {formError && <Alert tone="danger">{formError}</Alert>}
            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setStage("form")}>
                Discard and edit
              </Button>
              <Button onClick={handleSave} isLoading={isSaving}>
                <Save className="size-4" aria-hidden="true" />
                Save Assessment
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Child Record</CardTitle>
        </CardHeader>
        <CardContent>
          <ChildSelector
            mode={childMode}
            onModeChange={(mode) => {
              setChildMode(mode);
              setSelectedChild(null);
            }}
            selectedChild={selectedChild}
            onSelectChild={setSelectedChild}
          />
        </CardContent>
      </Card>

      {[...grouped.entries()].map(([sectionKey, fields]) => {
        const section = modelInfo.schema.sections.find((s) => s.key === sectionKey);
        if (!section || fields.length === 0) return null;
        return (
          <Card key={sectionKey}>
            <CardHeader>
              <CardTitle>{section.label}</CardTitle>
            </CardHeader>
            <CardContent>
              <ScreeningFormFields
                fields={fields}
                values={currentValues}
                errors={errors}
                onChange={handleChange}
              />
            </CardContent>
          </Card>
        );
      })}

      {formError && <Alert tone="danger">{formError}</Alert>}

      <div className="flex justify-end pb-4">
        <Button size="lg" onClick={handleRunPrediction} isLoading={isRunning}>
          <PlayCircle className="size-4" aria-hidden="true" />
          Run Prediction
        </Button>
      </div>
    </div>
  );
}
