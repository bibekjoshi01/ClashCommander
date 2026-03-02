import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function scoreTone(score: number): "good" | "warn" | "critical" {
  if (score >= 85) return "good";
  if (score >= 60) return "warn";
  return "critical";
}