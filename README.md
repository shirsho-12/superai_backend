# CompliAgent Horizon Backend API

A FastAPI-based backend service for regulatory compliance gap analysis and policy management, integrated with AWS services including Amazon Bedrock, S3, and OpenSearch.

## Features

- Document management for regulations and policies
- AI-powered gap analysis between regulations and policies
- Integration with AWS Bedrock for AI/ML capabilities
- Secure file storage using AWS S3
- FastAPI-based RESTful API with OpenAPI documentation

## Prerequisites

- Python 3.9+
- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- Python virtual environment (recommended)

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd superai-hackathon-backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the example environment file and update with your AWS credentials:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your AWS credentials and configuration.

5. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

6. Access the API documentation at:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### 1. Document Management

#### List Documents
- **GET** `/api/documents`
  - Query Parameters:
    - `document_type` (optional): Filter by document type ('regulation' or 'policy')
  - Returns: List of document metadata

#### Get Document Content
- **GET** `/api/documents/{document_id}`
  - Path Parameters:
    - `document_id`: ID of the document to retrieve
  - Returns: Document content and metadata

### 2. Gap Analysis

#### Analyze Gaps
- **POST** `/api/analyze`
  - Request Body:
    - `regulation_id`: ID of the regulation document
    - `policy_id`: ID of the policy document to analyze
  - Returns: Gap analysis results with identified compliance gaps

## AWS Setup

### 1. S3 Buckets
- Create two S3 buckets:
  - One for storing regulation documents
  - One for storing policy documents
- Ensure proper IAM permissions are set for Bedrock and your application

### 2. Amazon Bedrock Knowledge Bases
1. Go to AWS Console > Amazon Bedrock > Knowledge bases
2. Create knowledge bases:
   - `regulations-kb` for regulation documents
   - `policies-kb` for policy documents
3. Configure data sources to point to respective S3 buckets
4. Set up OpenSearch Serverless collection for vector storage

### 3. IAM Roles
Create an IAM role with permissions for:
- AmazonS3FullAccess (or more restricted as needed)
- AmazonBedrockFullAccess (or more restricted)
- AmazonOpenSearchServiceFullAccess (or more restricted)

## Environment Variables

Copy `.env.example` to `.env` and update with your configuration:

