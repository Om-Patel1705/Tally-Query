export interface ColumnInfo {
  name: string;
  dtype: string;
  sample: any[];
}

export interface SchemaPreview {
  columns: ColumnInfo[];
  row_count: number;
  file_name: string;
}

export interface ChartData {
  labels: string[];
  values: number[];
  x_label: string;
  y_label: string;
}

export interface AnswerResponse {
  answer: string;
  chart_data: ChartData | null;
  query_type: string;
  rows_analysed: number;
  data: Record<string, any>[];  // The actual result rows
}

export interface UploadResponse {
  session_id: string;
  schema_preview: SchemaPreview;
}

export interface QueryRequest {
  session_id: string;
  question: string;
}
