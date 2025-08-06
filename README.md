# Crypto Trend Analysis Chatbot - Backend Infrastructure

## 🚀 Quick Start

This repository contains the backend infrastructure for the Crypto Trend Analysis Chatbot MVP, a proof-of-concept system that analyzes cryptocurrency price trends and provides natural language query responses about market conditions.

**👉 New to the project?** Start with the [Complete Setup Guide](docs/SETUP_GUIDE.md) for step-by-step deployment instructions.

## 📋 Project Overview

### MVP Scope

The system supports analysis and queries for:
- **Basic Trends**: Uptrend, Downtrend, Sideways movement
- **Advanced Signals**: 
  - "Bottomed Out" (trend reversal detection)
  - "Pump & Dump" (volatility spike detection)
  - "Volume Anomaly" (unusual volume patterns)
  - "Parabolic Rise" (accelerating growth)
  - "Capitulation Drop" (sustained decline)

### Technology Stack

- **Database**: PostgreSQL on Amazon RDS
- **Backend**: Python Lambda Functions
- **Data Source**: CoinGecko API (migrated from CoinMarketCap)
- **Scheduler**: Amazon EventBridge
- **API**: AWS API Gateway
- **Frontend Hosting**: AWS Amplify

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway    │    │   Lambda        │
│   (Amplify)     │◄──►│                  │◄──►│   Functions     │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                       ┌──────────────────┐              │
                       │   EventBridge    │              │
                       │   (Cron Jobs)    │──────────────┘
                       └──────────────────┘              │
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CoinGecko     │◄──►│   PostgreSQL     │◄──►│   Lambda        │
│      API        │    │     (RDS)        │    │   Functions     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📚 Documentation

### 🎯 Getting Started
- **[Complete Setup Guide](docs/SETUP_GUIDE.md)** - Step-by-step deployment instructions
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation with examples
- **[Documentation Index](docs/README.md)** - Comprehensive documentation overview

### 🏗️ Architecture & Design
- **[Project Summary](docs/00-project-summary.md)** - Complete project overview
- **[Architecture Decisions](docs/01-architecture-decisions.md)** - Technology choices and rationale
- **[Database Schema](docs/02-database-schema.md)** - PostgreSQL schema design
- **[AWS Architecture Overview](docs/aws-architecture-overview.md)** - Infrastructure design

### 🔧 Implementation
- **[Implementation Roadmap](docs/03-implementation-roadmap.md)** - 4-week development plan
- **[API Specifications](docs/04-api-specifications.md)** - REST API definitions
- **[AWS Infrastructure Setup](docs/05-aws-infrastructure-setup.md)** - Detailed AWS setup
- **[Lambda Functions Setup](docs/07-lambda-functions-setup.md)** - Lambda deployment guide

### 📊 Analysis & Requirements
- **[Database Schema Review](docs/10-database-schema-review.md)** - Schema optimization
- **[Keyword Requirements Analysis](docs/11-keyword-requirements-analysis.md)** - Client requirements
- **[Future Schema Requirements](docs/12-future-schema-requirements.md)** - Future enhancements

## 📁 Repository Structure

```
/
├── docs/                    # 📚 Comprehensive documentation
│   ├── README.md           # Documentation index
│   ├── SETUP_GUIDE.md      # Complete setup guide
│   ├── API_REFERENCE.md    # API documentation
│   └── [detailed docs]     # Architecture, implementation, etc.
├── lambda_functions/        # 🔧 Lambda function source code
│   ├── data_ingestion/     # Data collection from CoinGecko
│   ├── trend_analysis/     # Statistical trend analysis
│   └── query_processor/    # Natural language processing
├── database/               # 🗄️ SQL migrations and schemas
│   ├── migrations/         # Database schema migrations
│   └── seeds/             # Initial data seeding
├── frontend/              # 🎨 React frontend application
├── historical_backfill/    # 📈 Historical data processing
├── trend_analysis_ec2/    # 🔬 EC2-based analysis tools
└── secrets/               # 🔐 Credential templates
```

## 🚀 Quick Deployment

### Prerequisites
- AWS Account with appropriate permissions
- PostgreSQL client (for database setup)
- Basic knowledge of AWS services

### Deployment Steps
1. **Setup AWS Infrastructure**: Follow [Complete Setup Guide](docs/SETUP_GUIDE.md)
2. **Deploy Database**: Use migrations in `database/migrations/`
3. **Deploy Lambda Functions**: Follow [Lambda Setup Guide](docs/07-lambda-functions-setup.md)
4. **Test API**: Use [API Reference](docs/API_REFERENCE.md) for testing

## 📊 Expected Costs

**Estimated Monthly Cost: ~$25-50**
- RDS (db.t3.micro): ~$15
- Lambda Functions: ~$5
- API Gateway: ~$2
- CloudWatch/Monitoring: ~$3
- Additional services: ~$5-20

## 🔍 API Quick Start

### Basic Query Example

```bash
curl -X POST https://api.vibe-charting.com/prod/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What coins are going up today?",
    "filters": {
      "timeframe": "24h",
      "min_confidence": 0.7,
      "limit": 10
    }
  }'
```

### Supported Query Types
- **Uptrend**: "What coins are going up?"
- **Downtrend**: "Which coins are falling?"
- **Pump & Dump**: "Show me volatile coins"
- **Bottomed Out**: "Coins that bottomed out"
- **Volume Spikes**: "High volume coins"
- **Market Overview**: "Market summary"

## 📈 Project Status

### ✅ Completed
- Database schema design and migrations
- AWS infrastructure setup
- Lambda function architecture
- API specifications and implementation
- Migration from CoinMarketCap to CoinGecko
- Enhanced trend detection patterns

### 🔄 In Progress
- Historical data implementation
- Performance optimization
- Enhanced monitoring and alerting

### 📋 Planned
- Additional signal detection algorithms
- Advanced query processing
- Frontend application development

## 🤝 Contributing

When contributing to this project:

1. **Follow Documentation**: Use the comprehensive docs in `/docs`
2. **Test Changes**: Verify functionality before submitting
3. **Update Documentation**: Keep docs in sync with code changes
4. **Follow Architecture**: Maintain the established patterns

## 📞 Support

For questions and support:
1. Check the [Documentation Index](docs/README.md) for relevant guides
2. Review [Troubleshooting sections](docs/SETUP_GUIDE.md#troubleshooting) in setup guides
3. Consult [API Reference](docs/API_REFERENCE.md) for API-specific issues
4. Check CloudWatch logs for detailed error information

## 📄 License

This project is part of the Crypto Trend Analysis Chatbot MVP. See individual documentation files for specific licensing information. 