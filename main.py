from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Vertex AI
aiplatform.init(project=os.getenv('GOOGLE_CLOUD_PROJECT'))

# Define request/response models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

# Endpoint configuration
ENDPOINT_ID = os.getenv('VERTEX_AI_ENDPOINT_ID')
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT')
LOCATION = os.getenv('VERTEX_AI_LOCATION', 'us-central1')

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Get the endpoint
        endpoint = aiplatform.Endpoint(
            endpoint_name=f"projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/{ENDPOINT_ID}"
        )

        # Format the chat messages
        instance = {
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in request.messages
            ]
        }

        # Make the prediction
        response = endpoint.predict([instance])
        
        return {"response": response.predictions[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)