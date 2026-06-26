import pandas as pd
import numpy as np
from typing import Dict, List, Any
from app.models.response_models import SchemaPreview, ColumnInfo


def extract_schema(df: pd.DataFrame, file_name: str) -> SchemaPreview:
    columns = []
    for col in df.columns:
        dtype_str = str(df[col].dtype)
        sample_values = df[col].dropna().head(3).tolist()
        # Convert to serializable types
        sample_serializable = []
        for val in sample_values:
            if pd.isna(val):
                continue
            if isinstance(val, (pd.Timestamp, np.datetime64)):
                sample_serializable.append(str(val))
            elif hasattr(val, 'item'):  # numpy types
                sample_serializable.append(val.item())
            else:
                sample_serializable.append(val)
        
        columns.append(ColumnInfo(
            name=str(col),
            dtype=dtype_str,
            sample=sample_serializable[:3]
        ))
    
    return SchemaPreview(
        columns=columns,
        row_count=len(df),
        file_name=file_name
    )
