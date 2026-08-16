import type { UserRole } from "@/types";

export interface NavItem {
  to: string;
  label: string;
  icon: "dashboard" | "screening" | "history" | "reports" | "model" | "users" | "settings";
  roles: UserRole[];
}

export const NAV_ITEMS: NavItem[] = [
  {
    to: "/",
    label: "Dashboard",
    icon: "dashboard",
    roles: ["administrator", "healthcare_worker", "nutrition_officer", "researcher"],
  },
  {
    to: "/screening/new",
    label: "New Screening",
    icon: "screening",
    roles: ["administrator", "healthcare_worker", "nutrition_officer"],
  },
  {
    to: "/history",
    label: "Prediction History",
    icon: "history",
    roles: ["administrator", "healthcare_worker", "nutrition_officer", "researcher"],
  },
  {
    to: "/reports",
    label: "Reports",
    icon: "reports",
    roles: ["administrator", "healthcare_worker", "nutrition_officer"],
  },
  {
    to: "/model-performance",
    label: "Model Performance",
    icon: "model",
    roles: ["administrator", "researcher"],
  },
  {
    to: "/users",
    label: "Users",
    icon: "users",
    roles: ["administrator"],
  },
  {
    to: "/settings",
    label: "Settings",
    icon: "settings",
    roles: ["administrator", "healthcare_worker", "nutrition_officer", "researcher"],
  },
];
