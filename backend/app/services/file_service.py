import pandas as pd
import io
from typing import Tuple
from fastapi import HTTPException


def parse_file(file_content: bytes, filename: str) -> Tuple[pd.DataFrame, str]:
    """Parse CSV or Excel file and return DataFrame with cleaned column names."""
    
    if filename.endswith('.csv'):
        try:
            df = pd.read_csv(io.BytesIO(file_content))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse CSV file: {str(e)}")
    elif filename.endswith('.xlsx'):
        try:
            df = pd.read_excel(io.BytesIO(file_content))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse Excel file: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Only .csv and .xlsx are allowed.")
    
    if df.empty:
        raise HTTPException(status_code=400, detail="File is empty or could not be parsed.")
    
    # Clean column names: strip whitespace
    df.columns = df.columns.str.strip()
    
    # Infer dtypes
    df = df.infer_objects()
    
    return df, filename


def validate_file_size(file_size: int, max_size_mb: int = 10) -> None:
    """Validate file size doesn't exceed maximum."""
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=400, 
            detail=f"File size exceeds maximum of {max_size_mb}MB"
        )
