import json
from typing import Dict, Any, Tuple


def parse_gemini_response(response_text: str) -> Dict[str, Any]:
    """Safely parse Gemini JSON response."""
    # Try to extract JSON from the response
    response_text = response_text.strip()
    
    # Remove markdown code blocks if present
    if response_text.startswith("```"):
        response_text = response_text.strip("`")
        if response_text.startswith("json"):
            response_text = response_text[4:].strip()
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Gemini response as JSON: {e}")


def parse_sql_response(response_text: str) -> Tuple[str, bool]:
    """Parse SQL response and extract include_chart flag from comments."""
    sql_query = response_text.strip()
    include_chart = False
    
    # Check for include_chart comment
    if "-- include_chart: true" in sql_query.lower():
        include_chart = True
        # Remove the comment from the query
        sql_query = sql_query.replace("-- include_chart: true", "").replace("-- include_chart: True", "")
        sql_query = sql_query.strip()
    
    return sql_query, include_chart
