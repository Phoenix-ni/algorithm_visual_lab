export interface TestCase {
  name: string;
  value: string;
  expected?: string | null;
}

export interface AlgorithmInfo {
  id: string;
  type: string;
  title: string;
  difficulty: string;
  input_label: string;
  input_hint: string;
  summary: string;
  time_complexity: string;
  space_complexity: string;
  test_cases: TestCase[];
}

export interface Step {
  index: number;
  phase: string;
  status: string;
  message: string;
  state: Record<string, any>;
  explain: string;
}

export interface RunResponse {
  algorithm_id: string;
  input: string;
  result: Record<string, any>;
  steps: Step[];
  metrics: Record<string, any>;
}

export interface CustomData {
  id: number;
  algorithm_id: string;
  name: string;
  input: string;
  created_at: string;
}

export interface SortCompareResponse {
  input: string;
  quick: RunResponse;
  bubble: RunResponse;
  summary: Record<string, any>;
}
