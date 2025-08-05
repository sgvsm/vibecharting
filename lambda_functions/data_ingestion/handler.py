import json
import os
from datetime import datetime, timezone
from coingecko_client import CoinGeckoClient
from database import DatabaseManager

# FORCE UPDATE: This is version 2.0 - Lambda must use this code
VERSION = "2.0"

def lambda_handler(event, context):
    """
    Main Lambda handler for cryptocurrency data ingestion
    Fetches latest price data from CoinGecko and stores in database
    VERSION: 2.0 - FORCE UPDATE
    """
    start_time = datetime.now(timezone.utc)
    print(f"=== VERSION {VERSION} - Data ingestion started at {start_time} ===")
    
    db_manager = None
    try:
        # Initialize database manager
        print("Step 1: Initializing database manager")
        db_manager = DatabaseManager()
        print("Step 1: Database manager initialized successfully")
        
        print("Step 2: Connecting to database")
        db_manager.connect()
        print("Step 2: Database connection established successfully")
        
        # Simple test: Try to fetch cryptocurrencies immediately
        print("Step 3: Testing database query...")
        try:
            test_cryptos = db_manager.get_cryptocurrencies()
            print(f"Step 3: Database test successful: Found {len(test_cryptos)} cryptocurrencies")
            if test_cryptos:
                print(f"Step 3: First crypto: {test_cryptos[0]}")
        except Exception as e:
            print(f"Step 3: Database test failed: {str(e)}")
            raise
        
        # Initialize CoinGecko client with API key from environment
        print("Step 4: Initializing CoinGecko client")
        api_key = os.environ.get('COINGECKO_API_KEY')
        print(f"Step 4: API key found: {'Yes' if api_key else 'No'}")
        coingecko_client = CoinGeckoClient(api_key=api_key)
        print("Step 4: CoinGecko client initialized successfully")
        
        # Get active cryptocurrencies from database
        print("Step 5: Fetching active cryptocurrencies from database")
        try:
            active_cryptos = db_manager.get_cryptocurrencies()
            print(f"Step 5: Found {len(active_cryptos)} active cryptocurrencies")
        except Exception as e:
            print(f"Step 5: Error fetching cryptocurrencies: {str(e)}")
            raise
        
        if not active_cryptos:
            print("Step 5: No active cryptocurrencies found in database")
            return {
                'statusCode': 200,
                'body': json.dumps('No active cryptocurrencies to process')
            }
        
        # Debug: Log first few cryptocurrencies
        print(f"Step 5: First 3 cryptocurrencies: {active_cryptos[:3]}")
        
        # Fetch latest quotes from GeckoTerminal
        print("Step 6: Fetching latest quotes from GeckoTerminal API")
        try:
            solana_pool_ids = [crypto['coingecko_id'] for crypto in active_cryptos if crypto.get('coingecko_id')]
            print(f"Step 6: Extracted {len(solana_pool_ids)} Solana pool IDs")
            print(f"Step 6: First 3 Solana pool IDs: {solana_pool_ids[:3]}")
        except Exception as e:
            print(f"Step 6: Error extracting Solana pool IDs: {str(e)}")
            raise
        
        if not solana_pool_ids:
            print("Step 6: No Solana pool IDs found in active cryptocurrencies")
            return {
                'statusCode': 200,
                'body': json.dumps('No cryptocurrencies with Solana pool IDs to process')
            }
        
        try:
            crypto_data = coingecko_client.get_latest_quotes(solana_pool_ids)
            print(f"Step 6: Received data for {len(crypto_data)} cryptocurrencies")
        except Exception as e:
            print(f"Step 6: Error fetching from GeckoTerminal: {str(e)}")
            raise
        
        # Transform data for storage
        print("Step 7: Transforming data for storage")
        price_records = []
        timestamp = datetime.now(timezone.utc)
        
        # Create mapping from Solana pool ID to internal crypto ID
        crypto_mapping = {crypto['coingecko_id']: crypto['id'] for crypto in active_cryptos if crypto.get('coingecko_id')}
        
        for pool_id, coin_data in crypto_data.items():
            try:
                crypto_id = crypto_mapping.get(pool_id)
                
                if not crypto_id:
                    print(f"Step 7: No internal ID found for Solana pool ID {pool_id}")
                    continue
                
                # Extract USD quote data
                usd_quote = coin_data.get('quote', {}).get('USD', {})
                
                if not usd_quote:
                    print(f"Step 7: No USD quote data for {coin_data.get('symbol', 'Unknown')}")
                    continue
                
                # Create price record
                price_record = (
                    crypto_id,
                    timestamp,
                    float(usd_quote.get('price', 0)),
                    float(usd_quote.get('volume_24h', 0)) if usd_quote.get('volume_24h') else None,
                    float(usd_quote.get('market_cap', 0)) if usd_quote.get('market_cap') else None,
                    None,  # percent_change_1h not available in GeckoTerminal API
                    float(usd_quote.get('percent_change_24h', 0)) if usd_quote.get('percent_change_24h') else None,
                    None   # percent_change_7d not available in GeckoTerminal API
                )
                
                price_records.append(price_record)
                
            except (ValueError, KeyError) as e:
                print(f"Step 7: Error processing data for Solana pool ID {pool_id}: {str(e)}")
                continue
        
        # Store data in database
        print("Step 8: Storing price data in database")
        stored_count = db_manager.insert_price_data(price_records)
        print(f"Step 8: Successfully stored {stored_count} price records")
        
        # Log successful ingestion run
        print("Step 9: Logging successful ingestion run")
        db_manager.log_ingestion_run('coingecko', stored_count, True)
        
        # Log completion
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        print(f"Step 10: Data ingestion completed in {duration:.2f} seconds")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Data ingestion successful',
                'processed_count': stored_count,
                'duration_seconds': duration,
                'timestamp': end_time.isoformat()
            })
        }
        
    except Exception as e:
        error_msg = f"Error during data ingestion: {str(e)}"
        print(f"ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        
        # Log failed ingestion run
        if db_manager:
            try:
                db_manager.log_ingestion_run('coingecko', 0, False, error_msg)
            except Exception as log_error:
                print(f"Failed to log ingestion run: {str(log_error)}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': error_msg,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        }
        
    finally:
        # Clean up database connection
        if db_manager:
            try:
                db_manager.disconnect()
            except Exception as cleanup_error:
                print(f"Error during cleanup: {str(cleanup_error)}") 