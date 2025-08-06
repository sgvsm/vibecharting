# Vibe Charting - AWS Architecture Overview

## 🏗️ System Architecture

The Vibe Charting Trend Analysis Chatbot is built on AWS using a serverless architecture with the following key components:

### **Core Infrastructure Components**

#### **🛢️ Database Layer**
- **Amazon RDS PostgreSQL** (`vibe-charting-db`)
  - **Purpose**: Primary data store for cryptocurrency data and analysis results
  - **Location**: Private subnet in `vibe-charting-vpc`
  - **Security**: Private access only, no public internet exposure
  - **Credentials**: Stored in AWS Secrets Manager (`vibe-charting/database`)

#### **🔐 Security & Credentials**
- **AWS Secrets Manager**
  - **Secret Name**: `vibe-charting/database`
  - **Contents**: Database host, port, database name, username, password
  - **Access**: Lambda functions and EC2 instances via IAM roles
  - **Region**: `us-east-2`

#### **🌐 Network Infrastructure**
- **VPC**: `vibe-charting-vpc` (`10.0.0.0/16`)
  - **Public Subnets**: 
    - `vibe-charting-public-subnet-1` (`10.0.1.0/24`) - AZ: `us-east-2a`
    - `vibe-charting-public-subnet-2` (`10.0.2.0/24`) - AZ: `us-east-2b`
  - **Private Subnets**:
    - `vibe-charting-private-subnet-1` (`10.0.3.0/24`) - AZ: `us-east-2a`
    - `vibe-charting-private-subnet-2` (`10.0.4.0/24`) - AZ: `us-east-2b`

#### **🛡️ Security Groups**
- **RDS Security Group** (`vibe-charting-db-sg`)
  - **Inbound**: PostgreSQL (5432) from Lambda and EC2 security groups
  - **Outbound**: All traffic
- **Lambda Security Group** (`vibe-charting-lambda-sg`)
  - **Inbound**: None (serverless)
  - **Outbound**: All traffic (for API calls and database access)
- **EC2 Security Group** (`vibe-charting-ec2-sg`)
  - **Inbound**: SSH (22) from your IP address
  - **Outbound**: All traffic

---

## 🤖 Serverless Backend Components

### **📊 Data Ingestion Lambda**
- **Function Name**: `vibe-charting-data-ingestion`
- **Purpose**: Fetches cryptocurrency price data from CoinMarketCap API
- **Schedule**: Daily via EventBridge (cron: `0 12 * * ? *`)
- **Data Source**: CoinMarketCap API (50 top cryptocurrencies)
- **Storage**: PostgreSQL via RDS
- **Dependencies**: 
  - `requests` (API calls)
  - `psycopg2-binary` (database)
  - `boto3` (AWS services)

### **📈 Trend Analysis Lambda**
- **Function Name**: `vibe-charting-trend-analysis`
- **Purpose**: Analyzes price data to detect trends and market signals
- **Schedule**: Daily via EventBridge (cron: `0 13 * * ? *`)
- **Analysis Types**:
  - **Trend Detection**: Uptrend, Downtrend, Sideways
  - **Signal Detection**: Pump & Dump, Bottomed Out, Volume Anomaly
  - **Volatility Analysis**: Standard deviation calculations
- **Dependencies**:
  - `numpy`, `scipy` (mathematical analysis)
  - `psycopg2-binary` (database)
  - `boto3` (AWS services)

### **💬 Query Processor Lambda**
- **Function Name**: `vibe-charting-query-processor`
- **Purpose**: Processes natural language queries and returns relevant cryptocurrency data
- **Trigger**: API Gateway HTTP requests
- **Query Types Supported**:
  - **Basic Trends**: "uptrend", "downtrend", "sideways"
  - **Advanced Signals**: "pump and dump", "bottomed out", "volume spike"
  - **Performance**: "best performers", "worst performers"
  - **Volatility**: "high volatility", "low volatility"
- **NLP Features**:
  - Keyword-based intent classification
  - Cryptocurrency symbol extraction
  - Timeframe detection
  - Confidence scoring
- **Dependencies**:
  - `psycopg2-binary` (database)
  - `boto3` (AWS services)

---

## 🌐 API & Frontend Infrastructure

### **🔌 API Gateway**
- **API Name**: `vibe-charting-api`
- **Base URL**: `https://api.vibe-charting.com`
- **Endpoints**:
  - **MVP**: `POST /query` (natural language queries)
  - **Future**: `/signals`, `/trends/{symbol}`, `/coins`, `/health`
- **Authentication**: API Key required
- **Rate Limiting**: Configured for abuse prevention
- **CORS**: Enabled for frontend integration

### **🎨 Frontend Hosting**
- **Platform**: AWS Amplify
- **Repository**: Separate repository (not in this project)
- **Features**:
  - **Chat Interface**: Simple text input for queries
  - **Response Display**: Text-based list of trading pairs
  - **Real-time Updates**: WebSocket or polling for live data
- **Environment Variables**:
  - `REACT_APP_API_BASE_URL`: API Gateway endpoint
  - `REACT_APP_API_KEY`: API authentication key

---

## 📅 Event Scheduling & Automation

### **⏰ EventBridge (CloudWatch Events)**
- **Data Ingestion Schedule**: Daily at 12:00 PM UTC
  - **Cron Expression**: `0 12 * * ? *`
  - **Target**: `vibe-charting-data-ingestion` Lambda
- **Analysis Schedule**: Daily at 1:00 PM UTC
  - **Cron Expression**: `0 13 * * ? *`
  - **Target**: `vibe-charting-trend-analysis` Lambda
- **Cleanup Schedule**: Weekly (optional)
  - **Purpose**: Remove old data to manage storage costs

