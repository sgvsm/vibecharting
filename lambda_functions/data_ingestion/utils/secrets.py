import boto3
import json
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

def get_secret(secret_name: str) -> dict:
    """
    Retrieve secret from AWS Secrets Manager
    
    Args:
        secret_name: Name of the secret in AWS Secrets Manager
        
    Returns:
        Dictionary containing the secret values
        
    Raises:
        Exception: If secret cannot be retrieved
    """
    try:
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=session.region_name or 'us-east-2'
        )
        
        logger.info(f"Retrieving secret: {secret_name}")
        
        # Retrieve the secret value
        response = client.get_secret_value(SecretId=secret_name)
        
        # Parse the secret string
        secret_string = response.get('SecretString')
        if not secret_string:
            raise Exception(f"No secret string found for {secret_name}")
        
        # Parse JSON
        secret_dict = json.loads(secret_string)
        
        logger.info(f"Successfully retrieved secret: {secret_name}")
        return secret_dict
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == 'DecryptionFailureException':
            logger.error(f"Failed to decrypt secret {secret_name}: {error_message}")
            raise Exception(f"Failed to decrypt secret: {error_message}")
        elif error_code == 'InternalServiceErrorException':
            logger.error(f"Internal service error for secret {secret_name}: {error_message}")
            raise Exception(f"Internal service error: {error_message}")
        elif error_code == 'InvalidParameterException':
            logger.error(f"Invalid parameter for secret {secret_name}: {error_message}")
            raise Exception(f"Invalid parameter: {error_message}")
        elif error_code == 'InvalidRequestException':
            logger.error(f"Invalid request for secret {secret_name}: {error_message}")
            raise Exception(f"Invalid request: {error_message}")
        elif error_code == 'ResourceNotFoundException':
            logger.error(f"Secret not found: {secret_name}")
            raise Exception(f"Secret not found: {secret_name}")
        else:
            logger.error(f"Unknown error retrieving secret {secret_name}: {error_message}")
            raise Exception(f"Unknown error: {error_message}")
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse secret JSON for {secret_name}: {str(e)}")
        raise Exception(f"Failed to parse secret JSON: {str(e)}")
        
    except Exception as e:
        logger.error(f"Unexpected error retrieving secret {secret_name}: {str(e)}")
        raise Exception(f"Failed to retrieve secret: {str(e)}")

def get_secret_value(secret_name: str, key: str, default=None):
    """
    Get a specific value from a secret
    
    Args:
        secret_name: Name of the secret in AWS Secrets Manager
        key: Key to retrieve from the secret
        default: Default value if key not found
        
    Returns:
        The value for the specified key or default
    """
    try:
        secret_dict = get_secret(secret_name)
        return secret_dict.get(key, default)
    except Exception as e:
        logger.error(f"Error getting secret value {key} from {secret_name}: {str(e)}")
        if default is not None:
            return default
        raise 