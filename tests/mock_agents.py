from typing import Dict, Any
import json

class MockGapAnalyzer:
    def __init__(self):
        self.mock_gap_analysis = {
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

    async def analyze_gaps(self, regulation_id: str, policy_id: str, policy_content: str) -> Dict[str, Any]:
        return self.mock_gap_analysis

class MockAmendmentGenerator:
    def __init__(self):
        self.mock_amendments = {
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

    async def generate_amendments(self, gap_analysis: Dict[str, Any]) -> Dict[str, Any]:
        return self.mock_amendments

def apply_mock_agents():
    """
    Apply mock agents to the main application.
    Call this in your test setup.
    """
    import sys
    import importlib
    from unittest.mock import patch
    
    # Mock the agent imports in the main module
    with patch.dict('sys.modules', {
        'agents.gap_analyzer': MockGapAnalyzer(),
        'agents.amendment_generator': MockAmendmentGenerator()
    }):
        # Reload the main module to apply the mocks
        if 'main' in sys.modules:
            importlib.reload(sys.modules['main'])