---

## 📊 Database Schema

### **🗄️ Core Tables**

#### **cryptocurrencies**
- **Purpose**: Master list of tracked cryptocurrencies
- **Key Fields**: `id`, `symbol`, `name`, `cmc_id`, `rank`
- **Indexes**: `symbol`, `cmc_id`

#### **price_data**
- **Purpose**: Historical price data for analysis
- **Key Fields**: `id`, `crypto_id`, `price`, `volume_24h`, `market_cap`, `timestamp`
- **Indexes**: `crypto_id`, `timestamp`
- **Retention**: 90 days (configurable)

#### **trend_analysis**
- **Purpose**: Pre-calculated trend analysis results
- **Key Fields**: `id`, `crypto_id`, `trend_type`, `confidence`, `timeframe`, `created_at`
- **Enums**: `trend_type_enum` ('uptrend', 'downtrend', 'sideways')
- **Indexes**: `crypto_id`, `trend_type`, `created_at`

#### **signal_events**
- **Purpose**: Detected market signals and events
- **Key Fields**: `id`, `crypto_id`, `signal_type`, `confidence`, `detected_at`
- **Enums**: `signal_type_enum` ('pump_and_dump', 'bottomed_out', 'volume_anomaly')
- **Indexes**: `crypto_id`, `signal_type`, `detected_at`

#### **analysis_runs**
- **Purpose**: Audit trail of analysis executions
- **Key Fields**: `id`, `run_type`, `records_processed`, `started_at`, `completed_at`
- **Enums**: `run_type_enum` ('data_ingestion', 'trend_analysis', 'cleanup')

#### **query_logs**
- **Purpose**: User query history and analytics
- **Key Fields**: `id`, `query_text`, `intent_type`, `intent_confidence`, `result_count`
- **Indexes**: `intent_type`, `created_at`

---

## 🔧 Development & Deployment

### **📁 Project Structure**
```
vibecharting/
├── database/
│   ├── migrations/          # SQL migration files
│   └── seeds/              # Initial data scripts
├── lambda_functions/
│   ├── data_ingestion/     # Price data collection
│   ├── trend_analysis/     # Market analysis
│   └── query_processor/    # Query handling
├── docs/                   # Architecture documentation
└── secrets/               # Credential templates
```

### **🚀 Deployment Process**
1. **Infrastructure Setup**: Manual AWS Console configuration
2. **Database Migration**: EC2 bastion host approach
3. **Lambda Deployment**: Manual code upload via AWS Console
4. **Frontend Deployment**: AWS Amplify from Git repository

### **🔍 Monitoring & Logging**
- **CloudWatch Logs**: All Lambda function logs
- **CloudWatch Metrics**: API Gateway performance
- **CloudWatch Alarms**: Error rate and latency monitoring
- **SNS Notifications**: Critical error alerts

---

## 💰 Cost Optimization

### **📊 Estimated Monthly Costs**
- **RDS PostgreSQL**: ~$25-50/month (t3.micro, 20GB storage)
- **Lambda Functions**: ~$5-10/month (minimal usage)
- **API Gateway**: ~$5-15/month (based on requests)
- **Amplify Hosting**: ~$1/month (static hosting)
- **Secrets Manager**: ~$0.40/month per secret
- **EventBridge**: ~$1/month (scheduled events)
- **CloudWatch**: ~$5-10/month (logs and metrics)

### **💰 Total Estimated Cost**: $40-90/month

### **🎯 Cost Optimization Strategies**
- **Data Retention**: 90-day retention policy for price data
- **Lambda Optimization**: Efficient code to minimize execution time
- **RDS Scaling**: Start with t3.micro, scale as needed
- **Caching**: Future implementation of ElastiCache for query results

---

## 🔮 Future Enhancements

### **📈 Planned Features**
1. **Real-time Data**: WebSocket connections for live price updates
2. **Advanced Patterns**: "Two Highs and One Low" algorithm
3. **User Authentication**: AWS Cognito integration
4. **Mobile App**: React Native or Flutter application
5. **Advanced Analytics**: Machine learning for pattern recognition

### **🏗️ Infrastructure Improvements**
1. **CDN**: CloudFront for global content delivery
2. **Caching**: ElastiCache Redis for performance
3. **Monitoring**: X-Ray for distributed tracing
4. **CI/CD**: AWS CodePipeline for automated deployments
5. **Terraform**: Infrastructure as Code for reproducibility

---

## 🔐 Security Considerations

### **🛡️ Current Security Measures**
- **Private RDS**: No public internet access
- **IAM Roles**: Least privilege access for Lambda functions
- **Secrets Manager**: Encrypted credential storage
- **VPC Isolation**: Network-level security
- **API Keys**: Authentication for API access
- **CORS**: Cross-origin request protection

### **🔒 Security Best Practices**
- **Regular Updates**: Keep dependencies updated
- **Access Logging**: Monitor all API and database access
- **Backup Strategy**: Automated RDS snapshots
- **Disaster Recovery**: Multi-AZ RDS deployment
- **Compliance**: GDPR and data privacy considerations

---

## 📞 Support & Maintenance

### **🔧 Regular Maintenance Tasks**
- **Database Cleanup**: Weekly automated cleanup of old data
- **Security Updates**: Monthly dependency updates
- **Performance Monitoring**: Weekly review of CloudWatch metrics
- **Backup Verification**: Monthly backup restoration tests

### **🚨 Incident Response**
- **Error Monitoring**: CloudWatch Alarms for critical errors
- **SNS Notifications**: Immediate alerting for issues
- **Rollback Procedures**: Lambda function version management
- **Documentation**: Runbook for common issues

