import requests
import logging
import time
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class CoinMarketCapClient:
    """Client for CoinMarketCap API v1"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://pro-api.coinmarketcap.com/v1'
        self.session = requests.Session()
        self.session.headers.update({
            'X-CMC_PRO_API_KEY': api_key,
            'Accept': 'application/json',
            'Accept-Encoding': 'deflate, gzip'
        })
    
    def get_latest_quotes(self, cmc_ids: List[int]) -> Dict[str, Any]:
        """
        Fetch latest quotes for specified cryptocurrency IDs
        
        Args:
            cmc_ids: List of CoinMarketCap cryptocurrency IDs
            
        Returns:
            Dictionary containing price data for each cryptocurrency
        """
        try:
            # Convert list to comma-separated string
            ids_str = ','.join(map(str, cmc_ids))
            
            # API endpoint
            url = f"{self.base_url}/cryptocurrency/quotes/latest"
            
            # Parameters
            params = {
                'id': ids_str,
                'convert': 'USD'
            }
            
            logger.info(f"Making API request to CoinMarketCap for {len(cmc_ids)} cryptocurrencies")
            
            # Make request with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.session.get(url, params=params, timeout=30)
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        raise e
                    logger.warning(f"API request failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                    time.sleep(2 ** attempt)  # Exponential backoff
            
            # Parse response
            data = response.json()
            
            if data.get('status', {}).get('error_code') != 0:
                error_msg = data.get('status', {}).get('error_message', 'Unknown API error')
                raise Exception(f"CoinMarketCap API error: {error_msg}")
            
            logger.info(f"Successfully received data for {len(data.get('data', {}))} cryptocurrencies")
            
            # Return the data section
            return data.get('data', {})
            
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {str(e)}")
            raise Exception(f"Failed to fetch data from CoinMarketCap: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error fetching CoinMarketCap data: {str(e)}")
            raise
    
    def transform_data_for_storage(self, cmc_data: Dict[str, Any], crypto_mapping: Dict[int, int]) -> List[Dict[str, Any]]:
        """
        Transform CoinMarketCap API response data for database storage
        
        Args:
            cmc_data: Raw data from CoinMarketCap API
            crypto_mapping: Mapping from CMC ID to internal crypto ID
            
        Returns:
            List of dictionaries ready for database insertion
        """
        transformed_data = []
        
        for cmc_id_str, coin_data in cmc_data.items():
            try:
                cmc_id = int(cmc_id_str)
                
                # Get internal crypto ID
                crypto_id = crypto_mapping.get(cmc_id)
                if not crypto_id:
                    logger.warning(f"No internal ID found for CMC ID {cmc_id}")
                    continue
                
                # Extract USD quote data
                usd_quote = coin_data.get('quote', {}).get('USD', {})
                
                if not usd_quote:
                    logger.warning(f"No USD quote data for {coin_data.get('symbol', 'Unknown')}")
                    continue
                
                # Transform to database format
                price_record = {
                    'crypto_id': crypto_id,
                    'price_usd': float(usd_quote.get('price', 0)),
                    'volume_24h': float(usd_quote.get('volume_24h', 0)),
                    'market_cap': float(usd_quote.get('market_cap', 0)),
                    'percent_change_1h': float(usd_quote.get('percent_change_1h', 0)),
                    'percent_change_24h': float(usd_quote.get('percent_change_24h', 0)),
                    'percent_change_7d': float(usd_quote.get('percent_change_7d', 0)),
                    'last_updated': usd_quote.get('last_updated')
                }
                
                transformed_data.append(price_record)
                
            except (ValueError, KeyError) as e:
                logger.warning(f"Error transforming data for CMC ID {cmc_id_str}: {str(e)}")
                continue
        
        logger.info(f"Transformed {len(transformed_data)} price records for storage")
        return transformed_data
    
    def get_cryptocurrency_map(self, symbols: List[str] = None) -> Dict[str, Any]:
        """
        Get cryptocurrency ID map from CoinMarketCap
        
        Args:
            symbols: Optional list of symbols to filter by
            
        Returns:
            Dictionary containing cryptocurrency mapping data
        """
        try:
            url = f"{self.base_url}/cryptocurrency/map"
            
            params = {}
            if symbols:
                params['symbol'] = ','.join(symbols)
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status', {}).get('error_code') != 0:
                error_msg = data.get('status', {}).get('error_message', 'Unknown API error')
                raise Exception(f"CoinMarketCap API error: {error_msg}")
            
            return data.get('data', [])
            
        except Exception as e:
            logger.error(f"Error fetching cryptocurrency map: {str(e)}")
            raise
    
    def close(self):
        """Close the session"""
        if self.session:
            self.session.close() 