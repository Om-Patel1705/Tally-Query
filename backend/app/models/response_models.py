from pydantic import BaseModel
from typing import List, Any, Optional, Dict


class ColumnInfo(BaseModel):
    name: str
    dtype: str
    sample: List[Any]


class SchemaPreview(BaseModel):
    columns: List[ColumnInfo]
    row_count: int
    file_name: str


class ChartData(BaseModel):
    labels: List[str]
    values: List[float]
    x_label: str
    y_label: str


class AnswerResponse(BaseModel):
    answer: str
    chart_data: Optional[ChartData] = None
    query_type: str
    rows_analysed: int
    data: List[Dict[str, Any]] = []  # The actual result rows


class UploadResponse(BaseModel):
    session_id: str
    schema_preview: SchemaPreview

