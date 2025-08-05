#!/usr/bin/env python3
"""
Main script for historical data backfill
Fetches 30 days of historical OHLCV data for all active Solana pools
"""

import sys
import traceback
from datetime import datetime, timezone
from typing import List, Dict, Any

from config import config
from database_client import HistoricalDatabaseClient
from historical_client import CoinGeckoHistoricalClient

def print_banner():
    """Print startup banner"""
    print("=" * 60)
    print("🏛️  HISTORICAL DATA BACKFILL - 30 DAYS")
    print("=" * 60)
    print(f"Started at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    if config.use_date_range:
        print(f"Target: Daily OHLCV data from {config.start_date} to {config.end_date}")
    else:
        print(f"Target: Daily OHLCV data from {config.calculated_start_date} to {config.calculated_end_date}")
    
    print(f"Rate limit: {config.rate_limit_delay}s between requests")
    print("=" * 60)

def print_summary(results: Dict[str, Any]):
    """Print execution summary"""
    print("\n" + "=" * 60)
    print("📊 BACKFILL SUMMARY")
    print("=" * 60)
    
    print(f"✅ Successful pools: {results['successful_count']}")
    print(f"⏭️  Skipped pools (had data): {results['skipped_count']}")
    print(f"❌ Failed pools: {results['failed_count']}")
    print(f"📊 Total records stored: {results['total_records']}")
    print(f"⏱️  Total execution time: {results['duration']:.2f} seconds")
    
    if results['failed_pools']:
        print(f"\n❌ Failed pool symbols:")
        for pool_symbol, error in results['failed_pools']:
            print(f"   - {pool_symbol}: {error}")
    
    if results['skipped_pools']:
        print(f"\n⏭️  Skipped pool symbols:")
        for pool_symbol in results['skipped_pools']:
            print(f"   - {pool_symbol}")
    
    print("\n" + "=" * 60)

def validate_environment():
    """Validate environment and configuration"""
    print("🔍 Validating environment...")
    
    try:
        # Test database connection
        db_client = HistoricalDatabaseClient()
        db_client.connect()
        print("✅ Database connection: OK")
        db_client.disconnect()
        
        # Test API connection
        api_client = CoinGeckoHistoricalClient()
        if api_client.test_api_connection():
            print("✅ CoinGecko API connection: OK")
        else:
            print("❌ CoinGecko API connection: FAILED")
            return False
            
        print("✅ Environment validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Environment validation failed: {str(e)}")
        return False

def main():
    """Main execution function"""
    start_time = datetime.now(timezone.utc)
    
    # Print banner
    print_banner()
    
    # Validate environment
    if not validate_environment():
        print("❌ Environment validation failed. Exiting.")
        sys.exit(1)
    
    # Initialize clients
    db_client = None
    api_client = None
    
    try:
        db_client = HistoricalDatabaseClient()
        api_client = CoinGeckoHistoricalClient()
    except Exception as e:
        print(f"❌ Failed to initialize clients: {str(e)}")
        sys.exit(1)
    
    # Results tracking
    results = {
        'successful_count': 0,
        'skipped_count': 0,
        'failed_count': 0,
        'total_records': 0,
        'failed_pools': [],
        'skipped_pools': [],
        'duration': 0
    }
    
    try:
        # Initialize clients
        print("\n🔧 Initializing clients...")
        db_client = HistoricalDatabaseClient()
        api_client = CoinGeckoHistoricalClient()
        
        # Connect to database
        db_client.connect()
        
        # Get active pools
        print("\n📋 Fetching active pools...")
        active_pools = db_client.get_active_pools()
        
        if not active_pools:
            print("❌ No active pools found. Exiting.")
            sys.exit(1)
        
        print(f"🎯 Processing {len(active_pools)} active pools...")
        
        # Process each pool
        for i, pool in enumerate(active_pools, 1):
            pool_symbol = pool['symbol']
            pool_id = pool['id']
            pool_address = pool['coingecko_id']
            
            print(f"\n[{i}/{len(active_pools)}] Processing {pool_symbol}...")
            
            try:
                # Check if pool already has sufficient historical data
                if config.skip_existing_data:
                    if config.use_date_range:
                        has_data = db_client.check_existing_historical_data(
                            pool_id, config.days_to_fetch, 
                            config.start_date, config.end_date
                        )
                    else:
                        has_data = db_client.check_existing_historical_data(
                            pool_id, config.days_to_fetch,
                            config.calculated_start_date, config.calculated_end_date
                        )
                    
                    if has_data:
                        print(f"   ⏭️  Skipping {pool_symbol} - already has sufficient historical data")
                        results['skipped_count'] += 1
                        results['skipped_pools'].append(pool_symbol)
                        db_client.log_backfill_progress(pool_symbol, 'skipped', 0, 'Already has sufficient data')
                        continue
                
                # Fetch historical data from CoinGecko
                historical_data = api_client.get_pool_historical_data(pool_address, pool_symbol)
                
                if not historical_data:
                    print(f"   ⚠️ No historical data available for {pool_symbol}")
                    results['failed_count'] += 1
                    results['failed_pools'].append((pool_symbol, "No historical data available"))
                    db_client.log_backfill_progress(pool_symbol, 'failed', 0, 'No historical data available')
                    continue
                
                # Store in database
                records_stored = db_client.store_historical_data(pool_id, historical_data)
                
                # Update results
                results['successful_count'] += 1
                results['total_records'] += records_stored
                
                # Log success
                db_client.log_backfill_progress(pool_symbol, 'completed', records_stored)
                print(f"   ✅ Successfully processed {pool_symbol}: {records_stored} records")
                
            except Exception as e:
                error_msg = str(e)
                print(f"   ❌ Failed to process {pool_symbol}: {error_msg}")
                results['failed_count'] += 1
                results['failed_pools'].append((pool_symbol, error_msg))
                
                # Log failure
                db_client.log_backfill_progress(pool_symbol, 'failed', 0, error_msg)
                
                # Continue with next pool
                continue
        
        # Calculate execution time
        end_time = datetime.now(timezone.utc)
        results['duration'] = (end_time - start_time).total_seconds()
        
        # Print summary
        print_summary(results)
        
        # Generate database summary
        print("\n📊 Database Summary:")
        try:
            db_summary = db_client.get_backfill_summary()
            print(f"Total pools in database: {db_summary['total_pools']}")
            print(f"Total historical records: {db_summary['total_records']}")
            
            # Show pools with sufficient data
            sufficient_data_pools = [p for p in db_summary['pools'] if p['record_count'] >= 20]
            print(f"Pools with sufficient data (20+ records): {len(sufficient_data_pools)}")
            
        except Exception as e:
            print(f"❌ Error generating database summary: {str(e)}")
        
        # Success message
        if results['failed_count'] == 0:
            print("\n🎉 All pools processed successfully!")
        elif results['successful_count'] > 0:
            print(f"\n✅ Partial success: {results['successful_count']} pools processed")
        else:
            print("\n❌ No pools were processed successfully")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Critical error during execution: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        # Clean up database connection
        if db_client:
            try:
                db_client.disconnect()
            except Exception as cleanup_error:
                print(f"⚠️ Error during cleanup: {str(cleanup_error)}")
    
    print(f"\n🏁 Backfill completed at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)