from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import json
from pathlib import Path
import uuid
from datetime import datetime

app = FastAPI(title="Mock CompliAgent Horizon API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data storage
MOCK_DATA_DIR = Path("mock_data")
MOCK_DATA_DIR.mkdir(exist_ok=True)

# Mock database
mock_db = {
    "documents": {
        "regulations": {
            "gdpr": {
                "id": "gdpr",
                "title": "GDPR Compliance Requirements",
                "content": """
                General Data Protection Regulation (GDPR)
                
                Article 5: Principles relating to processing of personal data
                1. Personal data shall be:
                   a) processed lawfully, fairly and in a transparent manner
                   b) collected for specified, explicit and legitimate purposes
                   c) adequate, relevant and limited to what is necessary
                   d) accurate and kept up to date
                   e) stored for no longer than is necessary
                   f) processed securely
                
                Article 17: Right to erasure ('right to be forgotten')
                The data subject shall have the right to obtain erasure of personal data.
                """,
                "type": "regulation",
                "metadata": {"version": "1.0", "jurisdiction": "EU"}
            }
        },
        "policies": {
            "data_protection": {
                "id": "data_protection",
                "title": "Company Data Protection Policy",
                "content": """
                COMPANY DATA PROTECTION POLICY
                
                Section 1: Data Collection
                - We collect personal data necessary for business operations
                - Data is stored in secure servers
                
                Section 2: Data Usage
                - Data is used to provide and improve our services
                - We may share data with trusted third-party providers
                
                Section 3: Data Retention
                - Data is retained as long as necessary for business purposes
                - Users can request data deletion by contacting support
                """,
                "type": "policy",
                "metadata": {"version": "1.2", "department": "Compliance"}
            }
        }
    },
    "analyses": {},
    "amendments": {}
}

# Save mock data to file
def save_mock_data():
    with open(MOCK_DATA_DIR / "mock_db.json", "w") as f:
        json.dump(mock_db, f, indent=2)

# Load mock data from file
def load_mock_data():
    try:
        with open(MOCK_DATA_DIR / "mock_db.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

# Load existing data if available
if existing_data := load_mock_data():
    mock_db.update(existing_data)

# Pydantic models
class Document(BaseModel):
    id: str
    title: str
    content: Optional[str] = None
    type: str
    metadata: Dict[str, Any] = {}

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

# Mock API Key
MOCK_API_KEY = "test-api-key-123"

def verify_api_key(request: Request):
    if request.headers.get("X-API-Key") != MOCK_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to Mock CompliAgent Horizon API"}

@app.get("/api/documents", response_model=List[Document])
async def list_documents(document_type: Optional[str] = None):
    """List all available documents"""
    verify_api_key(Request)
    
    documents = []
    
    if document_type == "regulation" or document_type is None:
        for doc in mock_db["documents"]["regulations"].values():
            doc_copy = doc.copy()
            doc_copy.pop("content", None)  # Don't include content in list view
            documents.append(doc_copy)
    
    if document_type == "policy" or document_type is None:
        for doc in mock_db["documents"]["policies"].values():
            doc_copy = doc.copy()
            doc_copy.pop("content", None)  # Don't include content in list view
            documents.append(doc_copy)
    
    return documents

@app.get("/api/documents/{document_type}/{document_id}", response_model=Document)
async def get_document(document_type: str, document_id: str):
    """Get document content by ID and type"""
    verify_api_key(Request)
    
    if document_type not in ["regulation", "policy"]:
        raise HTTPException(
            status_code=400,
            detail="Document type must be either 'regulation' or 'policy'"
        )
    
    doc = mock_db["documents"][f"{document_type}s"].get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return doc

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_gaps(request: AnalysisRequest):
    """Mock gap analysis endpoint"""
    verify_api_key(Request)
    
    # Generate a mock analysis
    analysis_id = str(uuid.uuid4())
    
    mock_gap_analysis = {
        "analysis_id": analysis_id,
        "gaps": [
            {
                "gap_id": "gap_001",
                "title": "Data Retention Policy Missing",
                "description": "The policy does not specify data retention periods as required by the regulation.",
                "regulation_text": "Personal data must be retained for a minimum of 5 years.",
                "policy_text": "Data retention periods are determined by business needs.",
                "severity": "high",
                "confidence": 0.92
            },
            {
                "gap_id": "gap_002",
                "title": "Data Subject Rights Not Addressed",
                "description": "The policy does not clearly state how data subjects can exercise their rights.",
                "regulation_text": "Data subjects have the right to access, rectify, and erase their data.",
                "policy_text": "Contact support for any data-related inquiries.",
                "severity": "medium",
                "confidence": 0.85
            }
        ],
        "summary": "Found 2 compliance gaps that need to be addressed.",
        "status": "completed"
    }
    
    # Store the analysis
    mock_db["analyses"][analysis_id] = {
        **mock_gap_analysis,
        "regulation_id": request.regulation_id,
        "policy_id": request.policy_id,
        "created_at": datetime.utcnow().isoformat()
    }
    save_mock_data()
    
    return mock_gap_analysis

@app.post("/api/amendments/generate", response_model=AmendmentResponse)
async def generate_amendments(analysis: AnalysisResponse):
    """Mock amendment generation endpoint"""
    verify_api_key(Request)
    
    amendment_id = str(uuid.uuid4())
    
    mock_amendments = {
        "amendment_id": amendment_id,
        "analysis_id": analysis.analysis_id,
        "amendments": [
            {
                "id": "amend_001",
                "gap_id": gap["gap_id"],
                "policy_section": "Data Retention",
                "original_text": gap["policy_text"],
                "proposed_text": "Personal data will be retained for a period of 5 years from the date of collection, after which it will be securely deleted.",
                "change_type": "modification",
                "rationale": f"This change ensures compliance with the retention period requirement specified in the regulation: {gap['regulation_text']}",
                "impact": "High - Ensures compliance with data retention regulations."
            }
            for gap in analysis.gaps
        ],
        "summary": f"Generated {len(analysis.gaps)} amendments to address compliance gaps.",
        "status": "completed"
    }
    
    # Store the amendments
    mock_db["amendments"][amendment_id] = {
        **mock_amendments,
        "created_at": datetime.utcnow().isoformat()
    }
    save_mock_data()
    
    return mock_amendments

if __name__ == "__main__":
    print("Starting Mock CompliAgent Horizon API server...")
    print(f"Mock API Key: {MOCK_API_KEY}")
    print("API Documentation: http://localhost:8000/docs")
    uvicorn.run("mock_server:app", host="0.0.0.0", port=8000, reload=True)
