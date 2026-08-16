import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "@/components/layout/AppLayout";
import { ProtectedRoute, RoleRoute } from "@/components/layout/ProtectedRoute";
import { AuthProvider } from "@/context/AuthContext";
import { ModelInfoProvider } from "@/context/ModelInfoContext";
import { AssessmentDetailPage } from "@/pages/AssessmentDetailPage";
import { ChildHistoryPage } from "@/pages/ChildHistoryPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { HistoryPage } from "@/pages/HistoryPage";
import { LoginPage } from "@/pages/LoginPage";
import { ModelPerformancePage } from "@/pages/ModelPerformancePage";
import { NewScreeningPage } from "@/pages/NewScreeningPage";
import { ReportViewPage } from "@/pages/ReportViewPage";
import { ReportsPage } from "@/pages/ReportsPage";
import { SettingsPage } from "@/pages/SettingsPage";
import { UsersPage } from "@/pages/UsersPage";

const CLINICAL_ROLES = ["administrator", "healthcare_worker", "nutrition_officer"] as const;

export default function App() {
  return (
    <AuthProvider>
      <ModelInfoProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />

            <Route element={<ProtectedRoute />}>
              <Route element={<AppLayout />}>
                <Route index element={<DashboardPage />} />
                <Route path="history" element={<HistoryPage />} />
                <Route path="assessments/:id" element={<AssessmentDetailPage />} />
                <Route path="children/:id" element={<ChildHistoryPage />} />
                <Route path="reports/:assessmentId" element={<ReportViewPage />} />
                <Route path="settings" element={<SettingsPage />} />

                <Route element={<RoleRoute allow={[...CLINICAL_ROLES]} />}>
                  <Route path="screening/new" element={<NewScreeningPage />} />
                  <Route path="reports" element={<ReportsPage />} />
                </Route>

                <Route element={<RoleRoute allow={["administrator", "researcher"]} />}>
                  <Route path="model-performance" element={<ModelPerformancePage />} />
                </Route>

                <Route element={<RoleRoute allow={["administrator"]} />}>
                  <Route path="users" element={<UsersPage />} />
                </Route>
              </Route>
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </ModelInfoProvider>
    </AuthProvider>
  );
}
