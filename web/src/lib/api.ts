import type { GenericResult, Patient, TwinResult } from "../types";
import { errorMessage } from "./utils";

export interface StreamEvent {
  type: "meta" | "token" | "done" | "error";
  text?: string;
  field?: string;
  result?: GenericResult & TwinResult;
  sources?: Array<Record<string, unknown>>;
  disclaimer?: string;
  clarifying_questions?: string[];
  detail?: string;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(errorMessage(data, response.statusText || "Request failed"));
  return data as T;
}

export function postJson<T>(path: string, body: unknown) {
  return request<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export function getJson<T>(path: string) {
  return request<T>(path);
}

export async function streamConsult(
  body: Record<string, unknown>,
  onEvent: (event: StreamEvent) => void,
  signal?: AbortSignal,
) {
  const response = await fetch("/api/consult/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(errorMessage(data, "The consultation could not start."));
  }
  if (!response.body) throw new Error("The server did not return a stream.");
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const chunks = buffer.split("\n\n");
    buffer = chunks.pop() || "";
    for (const chunk of chunks) {
      const line = chunk.split("\n").find((item) => item.startsWith("data:"));
      if (!line) continue;
      const event = JSON.parse(line.slice(5).trim()) as StreamEvent;
      if (event.type === "error") throw new Error(event.detail || "Consultation failed.");
      onEvent(event);
    }
  }
}
