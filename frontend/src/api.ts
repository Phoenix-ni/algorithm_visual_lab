import type { AlgorithmInfo, CustomData, RunResponse, SortCompareResponse } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });
  if (!response.ok) {
    let detail = `请求失败：${response.status}`;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      detail = await response.text();
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export const api = {
  listAlgorithms: () => request<AlgorithmInfo[]>("/api/algorithms"),
  randomInput: (algorithmId: string) => request<{ input: string }>(`/api/algorithms/${algorithmId}/random`),
  runAlgorithm: (algorithmId: string, input: string) =>
    request<RunResponse>(`/api/algorithms/${algorithmId}/run`, {
      method: "POST",
      body: JSON.stringify({ input })
    }),
  listCustomData: (algorithmId: string) =>
    request<CustomData[]>(`/api/custom-data?algorithm_id=${encodeURIComponent(algorithmId)}`),
  saveCustomData: (algorithmId: string, name: string, input: string) =>
    request<CustomData>("/api/custom-data", {
      method: "POST",
      body: JSON.stringify({ algorithm_id: algorithmId, name, input })
    }),
  deleteCustomData: (id: number) =>
    request<{ deleted: boolean }>(`/api/custom-data/${id}`, {
      method: "DELETE"
    }),
  exportLog: (payload: RunResponse) =>
    request<{ filename: string; content: string }>("/api/logs/export", {
      method: "POST",
      body: JSON.stringify({
        algorithm_id: payload.algorithm_id,
        input: payload.input,
        result: payload.result,
        steps: payload.steps,
        metrics: payload.metrics
      })
    }),
  compareSort: (input: string) =>
    request<SortCompareResponse>("/api/compare/sort", {
      method: "POST",
      body: JSON.stringify({ input })
    }),
  predictDrawnDigit: (image: number[][]) =>
    request<RunResponse>("/api/cnn/draw-predict", {
      method: "POST",
      body: JSON.stringify({ image })
    })
};
