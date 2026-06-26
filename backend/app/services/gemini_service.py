from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import logging
import json
from typing import List
from app.core.config import settings
from app.utils.prompt_builder import build_prompt
from app.utils.response_parser import parse_gemini_response

logger = logging.getLogger(__name__)


def get_gemini_response(question: str, df, query_history: List[str] = None) -> dict:
    """Send question to Gemini and get either SQL or JSON query plan."""
    
    # Build the prompt with query history
    prompt = build_prompt(question, df, query_history)
    logger.info(f"Built prompt for question: {question}")
    if query_history:
        logger.info(f"Including {len(query_history)} previous queries in context")
    logger.debug(f"Prompt content:\n{prompt}")
    
    # Initialize Gemini
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        api_key=settings.gemini_api_key,
        temperature=0
    )
    
    # Create prompt template
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a data analyst assistant. Follow instructions carefully. Always use meaningful column aliases (e.g., 'SUM(amount) as total_sales' instead of 'sum(amount)')."),
        ("user", "{input}")
    ])
    
    # Invoke the model
    chain = prompt_template | llm
    try:
        logger.info("Calling Gemini API...")
        response = chain.invoke({"input": prompt})
        response_text = response.content
        logger.info("Gemini API response received successfully")
        logger.debug(f"Raw Gemini response:\n{response_text}")
    except Exception as e:
        logger.error(f"Gemini API call failed: {str(e)}", exc_info=True)
        raise Exception(f"Gemini API call failed: {str(e)}")
    
    # Try to parse as JSON first (predefined functions or error)
    try:
        logger.info("Attempting to parse as JSON...")
        plan = json.loads(response_text)
        logger.info(f"Successfully parsed as JSON. Plan: {plan}")
        
        # Check if it's an error response
        if "error" in plan:
            logger.warning(f"Gemini returned error: {plan['error']}")
            return {"type": "error", "message": plan["error"]}
        
        # It's a predefined function plan
        plan["type"] = "function"
        return plan
    except json.JSONDecodeError:
        # Not JSON, treat as SQL
        logger.info("Not JSON format, treating as SQL query")
        sql_query = response_text.strip()
        
        # Remove markdown code blocks if present
        if sql_query.startswith("```"):
            sql_query = sql_query.split("```")[1]
            if sql_query.startswith("sql"):
                sql_query = sql_query[3:]
        sql_query = sql_query.strip()
        
        # Remove any trailing newlines or special characters that might corrupt LIMIT value
        sql_query = " ".join(sql_query.split()) 
        
        logger.debug(f"SQL query: {sql_query}")
        return {"type": "sql", "query": sql_query}


def generate_narrative_from_results(question: str, result_df, result_summary: str) -> str:
    """
    Send the question + actual query results to Gemini and let it decide what to say.
    Falls back to generic message if Gemini fails.
    """
    try:
        logger.info("Sending results to Gemini for narrative generation...")
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            api_key=settings.gemini_api_key,
            temperature=0
        )
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful data analyst. Analyze the query results and provide a brief, human-friendly summary."),
            ("user", "{input}")
        ])
        
        chain = prompt_template | llm
        
        # Send question + actual data to Gemini
        narrative_prompt = f"""User Question: {question}

Query Results (first 10 rows):
{result_summary}

Based on these results, provide a 1-2 sentence human-friendly summary. 
Focus on what's interesting or important in the data.
Be specific with values and insights."""
        
        response = chain.invoke({"input": narrative_prompt})
        narrative = response.content.strip()
        logger.info(f"Gemini generated narrative: {narrative}")
        return narrative
        
    except Exception as e:
        logger.error(f"Gemini narrative generation failed: {str(e)}")
        
        # Generic fallback - no hardcoding of logic
        row_count = len(result_df)
        if row_count == 0:
            return "No results found"
        elif row_count == 1:
            return "Query returned 1 result"
        else:
            return f"Query returned {row_count} results"
