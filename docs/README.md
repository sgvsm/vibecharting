# Crypto Trend Analysis Chatbot - Documentation

## 📚 Documentation Overview

This directory contains comprehensive documentation for the Crypto Trend Analysis Chatbot project. The documentation is organized into logical sections to help you find the information you need quickly.

## 🚀 Quick Start

**New to the project?** Start here:
1. **[Project Overview](#project-overview)** - High-level system description
2. **[Getting Started](#getting-started)** - Setup and deployment guide
3. **[Architecture](#architecture)** - System design and technology choices

## 📋 Documentation Structure

### 🎯 Project Overview
- **[00-project-summary.md](00-project-summary.md)** - Complete project overview and MVP scope
- **[01-architecture-decisions.md](01-architecture-decisions.md)** - Technology choices and rationale

### 🏗️ Architecture & Design
- **[02-database-schema.md](02-database-schema.md)** - Complete PostgreSQL schema design
- **[aws-architecture-overview.md](aws-architecture-overview.md)** - AWS infrastructure architecture
- **[03-implementation-roadmap.md](03-implementation-roadmap.md)** - 4-week development plan

### 🔧 Implementation Guides
- **[04-api-specifications.md](04-api-specifications.md)** - REST API endpoint definitions
- **[05-aws-infrastructure-setup.md](05-aws-infrastructure-setup.md)** - Step-by-step AWS setup
- **[06-aws-amplify-frontend-setup.md](06-aws-amplify-frontend-setup.md)** - Frontend deployment
- **[07-lambda-functions-setup.md](07-lambda-functions-setup.md)** - Lambda deployment guide

### 📊 Analysis & Requirements
- **[10-database-schema-review.md](10-database-schema-review.md)** - Schema optimization analysis
- **[11-keyword-requirements-analysis.md](11-keyword-requirements-analysis.md)** - Client keyword analysis
- **[12-future-schema-requirements.md](12-future-schema-requirements.md)** - Future schema enhancements

### 🔄 Migration & Historical Data
- **[13-coinmarketcap-to-coingecko-migration-plan.md](13-coinmarketcap-to-coingecko-migration-plan.md)** - API migration plan
- **[15-complete-migration-execution-guide.md](15-complete-migration-execution-guide.md)** - Migration execution guide
- **[16-historical-data-implementation-plan.md](16-historical-data-implementation-plan.md)** - Historical data setup

## 🎯 Project Overview

### System Purpose
The Crypto Trend Analysis Chatbot is an MVP system that analyzes cryptocurrency price trends and provides natural language query responses about market conditions.

### MVP Scope
- **Data Collection**: Daily price data for specific cryptocurrencies
- **Trend Analysis**: Uptrend, downtrend, and sideways movement detection
- **Signal Detection**: "Pump & Dump" and "Bottomed Out" event identification
- **Natural Language Queries**: Chat interface for trend inquiries (8 intent types)
- **Automated Processing**: Scheduled analysis and pre-computed results

### Technology Stack
- **Database**: PostgreSQL on Amazon RDS
- **Backend**: Python Lambda Functions
- **Data Source**: CoinGecko API (migrated from CoinMarketCap)
- **Scheduler**: Amazon EventBridge
- **API**: AWS API Gateway
- **Frontend**: AWS Amplify

## 🏗️ Architecture

### System Architecture
```
Frontend (AWS Amplify) → API Gateway → Query Processor Lambda ↔ PostgreSQL (RDS)
                                        ↕
                        Data Ingestion Lambda ← EventBridge (Scheduler)
                                        ↕
                                CoinGecko API
                                        ↕
                        Trend Analysis Lambda ↔ PostgreSQL (RDS)
```

### Key Components
- **3 Lambda Functions**: Data ingestion, trend analysis, query processing
- **PostgreSQL Database**: Time-series data with optimized schema
- **EventBridge Scheduling**: Daily data collection and analysis
- **API Gateway**: Single REST endpoint (`POST /query`)

## 🚀 Getting Started

### For Developers
1. **Setup AWS Infrastructure**: Follow [05-aws-infrastructure-setup.md](05-aws-infrastructure-setup.md)
2. **Deploy Database**: Use [02-database-schema.md](02-database-schema.md) for schema
3. **Deploy Lambda Functions**: Follow [07-lambda-functions-setup.md](07-lambda-functions-setup.md)
4. **Setup Frontend**: Use [06-aws-amplify-frontend-setup.md](06-aws-amplify-frontend-setup.md)

### For Operations
1. **Monitor System**: Check CloudWatch logs and metrics
2. **Verify Data Quality**: Run database queries from schema documentation
3. **Troubleshoot Issues**: Use troubleshooting sections in setup guides

### For Migrations
1. **API Migration**: Follow [15-complete-migration-execution-guide.md](15-complete-migration-execution-guide.md)
2. **Historical Data**: Use [16-historical-data-implementation-plan.md](16-historical-data-implementation-plan.md)

## 📊 Expected Costs

**Estimated Monthly Cost: ~$25-50**
- RDS (db.t3.micro): ~$15
- Lambda Functions: ~$5
- API Gateway: ~$2
- CloudWatch/Monitoring: ~$3
- Additional services: ~$5-20

## 🔍 Documentation by Use Case

### Setting Up the System
- [05-aws-infrastructure-setup.md](05-aws-infrastructure-setup.md) - Complete AWS setup
- [02-database-schema.md](02-database-schema.md) - Database schema and migrations
- [07-lambda-functions-setup.md](07-lambda-functions-setup.md) - Lambda deployment

### Understanding the Architecture
- [01-architecture-decisions.md](01-architecture-decisions.md) - Technology choices
- [aws-architecture-overview.md](aws-architecture-overview.md) - Infrastructure design
- [03-implementation-roadmap.md](03-implementation-roadmap.md) - Development phases

### API Development
- [04-api-specifications.md](04-api-specifications.md) - API endpoints and responses
- [11-keyword-requirements-analysis.md](11-keyword-requirements-analysis.md) - Query requirements

### Database Management
- [02-database-schema.md](02-database-schema.md) - Schema design
- [10-database-schema-review.md](10-database-schema-review.md) - Optimization analysis
- [12-future-schema-requirements.md](12-future-schema-requirements.md) - Future enhancements

### Migration & Upgrades
- [15-complete-migration-execution-guide.md](15-complete-migration-execution-guide.md) - Migration execution
- [13-coinmarketcap-to-coingecko-migration-plan.md](13-coinmarketcap-to-coingecko-migration-plan.md) - Migration planning

## 📈 Project Status

### ✅ Completed
- Database schema design and migrations
- AWS infrastructure setup guide
- Lambda function architecture
- API specifications
- Migration from CoinMarketCap to CoinGecko

### 🔄 In Progress
- Enhanced trend detection patterns
- Historical data implementation
- Performance optimization

### 📋 Planned
- Additional signal detection algorithms
- Advanced query processing
- Enhanced monitoring and alerting

## 🤝 Contributing

When updating documentation:
1. Follow the existing structure and formatting
2. Update this README.md if adding new sections
3. Ensure all links remain valid
4. Add appropriate cross-references between related documents

## 📞 Support

For questions about the documentation or system:
1. Check the troubleshooting sections in setup guides
2. Review the architecture decisions for context
3. Consult the implementation roadmap for development phases 