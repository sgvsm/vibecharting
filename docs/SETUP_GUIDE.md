# Crypto Trend Analysis Chatbot - Complete Setup Guide

## 🚀 Quick Start

This guide provides a complete setup process for the Crypto Trend Analysis Chatbot. Follow these steps in order to deploy the entire system.

## 📋 Prerequisites

- AWS Account with appropriate permissions
- PostgreSQL client (for database setup)
- Git repository access
- Basic knowledge of AWS services

## 🏗️ Phase 1: AWS Infrastructure Setup

### Step 1.1: Create RDS PostgreSQL Instance

1. **Open AWS RDS Console**
   - Go to AWS Console → RDS → Databases
   - Click **"Create database"**

2. **Database Configuration**
   ```
   Engine: PostgreSQL
   Version: 15.4 (latest)
   Template: Free tier
   DB instance identifier: vibe-charting-db
   Master username: vibecharting
   Master password: [generate secure password]
   ```

3. **Instance Configuration**
   ```
   DB instance class: db.t3.micro
   Storage: 20 GB (gp3)
   Storage autoscaling: Disabled
   ```

4. **Connectivity**
   ```
   VPC: Create new VPC
   Public access: Yes
   VPC security group: Create new
   Availability Zone: No preference
   Database port: 5432
   ```

5. **Additional Configuration**
   ```
   Database name: vibe_charting
   Backup retention: 7 days
   Monitoring: Disabled
   ```

### Step 1.2: Configure Security Groups

1. **RDS Security Group**
   - Go to EC2 → Security Groups
   - Find the RDS security group
   - Add inbound rule:
     ```
     Type: PostgreSQL
     Protocol: TCP
     Port: 5432
     Source: 0.0.0.0/0 (temporary for setup)
     ```

2. **Lambda Security Group** (will be created automatically)

### Step 1.3: Store Database Credentials

1. **Create AWS Secret**
   - Go to AWS Console → Secrets Manager
   - Click **"Store a new secret"**
   - Choose **"Other type of secret"**
   - Add key-value pairs:
     ```
     host: [your-rds-endpoint]
     database: vibe_charting
     username: vibecharting
     password: [your-password]
     port: 5432
     ```
   - Secret name: `vibe-charting/database`

## 🗄️ Phase 2: Database Setup

### Step 2.1: Connect to Database

```bash
# Connect using psql
psql -h [your-rds-endpoint] -U vibecharting -d vibe_charting

# Or set password environment variable
export PGPASSWORD='your-password'
psql -h [your-rds-endpoint] -U vibecharting -d vibe_charting
```

### Step 2.2: Run Database Migrations

```sql
-- Run migrations in order
\i database/migrations/001_create_cryptocurrencies.sql
\i database/migrations/002_create_price_data.sql
\i database/migrations/003_create_trend_analysis.sql
\i database/migrations/004_create_signal_events.sql
\i database/migrations/005_create_analysis_runs.sql
\i database/migrations/006_create_query_logs.sql
\i database/migrations/007_create_cleanup_jobs.sql
\i database/migrations/008_create_indexes.sql
\i database/migrations/009_add_coingecko_support.sql
\i database/migrations/010_allow_null_cmc_id.sql
```

### Step 2.3: Seed Initial Data

```sql
-- Insert cryptocurrency data
\i database/seeds/updated_cryptocurrencies_seed.sql
```

### Step 2.4: Verify Database Setup

```sql
-- Check tables
\dt

-- Check cryptocurrencies
SELECT COUNT(*) FROM cryptocurrencies WHERE is_active = true;

-- Check indexes
\di
```

## 🔧 Phase 3: Lambda Functions Setup

### Step 3.1: Create Lambda Functions

1. **Data Ingestion Function**
   - Go to AWS Console → Lambda
   - Click **"Create function"**
   - Function name: `vibe-charting-data-ingestion`
   - Runtime: Python 3.11
   - Architecture: x86_64

2. **Trend Analysis Function**
   - Create function: `vibe-charting-trend-analysis`
   - Runtime: Python 3.11
   - Architecture: x86_64

3. **Query Processor Function**
   - Create function: `vibe-charting-query-processor`
   - Runtime: Python 3.11
   - Architecture: x86_64

### Step 3.2: Configure Environment Variables

**For Data Ingestion Function:**
```
DB_SECRET_NAME = vibe-charting/database
COINGECKO_API_SECRET_NAME = vibe-charting/coingecko-api-key
```

**For Trend Analysis Function:**
```
DB_SECRET_NAME = vibe-charting/database
```

**For Query Processor Function:**
```
DB_SECRET_NAME = vibe-charting/database
```

### Step 3.3: Upload Lambda Code

1. **Package Lambda Functions**
   ```bash
   # Data Ingestion
   cd lambda_functions/data_ingestion
   zip -r data_ingestion.zip . -x "*.pyc" "__pycache__/*"
   
   # Trend Analysis
   cd ../trend_analysis
   zip -r trend_analysis.zip . -x "*.pyc" "__pycache__/*"
   
   # Query Processor
   cd ../query_processor
   zip -r query_processor.zip . -x "*.pyc" "__pycache__/*"
   ```

2. **Upload to Lambda**
   - In each function's **"Code"** tab
   - Click **"Upload from"** → **".zip file"**
   - Upload the respective zip file

