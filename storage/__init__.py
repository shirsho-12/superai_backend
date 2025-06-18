"""Storage module for handling file operations with cloud storage providers."""

from .s3_service import s3_service, S3Service

__all__ = ['s3_service', 'S3Service']
