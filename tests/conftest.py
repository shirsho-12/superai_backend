import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app
import os

@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing"""
    env_vars = {
        "AWS_ACCESS_KEY_ID": "test_key",
        "AWS_SECRET_ACCESS_KEY": "test_secret",
        "AWS_REGION": "us-west-2",
        "REGULATIONS_BUCKET": "test-regulations-bucket",
        "POLICIES_BUCKET": "test-policies-bucket",
        "REGULATIONS_KB_ID": "test-reg-kb",
        "POLICIES_KB_ID": "test-policy-kb",
        "GAP_ANALYSIS_AGENT_ID": "test-gap-agent",
        "AMENDMENT_AGENT_ID": "test-amend-agent",
        "API_KEY": "test-api-key"
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars

@pytest.fixture
def mock_s3_client():
    with patch('boto3.client') as mock_client:
        yield mock_client

@pytest.fixture
def mock_bedrock_runtime():
    with patch('boto3.client') as mock_client:
        yield mock_client
