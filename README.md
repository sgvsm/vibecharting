# Crypto Trend Analysis Chatbot - Backend Infrastructure

## Project Overview

This repository contains the backend infrastructure for the Crypto Trend Analysis Chatbot MVP, a proof-of-concept system that analyzes cryptocurrency price trends and provides natural language query responses about market conditions.

## MVP Scope

The system supports analysis and queries for:
- **Basic Trends**: Uptrend, Downtrend, Sideways movement
- **Advanced Signals**: 
  - "Bottomed Out" (trend reversal detection)
  - "Pump & Dump" (volatility spike detection)

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway    │    │   Lambda        │
│   (EC2/nginx)   │◄──►│                  │◄──►│   Functions     │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                       ┌──────────────────┐              │
                       │   EventBridge    │              │
                       │   (Cron Jobs)    │──────────────┘
                       └──────────────────┘              │
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  CoinMarketCap  │◄──►│   PostgreSQL     │◄──►│   Lambda        │
│      API        │    │     (RDS)        │    │   Functions     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Technology Stack

- **Database**: PostgreSQL on Amazon RDS
- **Backend**: Python Lambda Functions
- **Data Source**: CoinMarketCap API
- **Scheduler**: Amazon EventBridge
- **API**: AWS API Gateway
- **Frontend Hosting**: EC2 with nginx (alternative: AWS Amplify)

## Repository Structure

```
/
├── docs/                    # Documentation
├── infrastructure/          # AWS Infrastructure as Code
├── lambda_functions/        # Lambda function source code
├── database/               # SQL migration files and schemas
├── scripts/                # Utility scripts
└── tests/                  # Test files
```

## Implementation Phases

1. **Phase 1: Data Infrastructure** (Week 1-2)
   - Database setup and migrations
   - Data ingestion Lambda function
   - CoinMarketCap API integration

2. **Phase 2: Analysis Engine** (Week 2-3)
   - Trend analysis Lambda functions
   - Signal detection algorithms
   - Data processing pipeline

3. **Phase 3: API Layer** (Week 3-4)
   - Query processing Lambda functions
   - API Gateway setup
   - Response formatting

4. **Phase 4: Infrastructure & Deployment** (Week 4)
   - EC2 setup for frontend
   - CI/CD pipeline
   - Monitoring and logging

## Getting Started

**👉 Start Here**: Read the [Project Summary](docs/00-project-summary.md) for a complete overview and next steps.

See the individual documentation files in the `/docs` directory for detailed setup instructions and architectural decisions:

- **[Project Summary](docs/00-project-summary.md)** - Complete overview and next steps
- **[Architecture Decisions](docs/01-architecture-decisions.md)** - Technology choices and rationale  
- **[Database Schema](docs/02-database-schema.md)** - PostgreSQL schema design
- **[Implementation Roadmap](docs/03-implementation-roadmap.md)** - 4-week development plan
- **[API Specifications](docs/04-api-specifications.md)** - REST API definitions
- **[AWS Infrastructure Setup](docs/05-aws-infrastructure-setup.md)** - Step-by-step AWS guide
- **[AWS Amplify Frontend Setup](docs/06-aws-amplify-frontend-setup.md)** - Frontend deployment guide 