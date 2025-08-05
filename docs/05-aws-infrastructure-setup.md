# AWS Infrastructure Setup Guide (Manual Configuration)

## Overview

This guide provides step-by-step instructions for manually setting up the AWS infrastructure required for the Vibe Charting Trend Analysis Chatbot MVP using the AWS Management Console. The infrastructure includes RDS PostgreSQL, Lambda functions, API Gateway, EventBridge, and monitoring components.

## Prerequisites

- AWS Account with administrative access
- CoinMarketCap API key
- PostgreSQL client for local database access

## Infrastructure Components

### 1. VPC and Networking Setup

1. **Create VPC:**
   - Navigate to VPC Dashboard
   - Click "Create VPC"
   - Enter name: `vibe-charting-vpc`
   - IPv4 CIDR: `10.0.0.0/16`
   - Click "Create"

2. **Create Subnets:**
   - In VPC Dashboard, select "Subnets" → "Create subnet"
   - Create the following subnets in your VPC:
     ```
     Name: vibe-charting-private-1a
     AZ: us-east-1a
     CIDR: 10.0.1.0/24

     Name: vibe-charting-private-1b
     AZ: us-east-1b
     CIDR: 10.0.2.0/24
     ```

3. **Internet Gateway:**
   - Select "Internet Gateways" → "Create internet gateway"
   - Name: `vibe-charting-igw`
   - Attach to your VPC

### 2. Security Groups

1. **Create Lambda Security Group:**
   - Go to EC2 Dashboard → Security Groups
   - Click "Create security group"
   - Name: `vibe-charting-lambda-sg`
   - Description: "Security group for Lambda functions"
   - VPC: Select your vibe-charting-vpc
   - Outbound rules: Allow HTTPS (443) to 0.0.0.0/0

2. **Create RDS Security Group:**
   - Click "Create security group"
   - Name: `vibe-charting-rds-sg`
   - Description: "Security group for RDS PostgreSQL"
   - VPC: Select your vibe-charting-vpc
   - Inbound rules: Allow PostgreSQL (5432) from Lambda security group

### 3. Database Configuration

1. **Create DB Subnet Group:**
   - Go to RDS Dashboard → Subnet groups
   - Click "Create DB subnet group"
   - Settings:
     ```
     Name: vibe-charting-subnet-group
     Description: Subnet group for vibe-charting database
     VPC: vibe-charting-vpc
     ```
   - Add subnets:
     - Select both private subnets created earlier:
       - vibe-charting-private-1a
       - vibe-charting-private-1b
   - Click "Create"

2. **Create Database Instance:**
   - Go to RDS Dashboard → Databases
   - Click "Create database"
   - Choose options:
     ```
     Method: Standard create
     Engine: PostgreSQL
     Version: 14.7 (or latest available)
     Template: Free tier
     ```
       - Settings:
      ```
      DB instance identifier: vibe-charting-db
      Master username: vibecharting
      Master password: [See secrets/credentials.md]
      DB instance class: db.t3.micro
      ```
   - Storage:
     ```
     Storage type: GP2 (General Purpose SSD)
     Allocated storage: 20 GB
     Enable storage autoscaling: Yes
     Maximum storage threshold: 100 GB
     ```
   - Connectivity:
     ```
     VPC: vibe-charting-vpc
     DB Subnet group: vibe-charting-subnet-group
     Public access: No
     VPC security group: Choose existing
     Existing security groups: vibe-charting-rds-sg
     Availability Zone: No preference
     ```
   - Database authentication:
     ```
     Password authentication
     ```
   - Additional configuration:
     ```
     Initial database name: vibe_charting
     Backup retention: 7 days
     Monitoring: Enable Enhanced monitoring
     Log exports: PostgreSQL logs
     Maintenance: Enable auto minor version upgrade
     Deletion protection: Enable
     ```

