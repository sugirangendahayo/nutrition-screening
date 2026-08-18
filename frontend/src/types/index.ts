export type UserRole =
  | "administrator"
  | "healthcare_worker"
  | "nutrition_officer"
  | "researcher";

export interface Profile {
  id: string;
  email?: string | null;
  full_name: string | null;
  role: UserRole;
  facility?: string | null;
}

export type PredictionTarget = "stunting" | "underweight";
export type PredictedLabel = "at_risk" | "not_at_risk";
export type ExplanationMethod =
  | "shap_local"
  | "global_importance"
  | "development_mock"
  | "unavailable";
export type ModelMode = "mock" | "real";
export type TrendStatus = "improving" | "worsening" | "stable" | "insufficient_data";

export type FieldInputType = "number" | "select" | "radio";
export type LabelConfidence = "confirmed" | "standard_convention" | "unverified";

export interface FieldOption {
  value: string;
  label: string;
}

export interface FeatureField {
  key: string;
  label: string;
  section: string;
  inputType: FieldInputType;
  labelConfidence: LabelConfidence;
  required: boolean;
  unit: string | null;
  min: number | null;
  max: number | null;
  step: number | null;
  options: FieldOption[];
  helpText: string | null;
}

export interface FormSection {
  key: string;
  label: string;
  order: number;
}

export interface ModelSchema {
  sections: FormSection[];
  fields: FeatureField[];
  targets: PredictionTarget[];
}

export interface ModelTargetInfo {
  version: string;
  algorithm: string;
  decisionThreshold: number;
}

export interface ModelInfo {
  available: boolean;
  mode?: ModelMode;
  targets?: Record<PredictionTarget, ModelTargetInfo>;
  explanationMethod?: string;
  note?: string;
  error?: string | null;
  schema: ModelSchema;
}

export interface ModelVersionRecord {
  id: string;
  version: string;
  mode: ModelMode;
  targets: PredictionTarget[];
  metrics: ModelMetrics | null;
  trained_at: string | null;
  is_active: boolean;
  created_at: string;
}

export interface ConfusionMatrix {
  trueNegative: number;
  falsePositive: number;
  falseNegative: number;
  truePositive: number;
}

export interface ModelMetrics {
  stunting?: {
    accuracy: number;
    precision: number;
    recall: number;
    f1: number;
    rocAuc: number;
    confusionMatrix: ConfusionMatrix;
  };
  underweight?: {
    accuracy: number;
    precision: number;
    recall: number;
    f1: number;
    rocAuc: number;
    confusionMatrix: ConfusionMatrix;
  };
}

export interface TargetPrediction {
  target: PredictionTarget;
  predictedLabel: PredictedLabel;
  probability: number | null;
  decisionThreshold: number;
  modelVersion: string;
  algorithm: string;
}

export interface ExplanationItem {
  featureKey: string;
  featureLabel: string;
  contribution: number;
  direction: "increases_risk" | "decreases_risk" | "neutral";
}

export interface TargetExplanation {
  target: PredictionTarget;
  method: ExplanationMethod;
  items: ExplanationItem[];
  note: string;
}

export interface TrendResult {
  status: "available" | "insufficient_data";
  perTarget: Record<PredictionTarget, TrendStatus>;
  overall: TrendStatus;
  series: Array<{
    assessedAt: string;
    predictions: Record<PredictionTarget, { predictedLabel: PredictedLabel | null; probability: number | null }>;
  }>;
}

export interface PredictionResponse {
  mode: ModelMode;
  targets: TargetPrediction[];
  explanations: TargetExplanation[];
  generatedAt: string;
  inputData: Record<string, string | number>;
  trendPreview?: TrendResult;
}

export interface Child {
  id: string;
  child_code: string;
  sex: "male" | "female";
  created_at: string;
}

export interface AssessmentSummary {
  id: string;
  childId: string;
  childCode: string | null;
  sex: "male" | "female" | null;
  performedBy: string;
  assessedAt: string;
  predictions: Record<PredictionTarget, TargetPrediction>;
}

export interface AssessmentDetail {
  id: string;
  child: Child;
  performedBy: string;
  performedByName?: string | null;
  inputData: Record<string, string | number>;
  notes: string | null;
  assessedAt: string;
  mode: ModelMode | null;
  predictions: Record<PredictionTarget, TargetPrediction>;
  explanations: TargetExplanation[];
  trend?: TrendResult;
}

export interface DashboardSummary {
  childrenAssessed: number;
  assessmentsThisMonth: number;
  stuntingAtRiskThisMonth: number;
  underweightAtRiskThisMonth: number;
  recentAssessments: Array<{
    id: string;
    childCode: string | null;
    assessedAt: string;
    predictions: Record<string, TargetPrediction>;
  }>;
  hasData: boolean;
}

export interface ManagedUser {
  id: string;
  full_name: string;
  role: UserRole;
  facility: string | null;
  is_active: boolean;
  created_at: string;
}

export interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
  error: { message: string; details?: Record<string, string> } | null;
}
