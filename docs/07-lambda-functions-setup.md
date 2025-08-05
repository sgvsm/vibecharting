# Lambda Functions Setup Guide

## Overview

This guide details how to prepare, package, and manually upload the three Lambda functions for the Vibe Charting Trend Analysis Chatbot:
1. Data Ingestion Function
2. Trend Analysis Function
3. Query Processor Function

## Prerequisites

- Python 3.9 installed locally
- Access to AWS Management Console
- Your database credentials for `vibe-charting-db`
- CoinMarketCap API key

## Common Dependencies

All functions will need a `requirements.txt` file with these base dependencies:

```txt
psycopg2-binary==2.9.9
requests==2.31.0
python-dotenv==1.0.0
boto3==1.34.11
```

## 1. Data Ingestion Function

### Directory Structure
```
data_ingestion/
├── handler.py
├── cmc_client.py
├── database.py
├── requirements.txt
└── utils/
    ├── __init__.py
    └── secrets.py
```

### Code Files

**handler.py**:
```python
import json
import os
from cmc_client import CoinMarketCapClient
from database import DatabaseClient
from utils.secrets import get_secret

def lambda_handler(event, context):
    try:
        # Get secrets
        db_secret = get_secret(os.environ['DB_SECRET_NAME'])
        api_secret = get_secret(os.environ['CMC_API_SECRET_NAME'])
        
        # Initialize clients
        cmc_client = CoinMarketCapClient(api_secret['CMC_API_KEY'])
        db_client = DatabaseClient(db_secret)
        
        # Fetch and store data
        crypto_data = cmc_client.get_latest_quotes()
        db_client.store_price_data(crypto_data)
        
        return {
            'statusCode': 200,
            'body': json.dumps('Data ingestion successful')
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error during data ingestion: {str(e)}')
        }
```

**cmc_client.py**:
```python
import requests

class CoinMarketCapClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://pro-api.coinmarketcap.com/v1'
        
    def get_latest_quotes(self):
        headers = {
            'X-CMC_PRO_API_KEY': self.api_key,
            'Accept': 'application/json'
        }
        
        # Get active cryptocurrencies from database
        # Make API call for their latest quotes
        # Transform data for database storage
        # Return formatted data
```

**database.py**:
```python
import psycopg2
from psycopg2.extras import execute_values

class DatabaseClient:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(
            host=db_config['host'],
            database=db_config['database'],
            user=db_config['username'],
            password=db_config['password']
        )
        
    def store_price_data(self, data):
        with self.conn.cursor() as cur:
            # Insert price data
            # Update last_updated timestamps
            self.conn.commit()
```

**utils/secrets.py**:
```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])
```

## 2. Trend Analysis Function

### Directory Structure
```
trend_analysis/
├── handler.py
├── analyzers/
│   ├── __init__.py
│   ├── trend_analyzer.py
│   ├── volatility_analyzer.py
│   └── signal_detector.py
├── database.py
├── requirements.txt
└── utils/
    ├── __init__.py
    └── secrets.py
```

Add to `requirements.txt`:
```txt
numpy==1.26.2
pandas==2.1.4
scipy==1.11.4
```

**handler.py**:
```python
import json
import os
from analyzers.trend_analyzer import TrendAnalyzer
from analyzers.signal_detector import SignalDetector
from database import DatabaseClient
from utils.secrets import get_secret

def lambda_handler(event, context):
    try:
        # Get database credentials
        db_secret = get_secret(os.environ['DB_SECRET_NAME'])
        
        # Initialize components
        db_client = DatabaseClient(db_secret)
        trend_analyzer = TrendAnalyzer()
        signal_detector = SignalDetector()
        
        # Get price data and analyze
        price_data = db_client.get_recent_price_data()
        trend_results = trend_analyzer.analyze(price_data)
        signal_results = signal_detector.detect_signals(price_data)
        
        # Store results
        db_client.store_analysis_results(trend_results, signal_results)
        
        return {
            'statusCode': 200,
            'body': json.dumps('Analysis completed successfully')
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error during analysis: {str(e)}')
        }
```

## 3. Query Processor Function

### Directory Structure
```
query_processor/
├── handler.py
├── query_parser.py
├── database.py
├── requirements.txt
└── utils/
    ├── __init__.py
    └── secrets.py
```

**handler.py**:
```python
import json
import os
from query_parser import QueryParser
from database import DatabaseClient
from utils.secrets import get_secret

def lambda_handler(event, context):
    try:
        # Parse request
        body = json.loads(event['body'])
        query_text = body['query']
        
        # Get database credentials
        db_secret = get_secret(os.environ['DB_SECRET_NAME'])
        
        # Process query
        parser = QueryParser()
        intent = parser.parse_intent(query_text)
        
        # Get results from database
        db_client = DatabaseClient(db_secret)
        results = db_client.get_results_for_intent(intent)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'intent': intent,
                'results': results
            })
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }
```

## Packaging Instructions

1. **Create Function Directory**:
   ```bash
   mkdir lambda_package
   cd lambda_package
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt -t .
   ```

3. **Copy Function Code**:
   ```bash
   cp -r ../your_function_dir/* .
   ```

4. **Create ZIP Package**:
   ```bash
   zip -r ../function.zip .
   ```

## Manual Upload Steps

1. **Open AWS Lambda Console**
2. **Select your function**
3. **Click "Upload from" → ".zip file"**
4. **Upload your ZIP file**
5. **Set handler**: `handler.lambda_handler`
6. **Save and test**

## Environment Variables

Set these for each function:

**Data Ingestion:**
```
DB_SECRET_NAME=vibe-charting/database
CMC_API_SECRET_NAME=vibe-charting/cmc-api-key
```

**Trend Analysis:**
```
DB_SECRET_NAME=vibe-charting/database
```

**Query Processor:**
```
DB_SECRET_NAME=vibe-charting/database
```

## Testing

### Test Events

**Data Ingestion:**
```json
{
  "test-event": "data-ingestion"
}
```

**Trend Analysis:**
```json
{
  "test-event": "trend-analysis"
}
```

**Query Processor:**
```json
{
  "body": "{\"query\": \"what coins are going up?\"}"
}
```

### Monitoring

1. After uploading, click "Test" button
2. Check CloudWatch logs for execution details
3. Verify database entries
4. Test API Gateway integration

## Troubleshooting

Common issues and solutions:

1. **Database Connection**:
   - Verify VPC/subnet configuration
   - Check security group rules
   - Validate database credentials

2. **Dependencies**:
   - Ensure all packages are in ZIP file
   - Check Python version compatibility
   - Verify package versions

3. **Permissions**:
   - Verify IAM role permissions
   - Check Secrets Manager access
   - Validate VPC access

4. **Memory/Timeout**:
   - Monitor function metrics
   - Adjust memory if needed
   - Check timeout settings

## Best Practices

1. **Code Organization**:
   - Keep functions modular
   - Use clear naming conventions
   - Include error handling

2. **Security**:
   - Never hardcode credentials
   - Use environment variables
   - Implement proper error handling

3. **Performance**:
   - Optimize database queries
   - Reuse database connections
   - Implement caching where appropriate

4. **Monitoring**:
   - Add detailed logging
   - Monitor execution times
   - Track error rates 