3. **Verify Connectivity:**
    - Wait for database to be available (10-15 minutes)
    - Note down the database endpoint

    There are two ways to verify connectivity:

    **Option 1: Using AWS Cloud9 (Recommended)**
    - Go to Cloud9 Console
    - Create new environment:
      ```
      Name: vibe-charting-db-test
      Instance type: t3.micro
      Platform: Amazon Linux 2
      VPC: vibe-charting-vpc
      Subnet: vibe-charting-private-1a
      ```
    - Once environment is ready:
      ```bash
      # Install PostgreSQL client
      sudo yum install postgresql15

      # Test connection
      psql -h [DB_ENDPOINT] -U vibecharting -d vibe_charting
      ```
    - Delete the Cloud9 environment after testing

    **Option 2: Using Systems Manager Session Manager**
    - Create a temporary EC2 instance:
      ```
      AMI: Amazon Linux 2
      Instance type: t3.micro
      VPC: vibe-charting-vpc
      Subnet: vibe-charting-private-1a
      Security group: vibe-charting-lambda-sg
      IAM role: AWSSystemsManagerRole
      ```
    - Connect using Session Manager from AWS Console
    - Install PostgreSQL client and test:
      ```bash
      sudo yum install postgresql15
      psql -h [DB_ENDPOINT] -U vibecharting -d vibe_charting
      ```
    - Terminate the EC2 instance after testing

    Note: Both options require the security group to allow outbound traffic to port 5432

### 4. Secrets Manager Configuration

1. **Store Database Credentials:**
   - Go to AWS Secrets Manager
   - Click "Store a new secret"
   
   **Step 1: Choose secret type**
   - Select secret type: "Other type of secret"
   - Add key/value pairs (one per line):
     ```
     Key         Value
     host        [vibe-charting-db endpoint]
     database    vibe_charting
     username    vibecharting
     password    [from secrets/credentials.md]
     port        5432
     ```
     Note: Enter each key without colons, just the plain key name
   - Click "Next"

   **Step 2: Configure secret**
   - Secret name: `vibe-charting/database`
   - Description: "Database credentials for vibe-charting-db"
   - Resource permissions: Skip (use default)
   - Click "Next"

   **Step 3: Configure rotation**
   - Select "Disable automatic rotation"
   - Click "Next"

   **Step 4: Review**
   - Review all settings
   - Click "Store"

2. **Store CoinMarketCap API Key:**
   - Click "Store a new secret"
   
   **Step 1: Choose secret type**
   - Select secret type: "Other type of secret"
   - Add key/value pair:
     ```
     Key           Value
     CMC_API_KEY   [Your API key]
     ```
     Note: Enter the key without colon
   - Click "Next"

   **Step 2: Configure secret**
   - Secret name: `vibe-charting/cmc-api-key`
   - Description: "CoinMarketCap API key"
   - Resource permissions: Skip (use default)
   - Click "Next"

   **Step 3: Configure rotation**
   - Select "Disable automatic rotation"
   - Click "Next"

   **Step 4: Review**
   - Review all settings
   - Click "Store"

### 5. Lambda Functions Setup

1. **Create IAM Role:**
   - Go to IAM Dashboard
   - Select "Roles" → "Create role"
   - Use case: Lambda
   - Click "Next"
   - Add permissions:
     - Search and attach these AWS managed policies:
       - AWSLambdaVPCAccessExecutionRole
       - AWSLambdaBasicExecutionRole
   - Click "Next"
   - Name: `vibe-charting-lambda-role`
   - Create role
   
   After role creation, add Secrets Manager access:
   - Go to the created role
   - Click "Add permissions" → "Create inline policy"
   - JSON tab, paste:
     ```json
     {
       "Version": "2012-10-17",
       "Statement": [
         {
           "Effect": "Allow",
           "Action": "secretsmanager:GetSecretValue",
           "Resource": "arn:aws:secretsmanager:*:*:secret:vibe-charting/*"
         }
       ]
     }
     ```
   - Name the policy: `vibe-charting-secrets-access`
   - Click "Create policy"

