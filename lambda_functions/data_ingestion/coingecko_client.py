import requests
import time
from typing import List, Dict, Any

class CoinGeckoClient:
    """Client for GeckoTerminal Solana API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = 'https://api.geckoterminal.com/api/v2'
        self.session = requests.Session()
        
        # Set headers
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'VibeCharting/1.0'
        }
        
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
            
        self.session.headers.update(headers)
    
    def get_latest_quotes(self, solana_pool_ids: List[str]) -> Dict[str, Any]:
        """
        Fetch latest quotes for specified Solana pool contract addresses
        
        Args:
            solana_pool_ids: List of Solana pool contract addresses
            
        Returns:
            Dictionary containing price data for each cryptocurrency
        """
        try:
            transformed_data = {}
            
            print(f"Making API requests to GeckoTerminal for {len(solana_pool_ids)} Solana pools")
            
            # Process each pool individually since GeckoTerminal doesn't support batch requests
            for pool_id in solana_pool_ids:
                try:
                    # API endpoint for Solana pool
                    url = f"{self.base_url}/networks/solana/pools/{pool_id}"
                    
                    print(f"Requesting pool: {pool_id}")
                    print(f"URL: {url}")
                    
                    # Make request
                    response = self.session.get(url, timeout=30)
                    print(f"Response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"Pool {pool_id} response: {data}")
                        
                        # Extract pool data
                        pool_data = data.get('data', {})
                        attributes = pool_data.get('attributes', {})
                        
                        # Get token information
                        token_data = attributes.get('base_token_price_usd', 0)
                        volume_data = attributes.get('volume_usd', {}).get('h24', 0)
                        
                        # Transform to expected format
                        transformed_data[pool_id] = {
                            'id': pool_id,
                            'symbol': pool_id[:8].upper(),  # Use first 8 chars as symbol
                            'name': f"Pool_{pool_id[:8]}",
                            'quote': {
                                'USD': {
                                    'price': token_data,
                                    'volume_24h': volume_data,
                                    'market_cap': 0,  # Not available in pool data
                                    'percent_change_24h': 0,  # Not available in pool data
                                    'last_updated': attributes.get('updated_at')
                                }
                            }
                        }
                        
                        print(f"Successfully processed pool {pool_id}")
                    else:
                        print(f"Failed to get data for pool {pool_id}: {response.status_code}")
                        
                except Exception as e:
                    print(f"Error processing pool {pool_id}: {str(e)}")
                    continue
            
            print(f"Successfully received data for {len(transformed_data)} pools")
            return transformed_data
            
        except requests.exceptions.RequestException as e:
            print(f"HTTP request failed: {str(e)}")
            raise Exception(f"Failed to fetch data from CoinGecko: {str(e)}")
        
        except Exception as e:
            print(f"Error fetching CoinGecko data: {str(e)}")
            raise
    
    def get_cryptocurrency_map(self, symbols: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get cryptocurrency list from CoinGecko
        
        Args:
            symbols: Optional list of symbols to filter by
            
        Returns:
            List containing cryptocurrency mapping data
        """
        try:
            url = f"{self.base_url}/coins/list"
            
            params = {}
            if symbols:
                params['include_platform'] = 'true'
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Filter by symbols if provided
            if symbols:
                symbol_set = set(symbols)
                data = [coin for coin in data if coin.get('symbol', '').upper() in symbol_set]
            
            return data
            
        except Exception as e:
            print(f"Error fetching cryptocurrency map: {str(e)}")
            raise
    
    def close(self):
        """Close the session"""
        if self.session:
            self.session.close() 