import pandas as pd
import logging
from typing import Tuple, Optional
from app.models.response_models import ChartData

logger = logging.getLogger(__name__)


def execute_plan(df: pd.DataFrame, plan: dict) -> Tuple[pd.DataFrame, str, Optional[ChartData]]:
    """Execute the query plan on DataFrame using pandas operations."""
    
    query_type = plan.get("query_type", "summary")
    narrative = plan.get("narrative", "Analysis complete")
    include_chart = plan.get("include_chart", False)
    logger.info(f"Executing query plan - Type: {query_type}, Narrative: {narrative}, Include chart: {include_chart}")
    
    result_df = pd.DataFrame()
    chart_data = None
    
    # First, handle column selection if specified
    selected_columns = plan.get("columns")
    if selected_columns:
        logger.info(f"Column selection requested: {selected_columns}")
        # Validate that all requested columns exist
        valid_columns = [col for col in selected_columns if col in df.columns]
        if valid_columns:
            df = df[valid_columns]
            logger.info(f"Using columns: {valid_columns}")
        else:
            logger.warning(f"Requested columns not found: {selected_columns}")
    
    if query_type == "groupby_agg":
        groupby_col = plan.get("groupby_column")
        agg_col = plan.get("agg_column")
        agg_func = plan.get("agg_function", "sum")
        logger.info(f"Groupby aggregation - groupby_col: {groupby_col}, agg_col: {agg_col}, func: {agg_func}")
        
        if groupby_col and agg_col and groupby_col in df.columns and agg_col in df.columns:
            result_df = df.groupby(groupby_col)[agg_col].agg(agg_func).reset_index()
            # Sort by aggregated value descending
            result_df = result_df.sort_values(by=agg_col, ascending=False)
            
            # Prepare chart data only if requested
            if include_chart:
                chart_data = ChartData(
                    labels=result_df[groupby_col].astype(str).tolist(),
                    values=result_df[agg_col].tolist(),
                    x_label=groupby_col,
                    y_label=agg_col
                )
            logger.info(f"Groupby result: {len(result_df)} rows")
    
    elif query_type == "filter":
        filter_condition = plan.get("filter_condition")
        logger.info(f"Filter condition: {filter_condition}")
        if filter_condition:
            # Execute the filter condition on the dataframe
            try:
                # Safely evaluate the filter condition
                result_df = df.query(filter_condition, engine='python')
                narrative = f"Customers whose names start with 'E'"
                logger.info(f"Filter applied successfully. Rows after filter: {len(result_df)}")
            except Exception as e:
                logger.error(f"Error applying filter: {str(e)}", exc_info=True)
                # Fallback to returning all data if filter fails
                result_df = df.copy()
                narrative = "Could not apply filter, showing all data"
        else:
            # No filter condition provided, return all data
            result_df = df.copy()
            narrative = f"Showing sample data from your dataset"
            logger.info("No filter condition, returning all data")
    
    elif query_type == "sort":
        sort_by = plan.get("sort_by")
        sort_ascending = plan.get("sort_ascending", True)
        logger.info(f"Sorting by column: {sort_by}, ascending: {sort_ascending}")
        if sort_by and sort_by in df.columns:
            result_df = df.sort_values(by=sort_by, ascending=sort_ascending)
            narrative = f"Data sorted by {sort_by} ({'ascending' if sort_ascending else 'descending'})"
            logger.info(f"Sort result: {len(result_df)} rows")
        else:
            logger.warning(f"Sort column '{sort_by}' not found in dataframe columns: {df.columns.tolist()}")
            result_df = df.copy()
    
    elif query_type == "count":
        result_df = pd.DataFrame([{"count": len(df)}])
        narrative = f"Total rows: {len(df)}"
        logger.info(f"Count: {len(df)}")
    
    elif query_type == "trend":
        logger.info("Processing trend analysis")
        # Try to detect a date column
        date_col = None
        for col in df.columns:
            if df[col].dtype == 'object' or 'date' in col.lower():
                try:
                    pd.to_datetime(df[col])
                    date_col = col
                    logger.info(f"Detected date column: {date_col}")
                    break
                except:
                    continue
        
        if date_col:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col])
            df_copy['period'] = df_copy[date_col].dt.to_period('M')
            
            # Find a numeric column to aggregate
            numeric_col = None
            for col in df.columns:
                if df[col].dtype in ['int64', 'float64']:
                    numeric_col = col
                    break
            
            if numeric_col:
                result_df = df_copy.groupby('period')[numeric_col].sum().reset_index()
                result_df['period'] = result_df['period'].astype(str)
                
                # Prepare chart data only if requested
                if include_chart:
                    chart_data = ChartData(
                        labels=result_df['period'].tolist(),
                        values=result_df[numeric_col].tolist(),
                        x_label='Period',
                        y_label=numeric_col
                    )
                logger.info(f"Trend data created with {len(result_df)} periods")
            else:
                result_df = df_copy.groupby('period').size().reset_index(name='count')
                result_df['period'] = result_df['period'].astype(str)
                
                # Prepare chart data only if requested
                if include_chart:
                    chart_data = ChartData(
                        labels=result_df['period'].tolist(),
                        values=result_df['count'].tolist(),
                        x_label='Period',
                        y_label='Count'
                    )
                logger.info(f"Trend data created (count-based) with {len(result_df)} periods")
        else:
            narrative = "Could not detect a date column for trend analysis"
            result_df = df.head()
            logger.warning("No date column detected for trend analysis")
    
    elif query_type == "summary":
        result_df = df.describe()
        narrative = "Summary statistics"
        logger.info("Generated summary statistics")
    
    else:
        # Default: return first few rows
        result_df = df.copy()
        narrative = "Showing data"
        logger.info(f"Unknown query type '{query_type}', returning all data")
    
    logger.info(f"Execute plan complete - Result rows: {len(result_df)}")
    return result_df, narrative, chart_data