2. **Create Lambda Functions:**

   For each function (data-ingestion, trend-analysis, query-processor):
   - Go to Lambda Dashboard
   - Click "Create function"
   - Settings:
     ```
     Author from scratch
     Name: vibe-charting-[function-name]
     Runtime: Python 3.9
     Architecture: x86_64
     ```
   - Change default execution role:
     - Select "Use an existing role"
     - Choose `vibe-charting-lambda-role`
   
   - Configure VPC:
     ```
     VPC: vibe-charting-vpc
     Subnets: Select both private subnets
     Security group: vibe-charting-lambda-sg
     ```
   
   - Function-specific settings:
     ```
     Data Ingestion:
     - Timeout: 5 minutes
     - Memory: 512 MB
     
     Trend Analysis:
     - Timeout: 10 minutes
     - Memory: 1024 MB
     
     Query Processor:
     - Timeout: 30 seconds
     - Memory: 256 MB
     ```

   - Environment variables:
     ```
     Data Ingestion:
     DB_SECRET_NAME: vibe-charting/database
     CMC_API_SECRET_NAME: vibe-charting/cmc-api-key

     Trend Analysis & Query Processor:
     DB_SECRET_NAME: vibe-charting/database
     ```

### 6. EventBridge (CloudWatch Events) Setup

1. **Create Data Ingestion Schedule:**
   - Go to Amazon EventBridge
   - Click "Create rule"
   - Settings:
     ```
     Name: vibe-charting-data-ingestion
     Description: Triggers data ingestion daily at 6 AM UTC
     Schedule: cron(0 6 * * ? *)
     ```
   - Target:
     - Select Lambda function
     - Function: vibe-charting-data-ingestion

2. **Create Trend Analysis Schedule:**
   - Click "Create rule"
   - Settings:
     ```
     Name: vibe-charting-trend-analysis
     Description: Triggers trend analysis at 6:30 AM UTC
     Schedule: cron(30 6 * * ? *)
     ```
   - Target:
     - Select Lambda function
     - Function: vibe-charting-trend-analysis

### 7. API Gateway Configuration

1. **Create API:**
   - Go to API Gateway Dashboard
   - Click "Create API"
   - Choose "REST API"
   - Settings:
     ```
     API name: vibe-charting-api
     Description: REST API for trend analysis chatbot
     Endpoint Type: Regional
     ```

2. **Create Resources and Methods:**
   - Click "Actions" → "Create Resource"
   - Resource name: `query`
   - Click "Create Method" → Select "POST"
   - Integration type: Lambda Function
   - Lambda function: vibe-charting-query-processor

3. **Enable CORS:**
   - Select the resource
   - Click "Actions" → "Enable CORS"
   - Access-Control-Allow-Origin: `*` (or your domain)
   - Access-Control-Allow-Headers: Add required headers

4. **Deploy API:**
   - Click "Actions" → "Deploy API"
   - Stage name: `prod`
   - Note the invoke URL

### 8. CloudWatch Monitoring Setup

1. **Create Dashboard:**
   - Go to CloudWatch Dashboard
   - Click "Create dashboard"
   - Name: `vibe-charting-dashboard`
   - Add widgets for each component:
     
     **Lambda Functions Widgets:**
     ```
     Widget type: Line graph
     Metrics:
     - Invocations (per function)
     - Errors (per function)
     - Duration (per function)
     - Throttles (per function)
     Period: 5 minutes
     ```

     **API Gateway Widgets:**
     ```
     Widget type: Line graph
     Metrics:
     - Latency (p95, p99)
     - 4XX errors
     - 5XX errors
     - Total API calls
     Period: 1 minute
     ```

     **RDS Widgets:**
     ```
     Widget type: Line graph
     Metrics:
     - CPU Utilization
     - Free Storage Space
     - Database Connections
     - Read/Write IOPS
     Period: 5 minutes
     ```