### Step 3.4: Configure IAM Permissions

Each Lambda function needs these permissions:

**Data Ingestion:**
- Secrets Manager read access
- RDS access
- CloudWatch logs

**Trend Analysis:**
- Secrets Manager read access
- RDS access
- CloudWatch logs

**Query Processor:**
- Secrets Manager read access
- RDS access
- CloudWatch logs

## ⏰ Phase 4: EventBridge Scheduling

### Step 4.1: Create EventBridge Rules

1. **Data Ingestion Schedule**
   - Go to AWS Console → EventBridge → Rules
   - Create rule: `vibe-charting-data-ingestion-schedule`
   - Schedule: `cron(0 6 * * ? *)` (daily at 6 AM UTC)
   - Target: `vibe-charting-data-ingestion` Lambda function

2. **Trend Analysis Schedule**
   - Create rule: `vibe-charting-trend-analysis-schedule`
   - Schedule: `cron(30 6 * * ? *)` (daily at 6:30 AM UTC)
   - Target: `vibe-charting-trend-analysis` Lambda function

## 🌐 Phase 5: API Gateway Setup

### Step 5.1: Create API Gateway

1. **Create REST API**
   - Go to AWS Console → API Gateway
   - Click **"Create API"**
   - Choose **"REST API"**
   - API name: `vibe-charting-api`

2. **Create Resource and Method**
   - Create resource: `/query`
   - Create method: `POST`
   - Integration type: Lambda Function
   - Lambda function: `vibe-charting-query-processor`

### Step 5.2: Configure CORS

1. **Enable CORS**
   - Select the `/query` resource
   - Click **"Actions"** → **"Enable CORS"**
   - Configure:
     ```
     Access-Control-Allow-Origin: *
     Access-Control-Allow-Headers: Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token
     Access-Control-Allow-Methods: POST,OPTIONS
     ```

### Step 5.3: Deploy API

1. **Create Stage**
   - Click **"Actions"** → **"Deploy API"**
   - Stage name: `prod`
   - Note: `Production deployment`

## 🎨 Phase 6: Frontend Setup (Optional)

### Step 6.1: AWS Amplify Setup

1. **Create Amplify App**
   - Go to AWS Console → Amplify
   - Click **"New app"** → **"Host web app"**
   - Connect to your Git repository

2. **Configure Build Settings**
   - Framework: React
   - Build commands: `npm run build`
   - Output directory: `build`

### Step 6.2: Environment Variables

Add these environment variables to Amplify:
```
REACT_APP_API_URL = [your-api-gateway-url]
REACT_APP_API_KEY = [optional-api-key]
```

## ✅ Phase 7: Verification

### Step 7.1: Test Data Ingestion

1. **Manual Trigger**
   - Go to Lambda console
   - Select `vibe-charting-data-ingestion`
   - Click **"Test"** with empty event `{}`

2. **Check Results**
   - View CloudWatch logs
   - Verify data in database:
     ```sql
     SELECT COUNT(*) FROM price_data WHERE timestamp > NOW() - INTERVAL '1 hour';
     ```

### Step 7.2: Test Trend Analysis

1. **Manual Trigger**
   - Select `vibe-charting-trend-analysis`
   - Click **"Test"** with empty event `{}`

2. **Check Results**
   ```sql
   SELECT COUNT(*) FROM trend_analysis WHERE created_at > NOW() - INTERVAL '1 hour';
   ```

### Step 7.3: Test API

1. **Test Query Endpoint**
   ```bash
   curl -X POST [your-api-gateway-url]/query \
     -H "Content-Type: application/json" \
     -d '{"query": "What coins are going up today?"}'
   ```

## 📊 Phase 8: Monitoring Setup

### Step 8.1: CloudWatch Alarms

1. **Error Alarms**
   - Create alarms for Lambda function errors
   - Set threshold: 1 error in 5 minutes

2. **Performance Alarms**
   - Create alarms for Lambda duration
   - Set threshold: > 30 seconds

### Step 8.2: Dashboard

1. **Create CloudWatch Dashboard**
   - Add widgets for Lambda metrics
   - Add widgets for API Gateway metrics
   - Add widgets for RDS metrics

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify RDS endpoint and credentials
   - Check security group settings
   - Ensure Lambda has VPC access

2. **Lambda Function Errors**
   - Check CloudWatch logs
   - Verify environment variables
   - Check IAM permissions

3. **API Gateway Errors**
   - Verify Lambda integration
   - Check CORS settings
   - Test with Postman or curl

### Useful Commands

```bash
# Check Lambda logs
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/vibe-charting

# Test database connection
psql -h [endpoint] -U vibecharting -d vibe_charting -c "SELECT version();"

# Check API Gateway
aws apigateway get-rest-apis
```

## 📈 Next Steps

After successful setup:

1. **Monitor System Performance**
   - Check CloudWatch metrics daily
   - Verify data quality
   - Monitor costs

2. **Enhance Security**
   - Add API key authentication
   - Restrict CORS origins
   - Enable CloudTrail logging

3. **Scale as Needed**
   - Upgrade RDS instance if needed
   - Add more Lambda memory if required
   - Implement caching strategies

## 📞 Support

For additional help:
- Check the detailed documentation in the `/docs` directory
- Review CloudWatch logs for specific errors
- Consult AWS documentation for service-specific issues 