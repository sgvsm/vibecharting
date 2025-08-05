import json
import os
import logging
from datetime import datetime, timezone
from query_parser import QueryParser
from database import DatabaseClient
from utils.secrets import get_secret

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    """
    Main Lambda handler for query processing
    Handles natural language queries and returns trend analysis results
    """
    start_time = datetime.now(timezone.utc)
    logger.info(f"Query processing started at {start_time}")
    
    try:
        # Parse the request
        if 'body' not in event:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({
                    'success': False,
                    'error': {
                        'code': 'MISSING_BODY',
                        'message': 'Request body is required'
                    }
                })
            }
        
        # Parse JSON body
        try:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({
                    'success': False,
                    'error': {
                        'code': 'INVALID_JSON',
                        'message': 'Invalid JSON in request body'
                    }
                })
            }
        
        # Extract query text
        query_text = body.get('query', '').strip()
        if not query_text:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({
                    'success': False,
                    'error': {
                        'code': 'EMPTY_QUERY',
                        'message': 'Query text is required'
                    }
                })
            }
        
        # Extract optional filters
        filters = body.get('filters', {})
        timeframe = filters.get('timeframe', '24h')
        min_confidence = filters.get('min_confidence', 0.7)
        limit = min(filters.get('limit', 10), 50)  # Cap at 50 results
        
        logger.info(f"Processing query: '{query_text}' with filters: {filters}")
        
        # Get database credentials
        db_secret = get_secret(os.environ['DB_SECRET_NAME'])
        
        # Initialize components
        query_parser = QueryParser()
        db_client = DatabaseClient(db_secret)
        
        # Parse query intent
        intent = query_parser.parse_intent(query_text)
        logger.info(f"Detected intent: {intent}")
        
        if not intent:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({
                    'success': False,
                    'error': {
                        'code': 'UNSUPPORTED_INTENT',
                        'message': 'Could not understand the query intent'
                    }
                })
            }
        
        # Get results from database
        results = db_client.get_results_for_intent(
            intent, 
            timeframe=timeframe,
            min_confidence=min_confidence,
            limit=limit
        )
        
        # Log query for analytics
        execution_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        db_client.log_query(query_text, intent, len(results), int(execution_time))
        
        # Format response
        response_data = {
            'success': True,
            'data': {
                'intent': intent,
                'query_interpretation': query_parser.get_interpretation(intent),
                'results': results,
                'total_matches': len(results),
                'filters_applied': {
                    'timeframe': timeframe,
                    'min_confidence': min_confidence,
                    'limit': limit
                }
            },
            'meta': {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'execution_time_ms': int(execution_time),
                'version': '1.0.0'
            },
            'error': None
        }
        
        logger.info(f"Query processed successfully: {len(results)} results in {execution_time:.0f}ms")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        execution_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'success': False,
                'data': None,
                'meta': {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'execution_time_ms': int(execution_time),
                    'version': '1.0.0'
                },
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': 'An error occurred while processing your query',
                    'details': error_msg
                }
            })
        }
    
    finally:
        # Clean up database connection
        try:
            if 'db_client' in locals():
                db_client.close()
        except:
            pass 