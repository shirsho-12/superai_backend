import os
import uuid
from typing import Optional, Union, BinaryIO, List
from fastapi import UploadFile, HTTPException, status
import boto3
# load environment variables
from dotenv import load_dotenv
load_dotenv()

class S3Service:
    """Service class for handling S3 operations."""

    def __init__(self):
        """Initialize the S3 client with environment variables."""
        self.s3_client = boto3.client(
            's3',
            region_name=os.getenv('AWS_REGION', 'us-west-2'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.regulations_bucket = os.getenv('REGULATIONS_BUCKET')
        self.policies_bucket = os.getenv('POLICIES_BUCKET')
        print(f"Regulations Bucket Endpoint: {self.s3_client.meta.endpoint_url}/{self.regulations_bucket}")
        print(f"Policies Bucket Endpoint: {self.s3_client.meta.endpoint_url}/{self.policies_bucket}")
        


    def _get_bucket(self, option: str) -> str:
        """Get the target bucket name based on the option."""
        if option == 'regulation':
            return self.regulations_bucket
        else:
            return self.policies_bucket

    async def upload_file(
        self,
        file: UploadFile,
        option: str,
        file_name: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> str:
        """Upload a file to the specified S3 bucket."""
        target_bucket = self._get_bucket(option)
        
        if not file_name:
            file_ext = os.path.splitext(file.filename)[1]
            file_name = f"{str(uuid.uuid4())}{file_ext}"
        
        try:
            self.s3_client.upload_fileobj(
                file.file,
                target_bucket,
                file_name,
                ExtraArgs={
                    'ContentType': content_type or file.content_type or 'application/octet-stream'
                }
            )
            return f"https://{target_bucket}.s3.us-west-2.amazonaws.com/{file_name}"
        except boto3.exceptions.S3UploadFailedError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def get_file(
        self,
        file_key: str,
        option: str,
        as_bytes: bool = False
    ) -> Union[bytes, str]:
        """Get a file from the specified S3 bucket."""
        target_bucket = self._get_bucket(option)
        
        try:
            response = self.s3_client.get_object(
                Bucket=target_bucket,
                Key=file_key
            )
            file_content = response['Body'].read()
            return file_content if as_bytes else file_content.decode('utf-8')
        except boto3.exceptions.S3UploadFailedError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
    
    async def list_documents(
        self,
        option: str
    ):
        """List all documents in the specified S3 bucket."""
        target_bucket = self._get_bucket(option)
        
        try:
            response = self.s3_client.list_objects_v2(Bucket=target_bucket)
            contents = response.get('Contents')
            if contents is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error listing documents: object list can't be used in 'await' expression"
                )
            return contents
        except boto3.exceptions.S3UploadFailedError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def delete_file(self, file_key: str, option: str) -> bool:
        pass

# Create a singleton instance of the S3Service
s3_service = S3Service()