2. **Create Alarms:**

   **Lambda Function Alarms:**
   - For each function (data-ingestion, trend-analysis, query-processor):
     ```
     Metric: Errors
     Threshold: >= 1 error in 5 minutes
     Action: SNS -> vibe-charting-alerts
     ```
     ```
     Metric: Duration
     Threshold: > 75% of timeout setting
     Action: SNS -> vibe-charting-alerts
     ```

   **Data Freshness Alarm:**
   ```
   Create custom metric:
   - Namespace: VibeCharting
   - MetricName: DataFreshness
   - Dimensions: None
   - Unit: Seconds
   
   Alarm settings:
   - Threshold: > 7200 seconds (2 hours)
   - Period: 5 minutes
   - Action: SNS -> vibe-charting-alerts
   ```

   **API Gateway Alarms:**
   ```
   Metric: 5XX Error Rate
   Threshold: >= 1% of requests in 5 minutes
   Action: SNS -> vibe-charting-alerts
   ```
   ```
   Metric: Latency (p95)
   Threshold: > 1000ms
   Action: SNS -> vibe-charting-alerts
   ```

   **RDS Alarms:**
   ```
   Metric: CPU Utilization
   Threshold: > 80% for 5 minutes
   Action: SNS -> vibe-charting-alerts
   ```
   ```
   Metric: Free Storage Space
   Threshold: < 20% free
   Action: SNS -> vibe-charting-alerts
   ```
   ```
   Metric: Database Connections
   Threshold: > 80% of max_connections
   Action: SNS -> vibe-charting-alerts
   ```

3. **Log Groups Configuration:**
   - Go to CloudWatch Logs
   - For each Lambda function log group:
     ```
     Group name: /aws/lambda/vibe-charting-[function-name]
     Retention: 30 days
     ```
   - For API Gateway:
     ```
     Group name: API-Gateway-Execution-Logs_[API-ID]/prod
     Retention: 30 days
     ```

4. **Metric Filters (Optional):**
   Create metric filters for Lambda logs to track specific events:
   ```
   Filter pattern: "ERROR"
   Metric namespace: VibeCharting
   Metric name: ErrorCount
   Metric value: 1
   ```
   ```
   Filter pattern: "Data ingestion completed"
   Metric namespace: VibeCharting
   Metric name: IngestionSuccess
   Metric value: 1
   ```

### 9. SNS Notifications

1. **Create Topic:**
   - Go to SNS Dashboard
   - Click "Create topic"
   - Name: `vibe-charting-alerts`
   - Type: Standard

2. **Add Subscription:**
   - Select topic
   - Click "Create subscription"
   - Protocol: Email
   - Endpoint: Your email address

## Security Checklist

- [ ] Database credentials in Secrets Manager
- [ ] API keys in Secrets Manager
- [ ] RDS in private subnets
- [ ] Security groups properly configured
- [ ] RDS encryption enabled
- [ ] Lambda functions in VPC
- [ ] CloudWatch logs enabled
- [ ] IAM roles with minimal permissions
- [ ] CORS configured in API Gateway

## Testing Steps

1. **Database Connection:**
   - Use pgAdmin or psql to test connection
   - Run sample queries

2. **Lambda Functions:**
   - Use "Test" button in Lambda Console
   - Check CloudWatch logs

3. **API Endpoints:**
   - Use Postman or curl to test endpoints
   - Verify CORS settings

## Cost Optimization

### Estimated Monthly Costs (MVP)

| Service | Configuration | Estimated Cost |
|---------|---------------|----------------|
| Lambda | 3 functions, ~10,000 invocations | $5 |
| API Gateway | ~5,000 API calls | $2 |
| CloudWatch | Basic monitoring | $3 |
| **Total** | | **~$10/month** |

### Cost Optimization Tips

1. **Lambda**: Right-size memory allocation based on usage
2. **API Gateway**: Consider using HTTP API instead of REST for lower costs
3. **CloudWatch**: Set log retention periods to reduce storage costs
4. **Data Transfer**: Keep Lambda functions in same AZ as RDS
5. **Execution**: Daily data collection reduces Lambda invocations

## Next Steps

1. Run database migrations
2. Upload Lambda function code
3. Test end-to-end functionality
4. Monitor CloudWatch metrics
5. Set up alerts and notifications 

