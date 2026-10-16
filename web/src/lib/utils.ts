import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import type { Patient } from "../types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function bmiOf(patient: Patient) {
  const bmi = patient.weight_kg / Math.max((patient.height_cm / 100) ** 2, 0.1);
  return Math.round(bmi * 10) / 10;
}

export function errorMessage(data: unknown, fallback: string) {
  if (!data || typeof data !== "object") return fallback;
  const detail = (data as { detail?: unknown }).detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => (typeof item === "object" && item && "msg" in item ? String(item.msg) : String(item))).join("; ");
  }
  return fallback;
}
