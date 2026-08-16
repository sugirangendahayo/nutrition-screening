import axios, { type AxiosError } from "axios";

import { supabase } from "@/lib/supabaseClient";
import type { ApiEnvelope } from "@/types";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "/api",
});

apiClient.interceptors.request.use(async (config) => {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export class ApiError extends Error {
  status: number;
  details?: Record<string, string>;

  constructor(message: string, status: number, details?: Record<string, string>) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

export async function unwrap<T>(promise: Promise<{ data: ApiEnvelope<T> }>): Promise<T> {
  try {
    const response = await promise;
    if (!response.data.success || response.data.data === null) {
      throw new ApiError(response.data.error?.message ?? "Request failed.", 400, response.data.error?.details);
    }
    return response.data.data;
  } catch (error) {
    const axiosError = error as AxiosError<ApiEnvelope<T>>;
    if (axiosError.response) {
      const envelope = axiosError.response.data;
      throw new ApiError(
        envelope?.error?.message ?? "Something went wrong. Please try again.",
        axiosError.response.status,
        envelope?.error?.details
      );
    }
    if (error instanceof ApiError) throw error;
    throw new ApiError("Could not reach the server. Check your connection and try again.", 0);
  }
}
