# Architecture Decision Record (ADR)

## 1. Database Choice: PostgreSQL on Amazon RDS

**Decision**: Use PostgreSQL hosted on Amazon RDS for data storage.

**Rationale**:
- **ACID Compliance**: Ensures data integrity for financial data
- **JSON Support**: Native JSON columns for flexible API response storage
- **Time Series**: Good performance for time-based price data queries
- **Managed Service**: RDS handles backups, updates, and scaling
- **Cost-Effective**: Suitable for MVP with predictable scaling path

**Alternatives Considered**:
- DynamoDB: Rejected due to complex querying requirements for trend analysis
- InfluxDB: Overkill for MVP scope, adds operational complexity

## 2. Backend: AWS Lambda Functions

**Decision**: Implement backend logic using Python Lambda functions.

**Rationale**:
- **Serverless**: No server management, automatic scaling
- **Cost-Effective**: Pay only for execution time
- **Event-Driven**: Perfect for scheduled data collection and API responses
- **Python Ecosystem**: Rich libraries for data analysis (pandas, numpy)

**Function Architecture**:
- **data-ingestion**: Fetches price data from CoinMarketCap API
- **trend-analysis**: Analyzes price data for trends and signals  
- **query-processor**: Handles natural language queries from frontend

**Separate Functions Rationale**:
- **Security**: Each function gets minimal IAM permissions for specific tasks
- **Scalability**: Independent scaling based on usage patterns
- **Robustness**: Component failures don't affect other functions
- **Cost Optimization**: Right-size memory/timeout per function
- **Development**: Parallel development and easier debugging

## 3. Data Source: Coingecko API

**Decision**: Use Coingecko API as the primary data source.

**Rationale**:
- **Free Tier**: 10,000 calls/month sufficient for MVP (hourly updates for 50 tokens)
- **Reliable**: Established provider with good uptime
- **Comprehensive**: Provides price, volume, and market cap data
- **Rate Limits**: 333 calls/minute fits our usage pattern

**Data Collection Strategy**:
- Collect data for specific cryptocurrency list (provided by client)
- Daily data collection (1 point/day per token) to stay within free API limits
- Store 30 days of historical data for trend analysis
- Future enhancement: Automatic token selection by market cap threshold

## 4. Frontend Hosting: AWS Amplify

**Decision**: Use AWS Amplify for frontend hosting.

**Amplify Advantages**:
- **Simplified Deployment**: Git-based deployments
- **Built-in CI/CD**: Automatic builds and deployments
- **Global CDN**: CloudFront distribution included
- **Cost-Effective**: No server management overhead
- **SSL/HTTPS**: Automatic certificate management
- **Perfect for Chat Interface**: Ideal for static frontend with API calls

## 5. API Gateway Configuration

**Decision**: Use AWS API Gateway for Lambda function exposure.

**Configuration**:
- **REST API**: Standard REST endpoints for frontend communication
- **CORS**: Enable cross-origin requests from frontend domain
- **Rate Limiting**: Prevent abuse with reasonable request limits
- **Authentication**: None for MVP (add API keys later if needed)

## 6. Scheduling: Amazon EventBridge

**Decision**: Use EventBridge (CloudWatch Events) for scheduled data collection.

**Schedule Configuration**:
- **Data Ingestion**: Daily at 6 AM UTC (0 6 * * *)
- **Trend Analysis**: 30 minutes after data ingestion (30 6 * * *)
- **Error Handling**: SNS notifications for failed executions

## 7. Token Selection Strategy

**Proposed Approach**: Focus on top 50 cryptocurrencies by market cap.

**Rationale**:
- **Liquidity**: Top tokens have better price discovery
- **User Interest**: Most queries will focus on popular tokens
- **Data Quality**: Better data availability and accuracy
- **API Efficiency**: Single API call can fetch multiple token data



## 8. Data Retention Policy

**Decision**: Implement tiered data retention.

**Retention Tiers**:
- **Raw Price Data**: 30 days (sufficient for trend analysis)
- **Analysis Results**: 90 days (for query response caching)
- **User Query Logs**: 7 days (for debugging and optimization)

## 9. Error Handling and Monitoring

**Strategy**:
- **CloudWatch Logs**: All Lambda function logs
- **CloudWatch Metrics**: Custom metrics for data freshness and API success rates
- **SNS Alerts**: Email notifications for critical failures
- **Retry Logic**: Exponential backoff for API failures 