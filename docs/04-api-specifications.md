# API Specifications

## Overview

This document defines the REST API endpoints for the Crypto Trend Analysis Chatbot backend. The API is designed to handle natural language queries and return cryptocurrency trend analysis results.

**MVP Scope**: The initial implementation focuses on the core query processing functionality. Additional endpoints are planned for future releases.

## Base Configuration

- **Base URL**: `https://api.vibe-charting.com` (production)
- **Protocol**: HTTPS
- **Format**: JSON
- **Authentication**: None (MVP) / API Key (future)
- **Rate Limiting**: 100 requests/minute per IP

## Common Response Format

All API responses follow a consistent structure:

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": "2025-01-01T12:00:00Z",
    "execution_time_ms": 145,
    "version": "1.0.0"
  },
  "error": null
}
```

**Error Response Format:**
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

## MVP Endpoints

### 1. Query Processing ✅ **IMPLEMENTED**

**Endpoint**: `POST /query`

**Description**: Processes natural language queries about cryptocurrency trends and returns relevant results.

**Request:**
```json
{
  "query": "What coins are going up today?",
  "filters": {
    "timeframe": "24h",           // Optional: 1h, 24h, 7d, 30d
    "min_confidence": 0.7,        // Optional: 0.0-1.0
    "limit": 10                   // Optional: max results (default: 10)
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
      "confidence": 0.85,
      "cryptocurrencies": [],
      "timeframe": "24h",
      "original_query": "What coins are going up today?"
    },
    "query_interpretation": "Find cryptocurrencies in uptrend in the last 24 hours",
    "results": [
      {
        "id": 1,
        "cryptocurrency": {
          "symbol": "BTC",
          "name": "Bitcoin"
        },
        "trend_type": "uptrend",
        "timeframe": "24h",
        "confidence": 0.85,
        "price_change_percent": 12.5,
        "current_price": 48500.00,
        "analysis_period": {
          "start_time": "2025-01-01T10:45:00Z",
          "end_time": "2025-01-01T11:45:00Z"
        },
        "detected_at": "2025-01-01T11:45:00Z",
        "metadata": {
          "slope": 0.00012345,
          "r_squared": 0.89,
          "volatility": 8.2,
          "data_points": 24
        }
      }
    ],
    "total_matches": 5,
    "filters_applied": {
      "timeframe": "24h",
      "min_confidence": 0.7,
      "limit": 10
    }
  },
  "meta": {
    "timestamp": "2025-01-01T12:00:00Z",
    "execution_time_ms": 245,
    "version": "1.0.0"
  },
  "error": null
}
```

**Supported Query Types:**

| Intent | Example Queries | Response Content |
|--------|----------------|------------------|
| `uptrend` | "What coins are going up?", "Show me bullish trends", "Rising cryptocurrencies" | Cryptocurrencies with positive trends |
| `downtrend` | "What coins are falling?", "Show bearish trends", "Declining prices" | Cryptocurrencies with negative trends |
| `sideways` | "Stable coins", "Sideways movement", "No clear trend" | Cryptocurrencies with sideways trends |
| `bottomed_out` | "Which coins bottomed out?", "Recovery candidates", "Trend reversals" | Potential trend reversals from down to up |
| `pump_and_dump` | "Suspicious activity", "Pump and dump", "Volatile spikes" | Detected unusual price/volume activity |
| `high_volatility` | "Most volatile coins", "Unstable prices", "High volatility" | Cryptocurrencies with high price volatility |
| `volume_spike` | "Volume anomalies", "Trading spikes", "Unusual volume" | Cryptocurrencies with volume anomalies |
| `trending` | "What's trending?", "Popular coins", "Hot cryptocurrencies" | Currently active cryptocurrencies |
| `performance` | "Best performers", "Top gainers", "Worst performers" | Performance-ranked cryptocurrencies |

**Error Codes:**
- `MISSING_BODY`: Request body is required
- `INVALID_JSON`: Invalid JSON in request body
- `EMPTY_QUERY`: Query text is required
- `UNSUPPORTED_INTENT`: Query intent could not be determined
- `INTERNAL_ERROR`: Server error during query processing

**Response Examples by Intent:**

**Pump & Dump Signals:**
```json
{
  "results": [
    {
      "id": 123,
      "cryptocurrency": {"symbol": "DOGE", "name": "Dogecoin"},
      "signal_type": "pump_and_dump",
      "detected_at": "2025-01-01T10:30:00Z",
      "confidence": 0.92,
      "trigger_price": 0.085,
      "current_price": 0.078,
      "volume_spike_ratio": 8.3,
      "metadata": {
        "pump_start_price": 0.075,
        "pump_peak_price": 0.085,
        "pump_increase_percent": 13.3,
        "dump_detected": true,
        "dump_decrease_percent": 8.2
      }
    }
  ]
}
```

**Bottomed Out Signals:**
```json
{
  "results": [
    {
      "id": 124,
      "cryptocurrency": {"symbol": "ADA", "name": "Cardano"},
      "signal_type": "bottomed_out",
      "detected_at": "2025-01-01T09:15:00Z",
      "confidence": 0.76,
      "trigger_price": 0.42,
      "current_price": 0.45,
      "recovery_percent": 7.1,
      "metadata": {
        "lowest_price": 0.42,
        "recovery_percent": 7.1,
        "historical_trend_slope": -0.00001234,
        "recent_trend_slope": 0.00000678
      }
    }
  ]
}
```

**High Volatility Analysis:**
```json
{
  "results": [
    {
      "cryptocurrency": {"symbol": "SHIB", "name": "Shiba Inu"},
      "volatility_percent": 15.4,
      "price_range": {
        "min": 0.000008,
        "max": 0.000012,
        "avg": 0.00001
      },
      "current_price": 0.0000105,
      "data_points": 24,
      "timeframe": "24h"
    }
  ]
}
```

## Future Enhancements 🚀

The following endpoints are planned for future releases:

### 2. Direct Signal Access (Future v2.0)

**Endpoint**: `GET /signals`

**Description**: Returns recent signal events with filtering options.

**Status**: 📋 **Planned for v2.0**

### 3. Historical Trends (Future v2.0)

**Endpoint**: `GET /trends/{symbol}`

**Description**: Returns historical trend analysis for specific cryptocurrencies.

**Status**: 📋 **Planned for v2.0**

### 4. Supported Cryptocurrencies (Future v2.0)

**Endpoint**: `GET /coins`

**Description**: Returns list of supported cryptocurrencies with metadata.

**Status**: 📋 **Planned for v2.0**

### 5. Health Check (Future v2.0)

**Endpoint**: `GET /health`

**Description**: Returns system health status and component availability.

**Status**: 📋 **Planned for v2.0**

## Error Handling

### HTTP Status Codes

| Code | Description | Usage |
|------|-------------|-------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | System maintenance |

### Error Response Examples

**400 Bad Request:**
```json
{
  "success": false,
  "data": null,
  "meta": {
    "timestamp": "2025-01-01T12:00:00Z",
    "execution_time_ms": 15,
    "version": "1.0.0"
  },
  "error": {
    "code": "INVALID_PARAMETERS",
    "message": "Invalid timeframe specified",
    "details": "Timeframe must be one of: 1h, 24h, 7d, 30d"
  }
}
```

**500 Internal Server Error:**
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
    "code": "INTERNAL_ERROR",
    "message": "An error occurred while processing your query",
    "details": "Database connection failed"
  }
}
```

