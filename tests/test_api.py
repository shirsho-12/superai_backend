import pytest
from fastapi import status
from unittest.mock import ANY
import json

# Test data
TEST_REGULATION_ID = "test_reg_001"
TEST_POLICY_ID = "test_policy_001"
TEST_ANALYSIS_ID = "test_analysis_001"
TEST_AMENDMENT_ID = "test_amend_001"

SAMPLE_REGULATION = """
Data Protection Regulation
1. Personal data must be encrypted at rest and in transit.
2. Data retention period must not exceed 5 years.
3. Users must be able to request data deletion.
"""

SAMPLE_POLICY = """
Company Data Policy
1. We store user data securely.
2. We retain data as needed for business purposes.
3. Contact support for data deletion requests.
"""

MOCK_GAP_ANALYSIS = {
    "gaps": [
        {
            "gap_id": "gap_001",
            "title": "Data Encryption Not Specified",
            "description": "The policy does not explicitly mention encryption of personal data.",
            "regulation_text": "Personal data must be encrypted at rest and in transit.",
            "policy_text": "We store user data securely.",
            "severity": "high"
        },
        {
            "gap_id": "gap_002",
            "title": "Vague Data Retention Policy",
            "description": "The policy does not specify a clear retention period.",
            "regulation_text": "Data retention period must not exceed 5 years.",
            "policy_text": "We retain data as needed for business purposes.",
            "severity": "medium"
        }
    ],
    "summary": "Found 2 compliance gaps that need to be addressed."
}

MOCK_AMENDMENTS = {
    "amendments": [
        {
            "id": "amend_001",
            "gap_id": "gap_001",
            "policy_section": "Data Storage",
            "original_text": "We store user data securely.",
            "proposed_text": "We store user data securely using industry-standard encryption both at rest (AES-256) and in transit (TLS 1.3+).",
            "change_type": "modification",
            "rationale": "Explicitly states the use of encryption to meet regulatory requirements.",
            "impact": "High - Ensures compliance with data protection regulations."
        },
        {
            "id": "amend_002",
            "gap_id": "gap_002",
            "policy_section": "Data Retention",
            "original_text": "We retain data as needed for business purposes.",
            "proposed_text": "We retain personal data for a maximum of 5 years from the date of collection, after which it will be securely deleted or anonymized.",
            "change_type": "modification",
            "rationale": "Sets a clear retention period in line with regulatory requirements.",
            "impact": "Medium - Provides clarity and ensures compliance with data retention rules."
        }
    ],
    "summary": "Generated 2 amendments to address the compliance gaps."
}

class TestAPI:
    def test_root_endpoint(self, test_client):
        response = test_client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Welcome to CompliAgent Horizon API"}

    def test_analyze_endpoint_unauthorized(self, test_client):
        response = test_client.post(
            "/api/analyze",
            json={"regulation_id": TEST_REGULATION_ID, "policy_id": TEST_POLICY_ID}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_analyze_endpoint(self, test_client, mock_s3_client, mock_env_vars):
        # Mock S3 get_object responses
        mock_s3 = mock_s3_client.return_value
        mock_s3.get_object.side_effect = [
            {"Body": Mock(read=Mock(return_value=SAMPLE_REGULATION.encode('utf-8')))},
            {"Body": Mock(read=Mock(return_value=SAMPLE_POLICY.encode('utf-8')))}
        ]
        
        # Mock Bedrock response
        with patch('agents.gap_analyzer.GapAnalyzer.analyze_gaps') as mock_analyze:
            mock_analyze.return_value = MOCK_GAP_ANALYSIS
            
            response = test_client.post(
                "/api/analyze",
                headers={"X-API-Key": mock_env_vars["API_KEY"]},
                json={
                    "regulation_id": TEST_REGULATION_ID,
                    "policy_id": TEST_POLICY_ID,
                    "policy_content": SAMPLE_POLICY
                }
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "analysis_id" in data
            assert len(data["gaps"]) == 2
            assert data["status"] == "completed"

    def test_generate_amendments(self, test_client, mock_env_vars):
        analysis_response = {
            "analysis_id": TEST_ANALYSIS_ID,
            "gaps": MOCK_GAP_ANALYSIS["gaps"],
            "summary": MOCK_GAP_ANALYSIS["summary"],
            "status": "completed"
        }
        
        with patch('agents.amendment_generator.AmendmentGenerator.generate_amendments') as mock_amend:
            mock_amend.return_value = MOCK_AMENDMENTS
            
            response = test_client.post(
                "/api/amendments/generate",
                headers={"X-API-Key": mock_env_vars["API_KEY"]},
                json=analysis_response
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["analysis_id"] == TEST_ANALYSIS_ID
            assert len(data["amendments"]) == 2
            assert data["status"] == "completed"

    def test_list_documents(self, test_client, mock_s3_client, mock_env_vars):
        # Mock S3 list_objects_v2 response
        mock_s3 = mock_s3_client.return_value
        mock_s3.list_objects_v2.return_value = {
            "Contents": [
                {"Key": "reg1.txt"},
                {"Key": "reg2.txt"}
            ]
        }
        
        response = test_client.get(
            "/api/documents?document_type=regulation",
            headers={"X-API-Key": mock_env_vars["API_KEY"]}
        )
        
        assert response.status_code == status.HTTP_200_OK
        documents = response.json()
        assert len(documents) == 2
        assert documents[0]["type"] == "regulation"

    def test_get_document(self, test_client, mock_s3_client, mock_env_vars):
        # Mock S3 get_object response
        mock_s3 = mock_s3_client.return_value
        mock_s3.get_object.return_value = {
            "Body": Mock(read=Mock(return_value=SAMPLE_REGULATION.encode('utf-8')))
        }
        
        response = test_client.get(
            f"/api/documents/regulation/{TEST_REGULATION_ID}",
            headers={"X-API-Key": mock_env_vars["API_KEY"]}
        )
        
        assert response.status_code == status.HTTP_200_OK
        document = response.json()
        assert document["id"] == TEST_REGULATION_ID
        assert "content" in document
