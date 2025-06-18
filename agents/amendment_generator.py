from typing import Dict, Any, List
import boto3
import os
import json

class AmendmentGenerator:
    def __init__(self):
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-west-2')
        )
        self.knowledge_base_id = os.getenv('POLICIES_KB_ID')
        self.agent_id = os.getenv('AMENDMENT_AGENT_ID')
        self.model_id = os.getenv('AMENDMENT_MODEL', 'anthropic.claude-3-sonnet-20240229-v1:0')

    async def generate_amendments(self, gap_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate policy amendments based on gap analysis
        """
        prompt = f"""
        You are a policy amendment specialist. Based on the following gap analysis, 
        suggest specific amendments to the policy to address the compliance gaps.
        
        Gap Analysis:
        {json.dumps(gap_analysis, indent=2)}
        
        For each gap, provide:
        1. A clear description of the required changes
        2. The exact text to be added/modified
        3. The rationale for the change
        4. Impact assessment
        
        Format the response as a JSON object.
        """
        
        try:
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "prompt": prompt,
                    "max_tokens_to_sample": 1500,
                    "temperature": 0.3,
                })
            )
            
            response_body = json.loads(response['body'].read())
            return json.loads(response_body['completion'])
            
        except Exception as e:
            raise Exception(f"Error generating amendments: {str(e)}")
