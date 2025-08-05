#!/usr/bin/env python3
"""
Configuration settings for historical data backfill script
"""

import os
from typing import Dict, Any

class Config:
    """Configuration class for historical backfill"""
    
    def __init__(self):
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from environment variables"""
        
        # CoinGecko API Configuration
        self.coingecko_api_key = os.getenv('COINGECKO_API_KEY')
        if not self.coingecko_api_key:
            raise ValueError("COINGECKO_API_KEY environment variable required")
        
        # Use CoinGecko's On-Chain DEX API
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        self.rate_limit_delay = 2  # seconds between API requests
        self.days_to_fetch = 30    # 30 days of historical data
        
        # Date range configuration (optional)
        self.start_date = os.getenv('START_DATE')  # Format: YYYY-MM-DD
        self.end_date = os.getenv('END_DATE')      # Format: YYYY-MM-DD
        self.use_date_range = bool(self.start_date and self.end_date)
        
        # If no date range specified, calculate default (30 days ago to yesterday)
        if not self.use_date_range:
            from datetime import datetime, timedelta
            yesterday = datetime.now() - timedelta(days=1)
            thirty_days_ago = yesterday - timedelta(days=30)
            self.calculated_start_date = thirty_days_ago.strftime('%Y-%m-%d')
            self.calculated_end_date = yesterday.strftime('%Y-%m-%d')
        
        # Database Configuration
        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'database': os.getenv('DB_NAME'), 
            'user': os.getenv('DB_USERNAME'),
            'password': os.getenv('DB_PASSWORD'),
            'port': int(os.getenv('DB_PORT', 5432))
        }
        
        # Validate database configuration
        required_db_fields = ['host', 'database', 'user', 'password']
        missing_fields = [field for field in required_db_fields if not self.db_config[field]]
        
        if missing_fields:
            raise ValueError(f"Missing required database environment variables: {', '.join(missing_fields)}")
        
        # Execution Configuration
        self.max_retries = 3
        self.request_timeout = 30
        self.skip_existing_data = True  # Skip pools that already have sufficient historical data
        
        print("✅ Configuration loaded successfully")
        print(f"   - Database: {self.db_config['host']}/{self.db_config['database']}")
        print(f"   - API Key: {'Present' if self.coingecko_api_key else 'Missing'}")
        print(f"   - Historical period: {self.days_to_fetch} days")
        print(f"   - Rate limit delay: {self.rate_limit_delay} seconds")
        
        if self.use_date_range:
            print(f"   - Date range mode: {self.start_date} to {self.end_date}")
        else:
            print(f"   - Date range mode: {self.calculated_start_date} to {self.calculated_end_date} (30 days)")
    
    def get_db_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return self.db_config.copy()
    
    def get_api_headers(self) -> Dict[str, str]:
        """Get API headers with authentication for CoinGecko"""
        return {
            'Accept': 'application/json',
            'User-Agent': 'VibeCharting-Historical/1.0',
            'x-cg-demo-api-key': self.coingecko_api_key
        }

# Global configuration instance
config = Config()