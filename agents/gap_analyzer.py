from typing import List, Dict, Any
import boto3
import os
import json

class GapAnalyzer:
    def __init__(self):
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-west-2')
        )
        self.knowledge_base_id = os.getenv('REGULATIONS_KB_ID')
        self.agent_id = os.getenv('GAP_ANALYSIS_AGENT_ID')
        self.model_id = os.getenv('GAP_ANALYSIS_MODEL', 'anthropic.claude-3-sonnet-20240229-v1:0')

    async def analyze_gaps(self, regulation_id: str, policy_id: str, policy_content: str) -> Dict[str, Any]:
        """
        Analyze gaps between a regulation and a policy document
        """
        prompt = f"""
        You are a compliance analyst. Analyze the following policy document against the regulation.
        
        Regulation ID: {regulation_id}
        Policy ID: {policy_id}
        
        Policy Content:
        {policy_content}
        
        Identify any compliance gaps and provide:
        1. Gap ID (generate a unique identifier)
        2. Title of the gap
        3. Description of the gap
        4. Relevant regulation text
        5. Current policy text
        6. Severity level (high/medium/low)
        
        Format the response as a JSON object.
        """
        
        try:
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "prompt": prompt,
                    "max_tokens_to_sample": 1000,
                    "temperature": 0.5,
                })
            )
            
            response_body = json.loads(response['body'].read())
            return json.loads(response_body['completion'])
            
        except Exception as e:
            raise Exception(f"Error analyzing gaps: {str(e)}")