## **✅ Required CORS Configuration:**

### **1. Gateway responses:**
- ✅ **Check both boxes**: `Default 4XX` and `Default 5XX`
- This ensures CORS headers are included in error responses

### **2. Access-Control-Allow-Methods:**
- ✅ **Check both**: `OPTIONS` and `POST`
- These are the only HTTP methods your API supports

### **3. Access-Control-Allow-Headers:**
Replace the current content with:
```
Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token
```

### **4. Access-Control-Allow-Origin:**
**For Development/Testing:**
```
*
```

**For Production (replace with your actual frontend domain):**
```
https://your-frontend-domain.amplifyapp.com
```

### **5. Additional Settings:**

**Access-Control-Expose-Headers:**
```
X-RateLimit-Limit,X-RateLimit-Remaining,X-RateLimit-Reset
```

**Access-Control-Max-Age:**
```
3600
```

**Access-Control-Allow-Credentials:**
- ✅ **Check this box** if you plan to use cookies or authentication
- For API key authentication, this should be checked

## **🔒 Security Recommendation:**

Once you deploy your frontend to AWS Amplify, **update** the `Access-Control-Allow-Origin` from `*` to your specific domain:

```
https://main.d1234567890.amplifyapp.com
```

This prevents other websites from making requests to your API from browsers.

## **⚠️ Important Notes:**

1. **API Key Header**: Notice `X-Api-Key` is included in the allowed headers - this is for when you add API key authentication
2. **Credentials**: If you enable this, remember that you cannot use `*` for origin - you must specify the exact domain
3. **Rate Limit Headers**: The expose headers will allow your frontend to read rate limiting information

**Configure these settings and then click "Save" to apply the CORS configuration.**

After saving, you'll need to **re-deploy your API** for the changes to take effect! 

## 1. **API Key Authentication**

1. Go to your API in API Gateway
2. Click on "API Keys" in the left sidebar
3. Click "Create API Key"
   ```
   Name: vibe-charting-api-key
   Description: API Key for Vibe Charting MVP
   ```
4. Go back to your `/query` POST method
5. Click on "Method Request"
6. Set "API Key Required" to `true`
7. Go to "Usage Plans" in the left sidebar
8. Create a new usage plan:
   ```
   Name: vibe-charting-usage-plan
   Description: Rate limits for Vibe Charting MVP
   Rate: 100 requests per minute
   Burst: 200 requests
   Quota: 10000 requests per month (adjust as needed)
   ```
9. Associate the API key with the usage plan
10. Re-deploy the API

## 2. **CORS Configuration**

Ensure CORS is properly configured to only allow requests from your frontend domain:

1. Go to your `/query` resource
2. Click on the OPTIONS method
3. Update CORS configuration:
   ```
   Access-Control-Allow-Origin: https://your-frontend-domain.com
   Access-Control-Allow-Headers: Content-Type,X-Api-Key
   Access-Control-Allow-Methods: OPTIONS,POST
   ```

## 3. **Rate Limiting**

The usage plan above includes rate limiting, but you can also add:

1. Go to "Throttling" in your API settings
2. Set up per-client throttling limits
3. Configure burst limits

## Using the API Key in Requests

Your frontend will need to include the API key in requests:

```javascript
const response = await fetch('https://your-api.execute-api.region.amazonaws.com/prod/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Api-Key': 'your-api-key-here'
  },
  body: JSON.stringify({
    query: "What coins are going up?",
    filters: {
      timeframe: "24h"
    }
  })
});
```

## Additional Security Recommendations

1. **WAF (Web Application Firewall)**
   - Set up AWS WAF to protect against common web exploits
   - Block suspicious IP addresses
   - Add rate-based rules

2. **CloudWatch Alarms**
   - Monitor for unusual spikes in API usage
   - Set up alerts for high error rates
   - Track API key usage

3. **Request Validation**
   - Add request validators in API Gateway
   - Implement strict input validation in Lambda

Would you like me to guide you through implementing any of these security measures? We should at least set up the API key and proper CORS configuration for the MVP. 