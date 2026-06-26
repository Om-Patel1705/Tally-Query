import pandas as pd
import duckdb
import logging
from typing import Tuple, Optional
from app.models.response_models import ChartData

logger = logging.getLogger(__name__)


def execute_sql(df: pd.DataFrame, sql_query: str, include_chart: bool = False) -> Tuple[pd.DataFrame, str, Optional[ChartData]]:
    """
    Execute SQL query on DataFrame using DuckDB.
    
    Args:
        df: Input DataFrame
        sql_query: SQL SELECT statement
        include_chart: Whether to generate chart data from result
        
    Returns:
        result_df, narrative, chart_data
    """
    try:
        logger.info(f"Executing SQL: {sql_query}")
        
        # Register DataFrame as 'df' in DuckDB
        result = duckdb.query(sql_query.replace("df", "df")).to_df()
        
        logger.info(f"SQL executed successfully. Result rows: {len(result)}")
        
        # Generate narrative
        narrative = f"Query executed successfully"
        
        # Generate chart data only if requested
        chart_data = None
        if include_chart and len(result) > 0 and len(result.columns) >= 2:
            # Look for a date column and a numeric column
            date_col = None
            numeric_col = None
            
            # Find date column
            for col in result.columns:
                try:
                    pd.to_datetime(result[col])
                    date_col = col
                    logger.info(f"Detected date column: {date_col}")
                    break
                except:
                    continue
            
            # Find numeric column
            if date_col:
                for col in result.columns:
                    if col != date_col and pd.api.types.is_numeric_dtype(result[col]):
                        numeric_col = col
                        logger.info(f"Detected numeric column: {numeric_col}")
                        break
            else:
                for col in result.columns:
                    if result[col].dtype == 'object' and not date_col:
                        date_col = col
                    elif pd.api.types.is_numeric_dtype(result[col]) and not numeric_col:
                        numeric_col = col
            
            if date_col and numeric_col:
                chart_data = ChartData(
                    labels=result[date_col].astype(str).tolist(),
                    values=result[numeric_col].tolist(),
                    x_label=date_col,
                    y_label=numeric_col
                )
                logger.info(f"Generated chart data with {len(result)} points")
        
        return result, narrative, chart_data
        
    except Exception as e:
        logger.error(f"SQL execution failed: {str(e)}", exc_info=True)
        raise Exception(f"SQL Error: {str(e)}")
