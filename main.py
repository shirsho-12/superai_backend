from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import boto3
import os
import uuid
from dotenv import load_dotenv
import json

# Import agents
from agents.gap_analyzer import GapAnalyzer
from agents.amendment_generator import AmendmentGenerator

# Load environment variables
load_dotenv()

app = FastAPI(
    title="CompliAgent Horizon API",
    description="API for regulatory compliance gap analysis and policy management",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Security
API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key

# Initialize AWS clients
s3_client = boto3.client(
    's3',
    region_name=os.getenv('AWS_REGION', 'us-west-2'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

# Initialize agents
gap_analyzer = GapAnalyzer()
amendment_generator = AmendmentGenerator()

# Pydantic Models
class Document(BaseModel):
    id: str
    title: str
    content: Optional[str] = None
    type: str  # 'regulation' or 'policy'
    metadata: Optional[Dict[str, Any]] = {}

class GapItem(BaseModel):
    gap_id: str
    title: str
    description: str
    regulation_text: str
    policy_text: str
    severity: str
    confidence: Optional[float] = None

class AmendmentItem(BaseModel):
    id: str
    gap_id: str
    policy_section: str
    original_text: str
    proposed_text: str
    change_type: str
    rationale: str
    impact: Optional[str] = None

class AnalysisRequest(BaseModel):
    regulation_id: str
    policy_id: str
    policy_content: Optional[str] = None
    policy_file: Optional[UploadFile] = None

class AnalysisResponse(BaseModel):
    analysis_id: str
    gaps: List[GapItem]
    summary: str
    status: str

class AmendmentResponse(BaseModel):
    amendment_id: str
    analysis_id: str
    amendments: List[AmendmentItem]
    summary: str
    status: str

# Helper Functions
async def get_document_from_s3(bucket: str, document_id: str) -> str:
    try:
        response = s3_client.get_object(Bucket=bucket, Key=document_id)
        return response['Body'].read().decode('utf-8')
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Document {document_id} not found in {bucket}: {str(e)}"
        )

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to CompliAgent Horizon API"}

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_gaps(
    request: AnalysisRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Analyze gaps between a regulation and a policy
    """
    try:
        # Get policy content from either direct input or file
        policy_content = request.policy_content
        if request.policy_file:
            policy_content = (await request.policy_file.read()).decode('utf-8')
        
        if not policy_content:
            # Try to fetch policy from S3 if no content provided
            policy_content = await get_document_from_s3(
                os.getenv('POLICIES_BUCKET'), 
                f"{request.policy_id}.txt"
            )
        
        # Fetch regulation content from S3
        regulation_content = await get_document_from_s3(
            os.getenv('REGULATIONS_BUCKET'),
            f"{request.regulation_id}.txt"
        )
        
        # Analyze gaps using the GapAnalyzer agent
        gap_analysis = await gap_analyzer.analyze_gaps(
            request.regulation_id,
            request.policy_id,
            policy_content
        )
        
        # Generate a unique analysis ID
        analysis_id = str(uuid.uuid4())
        
        return {
            "analysis_id": analysis_id,
            "gaps": gap_analysis.get("gaps", []),
            "summary": gap_analysis.get("summary", ""),
            "status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing document: {str(e)}"
        )

@app.post("/api/amendments/generate", response_model=AmendmentResponse)
async def generate_amendments(
    gap_analysis: AnalysisResponse,
    api_key: str = Depends(verify_api_key)
):
    """
    Generate policy amendments based on gap analysis
    """
    try:
        # Generate amendments using the AmendmentGenerator agent
        amendments = await amendment_generator.generate_amendments(gap_analysis.dict())
        
        return {
            "amendment_id": str(uuid.uuid4()),
            "analysis_id": gap_analysis.analysis_id,
            "amendments": amendments.get("amendments", []),
            "summary": amendments.get("summary", ""),
            "status": "completed"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating amendments: {str(e)}"
        )

@app.get("/api/documents", response_model=List[Document])
async def list_documents(
    document_type: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """
    List all available documents (regulations or policies)
    """
    try:
        bucket = (
            os.getenv('REGULATIONS_BUCKET') 
            if document_type == 'regulation' 
            else os.getenv('POLICIES_BUCKET')
        )
        
        response = s3_client.list_objects_v2(Bucket=bucket)
        documents = []
        
        for obj in response.get('Contents', []):
            doc_id = obj['Key']
            if doc_id.endswith('.txt'):  # Only process text files
                doc_id = doc_id[:-4]  # Remove .txt extension
                documents.append({
                    "id": doc_id,
                    "title": doc_id.replace('_', ' ').title(),
                    "type": "regulation" if "regulation" in bucket.lower() else "policy"
                })
        
        return documents
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing documents: {str(e)}"
        )

@app.get("/api/documents/{document_type}/{document_id}", response_model=Document)
async def get_document(
    document_type: str,
    document_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Get document content by ID and type
    """
    try:
        if document_type not in ["regulation", "policy"]:
            raise HTTPException(
                status_code=400,
                detail="Document type must be either 'regulation' or 'policy'"
            )
        
        bucket = (
            os.getenv('REGULATIONS_BUCKET') 
            if document_type == 'regulation' 
            else os.getenv('POLICIES_BUCKET')
        )
        
        content = await get_document_from_s3(bucket, f"{document_id}.txt")
        
        return {
            "id": document_id,
            "title": document_id.replace('_', ' ').title(),
            "content": content,
            "type": document_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving document: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
