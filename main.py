from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from fastapi.responses import Response
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any, Union
import os
from dotenv import load_dotenv
import json

# Import agents
from agents.amendment_generator import AmendmentGenerator
import aiohttp

from storage.s3_service import s3_service

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


# File operation models
class FileUploadResponse(BaseModel):
    file_url: str
    file_key: str
    bucket: str
    content_type: str

class FileContentResponse(BaseModel):
    content: Union[str, bytes]
    content_type: str
    file_name: str

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

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to CompliAgent Horizon API"}

@app.post("/api/analyze", response_model=Dict)
async def analyze_gaps():
    """
    Analyze gaps between a regulation and a policy
    """
    try:
        async with aiohttp.ClientSession() as client:
            response = await client.get(
                "https://u4bqsvoj2balkjevdnuxmv4kvi0czgzo.lambda-url.us-west-2.on.aws/"
            )
            return await response.json()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing document: {str(e)}"
        )

@app.post("/api/amendments/generate", response_model=AmendmentResponse)
async def generate_amendments(
    gap_analysis: AnalysisResponse
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

@app.get("/api/documents", response_model=List)
async def list_documents(
    document_type: Optional[str] = None
):
    """
    List all available documents (regulations or policies)
    """
    try:
        contents = await s3_service.list_documents(document_type)
        return [{'Key': obj['Key'], 'LastModified': obj['LastModified']} for obj in contents]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing documents: {str(e)}"
        )


@app.get("/api/documents", response_model=List[Document])
async def list_documents(
    document_type: Optional[str] = None
):
    """
    List all available documents (regulations or policies)
    """
    try:
        documents = await s3_service.list_documents(
            document_type=document_type
        )
        return documents
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing documents: {str(e)}"
        )


@app.get("/api/documents/{document_type}/{document_id}", response_model=Document)
async def get_document(
    document_type: str,
    document_id: str
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
        
        content = await s3_service.get_file(
            file_key=f"{document_id}.txt",
            option=document_type
        )
        
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

@app.post("/api/documents/{document_type}/{document_id}", response_model=Document)
async def upload_document(
    document_type: str,
    document_id: str,
    file: UploadFile = File(...)
):
    """
    Upload a document content by ID and type
    """
    try:
        if document_type not in ["regulation", "policy"]:
            raise HTTPException(
                status_code=400,
                detail="Document type must be either 'regulation' or 'policy'"
            )
        
        await s3_service.upload_file(
            file=file,
            option=document_type,
            file_name=f"{document_id}.txt"
        )
        
        return {
            "id": document_id,
            "title": document_id.replace('_', ' ').title(),
            "type": document_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading document: {str(e)}"
        )



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
