import pandas as pd
from typing import Dict, List


def build_prompt(question: str, df: pd.DataFrame, query_history: List[str] = None) -> str:
    """Build the Gemini prompt with schema, sample data, query history, and the question."""
    
    # Get column info
    columns = df.columns.tolist()
    dtypes = {col: str(df[col].dtype) for col in columns}
    
    # Get sample rows (first 5)
    sample_rows = df.head(5)
    sample_table = sample_rows.to_markdown(index=False)
    
    prompt = f"""You are an expert data analyst. Given the following dataset schema and sample data, analyze the user's question and generate a SQL query.

DATASET INFO:
- Row count: {len(df)}
- Columns: {', '.join(columns)}
- Column types:
"""
    for col, dtype in dtypes.items():
        prompt += f"  - {col}: {dtype}\n"
    
    prompt += f"""
SAMPLE DATA (first 5 rows):
{sample_table}
"""
    
    # Add query history if available
    if query_history:
        prompt += f"""
PREVIOUS QUERIES EXECUTED (for context on follow-up questions):
"""
        for i, query in enumerate(query_history, 1):
            prompt += f"{i}. {query}\n"
        prompt += "\nYou can reference or build upon previous queries if relevant to the current question.\n"
    
    prompt += f"""
USER QUESTION: {question}

AVAILABLE TOOLS:
1. SQL Queries - Write valid SQL SELECT statements to query the data
2. Basic Operations - If SQL is too complex, use these predefined functions:
   - groupby_agg: Aggregate data by groups
   - filter: Filter rows by condition
   - sort: Sort by column
   - count: Count rows
   - trend: Time-series analysis
   - summary: Statistical summary
   - column_selection: Select specific columns

IMPORTANT RULES:
- First, try to write a SQL query if possible
- Use meaningful column aliases (e.g., SELECT SUM(amount) as total_sales, COUNT(*) as record_count)
- If the query is too complex for SQL, respond with a JSON object using the predefined functions
- If you cannot handle the request with available tools, respond with: {{"error": "I don't have sufficient tools to handle this query. Please rephrase or ask something simpler."}}
- Never make up or hallucinate tool names or capabilities
- For follow-up questions, consider the previous queries in context

For SQL: Return ONLY the SQL query (no markdown, no explanation)
Format: SELECT column1 as readable_name1, SUM(column2) as readable_name2 FROM df WHERE condition ORDER BY readable_name2 DESC

CHART DECISION FOR SQL:
- If the query result would benefit from visualization, add a comment at the end: -- include_chart: true
- Do NOT add the comment if a chart is not needed
- Good for charts: time-series trends, categorical comparisons, top/bottom rankings
- Examples with chart: "SELECT date, SUM(amount) as daily_total FROM df GROUP BY date ORDER BY date -- include_chart: true"
- Examples without chart: "SELECT COUNT(*) as total FROM df"

IMPORTANT: Unless the user explicitly asks for a specific number of rows:
- For "top X" queries: Return up to 30 rows (no LIMIT or LIMIT 30)
- For "show me" queries: Return all matching rows (no LIMIT)
- Only use LIMIT when user specifically says "show me top 5" or "first 10"

Examples:
- "Top 5 customers by sales" -> SELECT customer, SUM(amount) as total_sales FROM df GROUP BY customer ORDER BY total_sales DESC LIMIT 30
- "Show me rows where status is Completed" -> SELECT * FROM df WHERE status = 'Completed'
- "What's the average amount?" -> SELECT AVG(amount) as average_amount FROM df
- "Daily sales summary" -> SELECT date, SUM(amount) as daily_total FROM df GROUP BY date ORDER BY date
- "Top 10 items" -> SELECT item, COUNT(*) as count FROM df GROUP BY item ORDER BY count DESC LIMIT 10

For predefined functions: Return ONLY a valid JSON object with this structure:
{{
  "query_type": "groupby_agg | filter | sort | count | trend | summary | column_selection",
  "groupby_column": "column_name",
  "agg_column": "column_name",
  "agg_function": "sum | mean | count | min | max",
  "filter_condition": "column condition",
  "sort_by": "column_name",
  "sort_ascending": true|false,
  "columns": ["col1", "col2"],
  "narrative": "Brief explanation",
  "include_chart": true|false
}}

CHART DECISION:
- Set "include_chart": true ONLY when the result would benefit from visualization
- Good for charts: time-series trends, categorical comparisons, top/bottom rankings
- NOT for charts: single values, simple counts, text-only results
- Examples where chart=true: "show me monthly sales trend", "top 5 customers", "sales by category"
- Examples where chart=false: "what is the total revenue", "how many rows", "show me all records"

For error: Return ONLY the error JSON as shown above.

Respond with ONLY SQL, JSON, or error JSON. Nothing else.
"""
    return prompt
