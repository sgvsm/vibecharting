# Crypto Trend Analysis Chatbot - API Reference

## 🌐 API Overview

The Crypto Trend Analysis Chatbot API provides natural language query processing for cryptocurrency trend analysis. The API is designed to be simple, intuitive, and powerful for analyzing market conditions.

**Base URL**: `https://api.vibe-charting.com/prod`  
**Protocol**: HTTPS  
**Format**: JSON  
**Authentication**: None (MVP) / API Key (future)  
**Rate Limiting**: 100 requests/minute per IP

## 📋 Quick Start

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

### Response Format

```json
{
  "success": true,
  "data": {
    "intent": {
      "type": "uptrend",
      "confidence": 0.85,
      "timeframe": "24h",
      "original_query": "What coins are going up today?"
    },
    "results": [
      {
        "cryptocurrency": {
          "symbol": "BTC",
          "name": "Bitcoin"
        },
        "trend_type": "uptrend",
        "confidence": 0.85,
        "price_change_percent": 12.5,
        "current_price": 48500.00,
        "analysis_period": {
          "start_time": "2025-01-01T10:45:00Z",
          "end_time": "2025-01-01T11:45:00Z"
        }
      }
    ]
  },
  "meta": {
    "timestamp": "2025-01-01T12:00:00Z",
    "execution_time_ms": 145,
    "version": "1.0.0"
  }
}
```

## 🔍 Endpoints

### POST /query

Processes natural language queries about cryptocurrency trends.

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | ✅ | Natural language query |
| `filters` | object | ❌ | Optional filters |
| `filters.timeframe` | string | ❌ | Analysis timeframe |
| `filters.min_confidence` | number | ❌ | Minimum confidence threshold |
| `filters.limit` | number | ❌ | Maximum results to return |

#### Query Examples

**Basic Queries:**
```json
{
  "query": "What coins are going up today?"
}
```

**With Filters:**
```json
{
  "query": "Show me the top 5 trending coins",
  "filters": {
    "timeframe": "7d",
    "min_confidence": 0.8,
    "limit": 5
  }
}
```

**Advanced Queries:**
```json
{
  "query": "Which cryptocurrencies are showing pump and dump patterns?",
  "filters": {
    "timeframe": "24h",
    "min_confidence": 0.6
  }
}
```

#### Supported Query Types

| Intent Type | Description | Example Queries |
|-------------|-------------|-----------------|
| `uptrend` | Find cryptocurrencies in uptrend | "What coins are going up?", "Show me trending coins" |
| `downtrend` | Find cryptocurrencies in downtrend | "What coins are falling?", "Which coins are down?" |
| `sideways` | Find cryptocurrencies moving sideways | "What coins are stable?", "Show me sideways coins" |
| `pump_and_dump` | Find pump and dump patterns | "Pump and dump coins", "Volatile coins" |
| `bottomed_out` | Find bottomed out patterns | "Coins that bottomed out", "Reversal candidates" |
| `volume_spike` | Find volume anomalies | "High volume coins", "Volume spikes" |
| `trend_reversal` | Find trend reversals | "Reversal patterns", "Trend changes" |
| `market_overview` | General market overview | "Market summary", "Overall trends" |

#### Timeframe Options

| Value | Description |
|-------|-------------|
| `1h` | Last hour |
| `24h` | Last 24 hours |
| `7d` | Last 7 days |
| `30d` | Last 30 days |

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Request success status |
| `data.intent` | object | Query interpretation details |
| `data.results` | array | Analysis results |
| `data.results[].cryptocurrency` | object | Crypto details |
| `data.results[].trend_type` | string | Detected trend type |
| `data.results[].confidence` | number | Analysis confidence (0-1) |
| `data.results[].price_change_percent` | number | Price change percentage |
| `data.results[].current_price` | number | Current price in USD |
| `data.results[].analysis_period` | object | Analysis time period |
| `meta.timestamp` | string | Response timestamp |
| `meta.execution_time_ms` | number | Request processing time |
| `meta.version` | string | API version |

## 🚨 Error Handling

### Error Response Format

```json
{
  "success": false,
  "data": null,
  "meta": {
    "timestamp": "2025-01-01T12:00:00Z",
    "execution_time_ms": 89,
    "version": "1.0.0"
  },
  "error": {
    "code": "INVALID_QUERY",
    "message": "Query could not be understood",
    "details": "No valid intent detected in query text"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_QUERY` | 400 | Query could not be understood |
| `INVALID_FILTERS` | 400 | Invalid filter parameters |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

### Common Error Scenarios

**Invalid Query:**
```json
{
  "error": {
    "code": "INVALID_QUERY",
    "message": "Query could not be understood",
    "details": "No valid intent detected in query text"
  }
}
```

