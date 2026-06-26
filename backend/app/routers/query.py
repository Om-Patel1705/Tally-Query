from fastapi import APIRouter, HTTPException
import logging
import json
from app.models.request_models import QueryRequest
from app.models.response_models import AnswerResponse
from app.session.store import get_session, add_query_to_history, get_query_history
from app.services.gemini_service import get_gemini_response
from app.services.sql_executor import execute_sql
from app.services.analytics_service import execute_plan
from app.utils.schema_extractor import extract_schema
from app.utils.response_parser import parse_sql_response
import pandas as pd

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=AnswerResponse)
async def submit_query(request: QueryRequest):
    """Submit a natural language query and get analysis results."""
    logger.info(f"Query received for session: {request.session_id}")
    logger.info(f"Question: {request.question}")
    
    try:
        # Get session
        session = get_session(request.session_id)
        if not session:
            logger.warning(f"Session not found: {request.session_id}")
            raise HTTPException(status_code=404, detail="Session not found. Please upload a file first.")
        
        logger.info(f"Session retrieved successfully")
        df = session["df"]
        
        # Validate question
        if not request.question or not request.question.strip():
            logger.warning("Empty question submitted")
            raise HTTPException(status_code=422, detail="Question cannot be empty")
        
        # Get query history for context
        query_history = get_query_history(request.session_id)
        logger.info(f"Retrieved {len(query_history)} previous queries from history")
        
        # Get response from Gemini with query history context
        logger.info("Calling Gemini API...")
        gemini_response = get_gemini_response(request.question, df, query_history)
        logger.info(f"Gemini response type: {gemini_response.get('type')}")
        logger.debug(f"Gemini response: {gemini_response}")
        
        # Handle error response
        if gemini_response.get("type") == "error":
            error_msg = gemini_response.get("message", "Unable to process this query")
            logger.warning(f"Gemini returned error: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        result_df = pd.DataFrame()
        narrative = ""
        chart_data = None
        executed_query = None
        
        # Handle SQL response
        if gemini_response.get("type") == "sql":
            try:
                logger.info("Executing SQL query...")
                executed_query = gemini_response["query"]
                # Parse SQL to extract include_chart flag
                clean_query, include_chart = parse_sql_response(executed_query)
                logger.info(f"Include chart flag: {include_chart}")
                result_df, narrative, chart_data = execute_sql(df, clean_query, include_chart)
                logger.info(f"SQL executed successfully. Rows: {len(result_df)}")
            except Exception as sql_error:
                logger.error(f"SQL execution failed: {str(sql_error)}")
                logger.info("Attempting to use predefined functions as fallback...")
                
                # Fallback: ask Gemini to use predefined functions
                try:
                    fallback_response = get_gemini_response(
                        f"{request.question}\n\nNote: Complex SQL is not supported. Please use simple operations like groupby_agg, filter, sort, count, trend, or summary.",
                        df,
                        query_history
                    )
                    
                    if fallback_response.get("type") == "error":
                        raise HTTPException(status_code=400, detail=fallback_response.get("message"))
                    
                    logger.info("Fallback: Using predefined functions...")
                    result_df, narrative, chart_data = execute_plan(df, fallback_response)
                    executed_query = str(fallback_response)  # Store fallback response as query reference
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed: {str(fallback_error)}")
                    raise HTTPException(status_code=400, detail=f"Query execution failed: {str(fallback_error)}")
        
        # Handle function response
        elif gemini_response.get("type") == "function":
            try:
                logger.info("Executing predefined function plan...")
                result_df, narrative, chart_data = execute_plan(df, gemini_response)
                logger.info(f"Function executed successfully. Rows: {len(result_df)}")
                executed_query = str(gemini_response)  # Store function plan as query reference
            except Exception as e:
                logger.error(f"Function execution failed: {str(e)}", exc_info=True)
                raise HTTPException(status_code=400, detail=f"Query execution failed: {str(e)}")
        
        # Store executed query in history for context in future requests
        if executed_query:
            add_query_to_history(request.session_id, executed_query)
            logger.info(f"Query added to history")
        
        # Build result summary to send to Gemini for narrative generation
        result_summary = result_df.head(10).to_markdown(index=False)  # Show first 10 rows for context
        logger.debug(f"Result summary:\n{result_summary}")
        
        # Generate human-friendly narrative from results
        from app.services.gemini_service import generate_narrative_from_results
        answer_text = generate_narrative_from_results(request.question, result_df, result_summary)
        
        # Add row count info
        if not result_df.empty:
            if len(result_df) <= 30:
                answer_text += f"\n\n({len(result_df)} rows)"
            else:
                answer_text += f"\n\n(showing top 30 of {len(result_df)} rows)"
        
        # Prepare response - show up to 30 rows for better visibility
        response = AnswerResponse(
            answer=answer_text,
            chart_data=chart_data,
            query_type=gemini_response.get("query_type", "unknown"),
            rows_analysed=len(df),
            data=result_df.head(30).to_dict(orient='records')  # Changed from 5 to 30
        )
        
        logger.info(f"Query processed successfully for session: {request.session_id}")
        logger.debug(f"Response to send: {response.model_dump_json()}")
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in submit_query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
