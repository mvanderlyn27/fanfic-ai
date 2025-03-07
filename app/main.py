from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
import json
from pathlib import Path
from .models.story import StoryInput, StoryContext, Chapter, Scene
from .story_service import StoryService
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI()
story_service = StoryService()

class StoryResponse(BaseModel):
    story_file_path: str

@app.post("/generate-story/", response_model=StoryResponse)
async def generate_story(story_input: StoryInput):
    try:
        # Validate input model
        if not story_input:
            raise ValueError("Story input cannot be empty")
            
        # Generate story using StoryService
        story_file_path = await story_service.generate_story(story_input)
        
        return StoryResponse(story_file_path=story_file_path)
    
    except ValidationError as e:
        logger.error(f"Validation error in story input: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        logger.error(f"Value error in story generation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in story generation: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during story generation")