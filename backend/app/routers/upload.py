from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
import logging
from app.services.file_service import parse_file, validate_file_size
from app.session.store import save_session
from app.utils.schema_extractor import extract_schema
from app.models.response_models import UploadResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload and parse a CSV or Excel file."""
    logger.info(f"Upload started for file: {file.filename}")
    
    try:
        # Validate file type
        if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            logger.warning(f"Invalid file type: {file.filename}")
            raise HTTPException(status_code=400, detail="Only .csv and .xlsx files are supported")
        
        # Read file content
        file_content = await file.read()
        logger.info(f"File content read successfully. Size: {len(file_content)} bytes")
        
        # Validate file size
        validate_file_size(len(file_content))
        
        # Parse file
        try:
            df, filename = parse_file(file_content, file.filename)
            logger.info(f"File parsed successfully. Rows: {len(df)}, Columns: {len(df.columns)}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error parsing file: {str(e)}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        logger.info(f"Session created: {session_id}")
        
        # Extract schema
        schema_preview = extract_schema(df, filename)
        logger.info(f"Schema extracted for session {session_id}")
        
        # Save to session store
        save_session(session_id, df, filename, {"schema": schema_preview})
        logger.info(f"Session saved successfully: {session_id}")
        
        return UploadResponse(
            session_id=session_id,
            schema_preview=schema_preview
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload_file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
