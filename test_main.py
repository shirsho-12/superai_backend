import pytest
from fastapi.testclient import TestClient
from main import app
from pydantic import BaseModel
from typing import List

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to CompliAgent Horizon API"}

def test_list_documents():
    response = client.get("/api/documents")
    assert response.status_code == 200
    documents = response.json()
    assert isinstance(documents, list)
    if len(documents) > 0:
        assert "id" in documents[0]
        assert "title" in documents[0]
        assert "type" in documents[0]

def test_get_document():
    # Test with a valid document ID
    response = client.get("/api/documents/reg_001")
    assert response.status_code == 200
    document = response.json()
    assert document["id"] == "reg_001"
    assert "content" in document

def test_analyze_gaps():
    test_data = {
        "regulation_id": "reg_001",
        "policy_id": "policy_001"
    }
    response = client.post("/api/analyze", json=test_data)
    assert response.status_code == 200
    result = response.json()
    assert "gaps" in result
    assert "summary" in result
    assert isinstance(result["gaps"], list)
    if len(result["gaps"]) > 0:
        gap = result["gaps"][0]
        assert "gap_id" in gap
        assert "title" in gap
        assert "description" in gap
        assert "severity" in gap

def test_invalid_document():
    # Test with non-existent document ID
    response = client.get("/api/documents/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"
