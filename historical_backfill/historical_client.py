#!/usr/bin/env python3
"""
CoinGecko historical data client for fetching OHLCV data from On-Chain DEX API
"""

import requests
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from config import config

class CoinGeckoHistoricalClient:
    """Client for fetching historical OHLCV data from CoinGecko On-Chain DEX API"""
    
    def __init__(self):
        self.base_url = config.coingecko_base_url
        self.headers = config.get_api_headers()
        self.rate_limit_delay = config.rate_limit_delay
        self.days_to_fetch = config.days_to_fetch
        self.max_retries = config.max_retries
        self.request_timeout = config.request_timeout
        
        print(f"✅ CoinGecko client initialized")
        print(f"   - Base URL: {self.base_url}")
        print(f"   - Rate limit delay: {self.rate_limit_delay}s")
        print(f"   - Days to fetch: {self.days_to_fetch}")
    
    def get_pool_historical_data(self, pool_address: str, pool_symbol: str) -> List[Dict[str, Any]]:
        """
        Fetch historical daily OHLCV data for a Solana pool
        
        Args:
            pool_address: Solana pool contract address
            pool_symbol: Pool symbol for logging
            
        Returns:
            List of historical data points in price_data format
        """
        print(f"   Fetching historical data for {pool_symbol} ({pool_address[:8]}...)")
        
        try:
            # Construct CoinGecko On-Chain DEX API endpoint
            url = f"{self.base_url}/onchain/networks/solana/pools/{pool_address}/ohlcv/day"
            
            # API parameters
            params = {
                'limit': self.days_to_fetch  # Default 30 days of daily data
            }
            
            # Add date range parameters
            from datetime import datetime
            
            if config.use_date_range:
                # Use environment variable dates
                start_date = config.start_date
                end_date = config.end_date
            else:
                # Use calculated dates (30 days ago to yesterday)
                start_date = config.calculated_start_date
                end_date = config.calculated_end_date
            
            # Convert dates to Unix timestamps
            start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
            end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
            
            params['before_timestamp'] = end_timestamp
            print(f"   Date range: {start_date} to {end_date}")
            print(f"   Timestamps: {start_timestamp} to {end_timestamp}")
            
            print(f"   API URL: {url}")
            print(f"   Parameters: {params}")
            
            # Make request with retry logic
            for attempt in range(self.max_retries):
                try:
                    response = requests.get(
                        url, 
                        headers=self.headers, 
                        params=params, 
                        timeout=self.request_timeout
                    )
                    
                    print(f"   Response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"   API response received: {len(data.get('data', {}).get('attributes', {}).get('ohlcv_list', []))} data points")
                        
                        # Transform OHLCV data to price_data format
                        historical_data = self.transform_ohlcv_data(data, pool_symbol)
                        
                        # Filter by date range
                        from datetime import datetime
                        
                        if config.use_date_range:
                            filter_start_date = datetime.strptime(config.start_date, '%Y-%m-%d')
                            filter_end_date = datetime.strptime(config.end_date, '%Y-%m-%d')
                        else:
                            filter_start_date = datetime.strptime(config.calculated_start_date, '%Y-%m-%d')
                            filter_end_date = datetime.strptime(config.calculated_end_date, '%Y-%m-%d')
                        
                        filtered_data = []
                        for data_point in historical_data:
                            data_date = data_point['timestamp'].date()
                            if filter_start_date.date() <= data_date <= filter_end_date.date():
                                filtered_data.append(data_point)
                        
                        historical_data = filtered_data
                        print(f"   Filtered to {len(historical_data)} data points within date range")
                        
                        # Rate limiting
                        time.sleep(self.rate_limit_delay)
                        
                        return historical_data
                    
                    elif response.status_code == 404:
                        print(f"   ⚠️ Pool not found on CoinGecko: {pool_symbol}")
                        return []
                    
                    elif response.status_code == 429:
                        print(f"   ⚠️ Rate limit exceeded, retrying in 60 seconds...")
                        time.sleep(60)
                        continue
                    
                    else:
                        print(f"   ❌ API request failed with status {response.status_code}")
                        if attempt < self.max_retries - 1:
                            print(f"   Retrying in {self.rate_limit_delay * 2} seconds...")
                            time.sleep(self.rate_limit_delay * 2)
                            continue
                        else:
                            print(f"   Max retries exceeded for {pool_symbol}")
                            return []
                
                except requests.exceptions.RequestException as e:
                    print(f"   ❌ Request error for {pool_symbol}: {str(e)}")
                    if attempt < self.max_retries - 1:
                        print(f"   Retrying in {self.rate_limit_delay * 2} seconds...")
                        time.sleep(self.rate_limit_delay * 2)
                        continue
                    else:
                        print(f"   Max retries exceeded for {pool_symbol}")
                        return []
        
        except Exception as e:
            print(f"   ❌ Unexpected error fetching data for {pool_symbol}: {str(e)}")
            return []
    
    def transform_ohlcv_data(self, api_response: Dict[str, Any], pool_symbol: str) -> List[Dict[str, Any]]:
        """
        Transform CoinGecko OHLCV data to price_data format
        
        Args:
            api_response: Raw API response from CoinGecko
            pool_symbol: Pool symbol for logging
            
        Returns:
            List of transformed data points
        """
        try:
            # Extract OHLCV data from CoinGecko response
            # Fixed: CoinGecko API returns data in data.attributes.ohlcv_list
            ohlcv_list = api_response.get('data', {}).get('attributes', {}).get('ohlcv_list', [])
            
            if not ohlcv_list:
                print(f"   ⚠️ No OHLCV data found for {pool_symbol}")
                return []
            
            print(f"   Transforming {len(ohlcv_list)} OHLCV data points for {pool_symbol}")
            
            transformed_data = []
            
            for ohlcv_point in ohlcv_list:
                try:
                    # CoinGecko OHLCV format: [timestamp, open, high, low, close, volume]
                    # Timestamp is in seconds (not milliseconds) for CoinGecko
                    timestamp_s, open_price, high_price, low_price, close_price, volume = ohlcv_point
                    
                    # Convert timestamp from seconds to datetime
                    timestamp = datetime.fromtimestamp(timestamp_s, tz=timezone.utc)
                    
                    # Create price data record
                    price_data = {
                        'timestamp': timestamp,
                        'price_usd': float(close_price),
                        'volume_24h': float(volume),
                        'market_cap': None,  # Not available in OHLCV data
                        'price_change_24h': None,  # Calculate if needed
                        'price_change_percentage_24h': None  # Calculate if needed
                    }
                    
                    transformed_data.append(price_data)
                
                except (ValueError, TypeError, IndexError) as e:
                    print(f"   ⚠️ Error transforming OHLCV point for {pool_symbol}: {str(e)}")
                    continue
            
            print(f"   ✅ Successfully transformed {len(transformed_data)} data points for {pool_symbol}")
            return transformed_data
        
        except Exception as e:
            print(f"   ❌ Error transforming data for {pool_symbol}: {str(e)}")
            return []
    
    def test_api_connection(self) -> bool:
        """
        Test API connection with a simple request
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            print("🔍 Testing CoinGecko API connection...")
            
            # Test with ping endpoint
            url = f"{self.base_url}/ping"
            
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.request_timeout
            )
            
            print(f"   Test URL: {url}")
            print(f"   Test response status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ CoinGecko API connection successful")
                return True
            elif response.status_code == 401:
                print("❌ CoinGecko API authentication failed - check your API key")
                return False
            else:
                print(f"❌ CoinGecko API connection failed: {response.status_code}")
                if response.text:
                    print(f"   Response: {response.text[:200]}")
                return False
        
        except Exception as e:
            print(f"❌ CoinGecko API connection error: {str(e)}")
            return False