```
# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1

# S3 Buckets
REGULATIONS_BUCKET=your-regulations-bucket-name
POLICIES_BUCKET=your-policies-bucket-name

# Bedrock
BEDROCK_KNOWLEDGE_BASE_ID=your-knowledge-base-id
BEDROCK_AGENT_ID=your-agent-id
```

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
isort .
```

## Deployment

### Docker
Build and run with Docker:
```bash
docker build -t compliagent-backend .
docker run -p 8000:8000 --env-file .env compliagent-backend
```

### AWS ECS/EC2
- Package the application in a Docker container
- Deploy to ECS or EC2 with proper IAM roles
- Set up a load balancer if needed
- Configure environment variables securely using AWS Systems Manager Parameter Store or AWS Secrets Manager

## License

MIT
                       }
                     }
                   }
                 }
               }
             }
           }
         }
       }
     }
     


5. Create Lambda function for the action:
   • Name: gap-analysis-function
   • Runtime: Python 3.11
   • Code: Implement the gap analysis logic
   • Connect to the action group

6. Configure agent instructions:

luke, [18-Jun-25 5:53 PM]
You are a compliance gap analysis expert. Your job is to:
   1. Compare regulatory documents with internal policies
   2. Identify specific gaps where policies don't meet regulatory requirements
   3. Highlight the exact text in both documents that demonstrates the gap
   4. Classify gaps by severity (critical, high, medium, low)
   5. Provide clear descriptions of each gap

   When analyzing gaps:
   - Focus on substantive requirements, not just wording differences
   - Consider both explicit requirements and implicit obligations
   - Identify missing controls, inadequate procedures, and inconsistent standards
   - Highlight specific sections that need attention
   


7. Test and deploy the agent

### Step 4: Create Amendment Drafting Agent

1. Go to AWS Console > Amazon Bedrock > Agents
2. Create new agent:
   • Name: amendment-drafting-agent
   • Description: "Drafts policy amendments to address compliance gaps"
   • Foundation model: Claude 3 Sonnet
   • IAM role: Create new with appropriate permissions

3. Add knowledge base:
   • Select both regulations-kb and policies-kb
   • Configure retrieval settings (top k = 5)

4. Create action groups:
   • Name: draft-amendments
   • Description: "Drafts policy amendments to address identified gaps"
   • API schema:
    
json
     {
       "openapi": "3.0.0",
       "info": {
         "title": "Amendment Drafting API",
         "version": "1.0.0"
       },
       "paths": {
         "/draft": {
           "post": {
             "summary": "Draft policy amendments",
             "requestBody": {
               "required": true,
               "content": {
                 "application/json": {
                   "schema": {
                     "type": "object",
                     "required": ["gaps", "policy_id"],
                     "properties": {
                       "gaps": {
                         "type": "array",
                         "items": {
                           "type": "object",
                           "properties": {
                             "gap_id": {"type": "string"},
                             "description": {"type": "string"},
                             "regulation_text": {"type": "string"},
                             "policy_text": {"type": "string"}
                           }
                         }
                       },
                       "policy_id": {
                         "type": "string",
                         "description": "ID of the policy document to amend"
                       }
                     }
                   }
                 }
               }
             },
             "responses": {
               "200": {
                 "description": "Successful drafting",
                 "content": {
                   "application/json": {
                     "schema": {
                       "type": "object",
                       "properties": {
                         "amendments": {
                           "type": "array",
                           "items": {
                             "type": "object",
                             "properties": {
                               "amendment_id": {"type": "string"},
                               "gap_id": {"type": "string"},
                               "original_text": {"type": "string"},
                               "proposed_text": {"type": "string"},
                               "rationale": {"type": "string"}
                             }
                           }
                         }
                       }
                     }
                   }
                 }
               }
             }
           }
         }
       }
     }
     


5. Create Lambda function for the action:
   • Name: amendment-drafting-function
   • Runtime: Python 3.11
   • Code: Implement the amendment drafting logic
   • Connect to the action group

6. Configure agent instructions:

luke, [18-Jun-25 5:53 PM]
You are a policy amendment drafting expert. Your job is to:
   1. Review identified compliance gaps between regulations and policies
   2. Draft specific text amendments to address each gap
   3. Ensure amendments are clear, concise, and legally sound
   4. Maintain the style and format of the original policy document
   5. Provide rationale for each amendment

   When drafting amendments:
   - Use precise regulatory language
   - Highlight exactly what text should be replaced or added
   - Ensure amendments fully address the identified gap
   - Consider practical implementation concerns
   - Maintain consistency with other policy sections
   


7. Test and deploy the agent

### Step 5: Create Simple Frontend for Agent Interaction

1. Create an S3 bucket for the frontend:
   • Name: compliance-frontend
   • Enable static website hosting

2. Upload a simple HTML interface that allows:
   • Uploading/selecting regulatory documents
   • Uploading/selecting policy documents
   • Triggering gap analysis
   • Viewing identified gaps
   • Requesting amendment drafts
   • Viewing and saving proposed amendments

3. Use AWS Amplify or API Gateway to create endpoints for:
   • Document upload/selection
   • Gap analysis agent invocation
   • Amendment drafting agent invocation

### Step 6: Integration and Testing

1. Test the complete workflow:
   • Upload sample regulations and policies
   • Run gap analysis
   • Review identified gaps
   • Request amendment drafts
   • Review proposed amendments

2. Refine agent prompts and knowledge base settings based on results

3. Implement any necessary adjustments to improve accuracy

## Implementation Considerations

1. Cost Management:
   • Bedrock agents and knowledge bases incur costs based on usage
   • OpenSearch Serverless collections have ongoing costs
   • Consider implementing cost monitoring

2. Performance Optimization:
   • Fine-tune chunking settings for optimal retrieval
   • Adjust top-k parameters based on testing
   • Consider document preprocessing for better results

3. User Experience:
   • Implement progress indicators for long-running operations
   • Add document preview capabilities
   • Include feedback mechanisms to improve agent responses

4. Limitations:
   • Knowledge bases have document size limits
   • Agent responses have token limits
   • Complex documents may require preprocessing

This implementation plan provides a straightforward approach to creating specialized Bedrock agents for 
your compliance comparison system, leveraging the RAG capabilities of knowledge bases for improved accuracy
and relevance.