**Invalid Filters:**
```json
{
  "error": {
    "code": "INVALID_FILTERS",
    "message": "Invalid filter parameters",
    "details": "timeframe must be one of: 1h, 24h, 7d, 30d"
  }
}
```

**Rate Limit Exceeded:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests",
    "details": "Rate limit: 100 requests per minute"
  }
}
```

## 📊 Response Examples

### Uptrend Query

**Request:**
```json
{
  "query": "What coins are trending up in the last 24 hours?",
  "filters": {
    "timeframe": "24h",
    "min_confidence": 0.7,
    "limit": 5
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "intent": {
      "type": "uptrend",
      "confidence": 0.92,
      "timeframe": "24h",
      "original_query": "What coins are trending up in the last 24 hours?"
    },
    "results": [
      {
        "cryptocurrency": {
          "symbol": "BTC",
          "name": "Bitcoin"
        },
        "trend_type": "uptrend",
        "confidence": 0.89,
        "price_change_percent": 15.2,
        "current_price": 48500.00,
        "analysis_period": {
          "start_time": "2025-01-01T10:45:00Z",
          "end_time": "2025-01-01T11:45:00Z"
        }
      },
      {
        "cryptocurrency": {
          "symbol": "ETH",
          "name": "Ethereum"
        },
        "trend_type": "uptrend",
        "confidence": 0.85,
        "price_change_percent": 12.8,
        "current_price": 3200.00,
        "analysis_period": {
          "start_time": "2025-01-01T10:45:00Z",
          "end_time": "2025-01-01T11:45:00Z"
        }
      }
    ]
  },
  "meta": {
    "timestamp": "2025-01-01T12:00:00Z",
    "execution_time_ms": 234,
    "version": "1.0.0"
  }
}
```

### Pump and Dump Query

**Request:**
```json
{
  "query": "Show me coins with pump and dump patterns",
  "filters": {
    "timeframe": "24h",
    "min_confidence": 0.6
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "intent": {
      "type": "pump_and_dump",
      "confidence": 0.88,
      "timeframe": "24h",
      "original_query": "Show me coins with pump and dump patterns"
    },
    "results": [
      {
        "cryptocurrency": {
          "symbol": "DOGE",
          "name": "Dogecoin"
        },
        "trend_type": "pump_and_dump",
        "confidence": 0.82,
        "price_change_percent": 45.6,
        "current_price": 0.085,
        "analysis_period": {
          "start_time": "2025-01-01T10:45:00Z",
          "end_time": "2025-01-01T11:45:00Z"
        },
        "signal_metadata": {
          "volume_spike_ratio": 8.5,
          "price_volatility": 0.67,
          "pump_duration_hours": 4.2
        }
      }
    ]
  },
  "meta": {
    "timestamp": "2025-01-01T12:00:00Z",
    "execution_time_ms": 189,
    "version": "1.0.0"
  }
}
```

## 🔧 Best Practices

### Query Optimization

1. **Be Specific**: Use clear, specific queries
   ```
   ✅ "Show me the top 5 trending coins in the last 24 hours"
   ❌ "What's happening?"
   ```

2. **Use Appropriate Timeframes**: Match timeframe to your analysis needs
   ```
   ✅ "What coins are trending up in the last 7 days?"
   ❌ "What coins are trending up today?" (too vague)
   ```

3. **Set Confidence Thresholds**: Use min_confidence to filter results
   ```
   ✅ filters: {"min_confidence": 0.8}
   ❌ No confidence filter (may get low-quality results)
   ```

### Error Handling

1. **Always Check Success Field**: Verify request success before processing data
2. **Handle Rate Limits**: Implement exponential backoff for rate limit errors
3. **Validate Responses**: Check for required fields before using data

### Performance Tips

1. **Use Appropriate Limits**: Set reasonable limits to avoid large responses
2. **Cache Results**: Cache responses for repeated queries
3. **Monitor Execution Time**: Use meta.execution_time_ms for performance monitoring

## 📈 Rate Limiting

- **Limit**: 100 requests per minute per IP
- **Headers**: Rate limit information included in response headers
- **Backoff**: Implement exponential backoff for rate limit errors

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## 🔐 Security

### Current (MVP)
- No authentication required
- Rate limiting by IP address
- CORS enabled for web applications

### Future Enhancements
- API key authentication
- JWT token support
- IP whitelisting
- Request signing

## 📞 Support

For API support:
- Check error messages for specific issues
- Review rate limiting headers
- Monitor execution times for performance issues
- Contact support for persistent errors

## 📋 Changelog

### v1.0.0 (Current)
- Initial API release
- Natural language query processing
- 8 supported intent types
- Basic filtering and pagination
- Rate limiting implementation 