## Request/Response Examples

### Example 1: Basic Uptrend Query

**Request:**
```bash
curl -X POST https://api.vibe-charting.com/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What cryptocurrencies are trending upward?",
    "filters": {
      "timeframe": "24h",
      "limit": 5
    }
  }'
```

### Example 2: Pump and Dump Detection

**Request:**
```bash
curl -X POST https://api.vibe-charting.com/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me suspicious pump and dump activities",
    "filters": {
      "min_confidence": 0.8
    }
  }'
```

### Example 3: Bitcoin-Specific Query

**Request:**
```bash
curl -X POST https://api.vibe-charting.com/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "BTC trends today",
    "filters": {
      "timeframe": "24h"
    }
  }'
```

## Rate Limiting

- **Default Limit**: 100 requests per minute per IP address
- **Burst Allowance**: Up to 10 requests in 1 second
- **Headers**: Rate limit information included in response headers
  - `X-RateLimit-Limit`: Total requests allowed per minute
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

## Security Considerations

1. **Input Validation**: All query parameters are validated and sanitized
2. **SQL Injection Prevention**: Parameterized queries used throughout
3. **CORS**: Configured to allow requests from frontend domain only
4. **Request Size Limits**: Maximum request body size of 10KB
5. **Query Timeout**: Requests timeout after 30 seconds

## Frontend Integration

**JavaScript Example:**
```javascript
const response = await fetch('/api/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        query: "Show me coins going up",
        filters: {
            timeframe: "24h",
            min_confidence: 0.7,
            limit: 10
        }
    })
});

const data = await response.json();
if (data.success) {
    console.log('Results:', data.data.results);
    console.log('Intent:', data.data.intent);
} else {
    console.error('Error:', data.error);
}
```

## Version History

- **v1.0.0** (MVP): Core query processing endpoint
- **v2.0.0** (Planned): Additional endpoints for signals, trends, health check 