import json
import os
import logging
from datetime import datetime, timezone, timedelta
from analyzers.trend_analyzer import TrendAnalyzer
from analyzers.signal_detector import SignalDetector
from database import DatabaseClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    """
    Main Lambda handler for cryptocurrency trend analysis
    Analyzes stored price data and detects trends and signals with improved 30-day utilization
    """
    start_time = datetime.now(timezone.utc)
    logger.info(f"Trend analysis started at {start_time}")
    
    run_id = None
    
    try:
        # Initialize database client using environment variables
        logger.info("Initializing database client with environment variables")
        db_client = DatabaseClient()
        
        # Log analysis run start
        run_id = db_client.log_analysis_run('trend_analysis', 'running')
        logger.info(f"Started analysis run with ID: {run_id}")
        
        # Get active cryptocurrencies
        logger.info("Fetching active cryptocurrencies")
        active_cryptos = db_client.get_active_cryptocurrencies()
        
        if not active_cryptos:
            logger.warning("No active cryptocurrencies found")
            if run_id:
                db_client.update_analysis_run(run_id, 'completed', 0)
            return {
                'statusCode': 200,
                'body': json.dumps('No active cryptocurrencies to analyze')
            }
        
        logger.info(f"Analyzing {len(active_cryptos)} cryptocurrencies")
        
        # Initialize analyzers
        trend_analyzer = TrendAnalyzer()
        signal_detector = SignalDetector()
        
        # Track analysis results
        total_trends_stored = 0
        total_signals_detected = 0
        processed_count = 0
        signal_types = {}
        
        # Process each cryptocurrency
        for crypto in active_cryptos:
            try:
                crypto_id = crypto['id']
                symbol = crypto['symbol']
                
                logger.info(f"Analyzing {symbol} (ID: {crypto_id})")
                
                # Get price data for analysis (30 days for better utilization)
                price_data = db_client.get_price_data_for_analysis(
                    crypto_id, 
                    days=30
                )
                
                if len(price_data) < 14:  # Need at least 14 data points
                    logger.warning(f"Insufficient data for {symbol}: {len(price_data)} points")
                    continue
                
                # Perform trend analysis for improved timeframes
                timeframes = ['7d', '14d', '30d']  # Better timeframes for 30-day data
                for timeframe in timeframes:
                    try:
                        trend_result = trend_analyzer.analyze_trend(
                            price_data, 
                            timeframe, 
                            crypto_id
                        )
                        
                        if trend_result:
                            db_client.store_trend_analysis(trend_result)
                            total_trends_stored += 1
                            logger.info(f"Stored trend analysis for {symbol} ({timeframe}): {trend_result['trend_type']} (confidence: {trend_result['confidence']:.2f})")
                        
                    except Exception as e:
                        logger.error(f"Error analyzing trend for {symbol} ({timeframe}): {str(e)}")
                
                # Perform signal detection with improved algorithms
                try:
                    signals = signal_detector.detect_signals(price_data, crypto_id)
                    
                    for signal in signals:
                        db_client.store_signal_event(signal)
                        total_signals_detected += 1
                        signal_type = signal['signal_type']
                        signal_types[signal_type] = signal_types.get(signal_type, 0) + 1
                        logger.info(f"Detected signal for {symbol}: {signal['signal_type']} (confidence: {signal['confidence']:.2f})")
                
                except Exception as e:
                    logger.error(f"Error detecting signals for {symbol}: {str(e)}")
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing {symbol}: {str(e)}")
                continue
        
        # Update analysis run
        if run_id:
            db_client.update_analysis_run(run_id, 'completed', processed_count)
        
        # Calculate duration
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"Analysis completed in {duration:.2f} seconds")
        logger.info(f"Processed: {processed_count} cryptocurrencies")
        logger.info(f"Trends stored: {total_trends_stored}")
        logger.info(f"Signals detected: {total_signals_detected}")
        
        # Log signal breakdown
        if signal_types:
            logger.info("Signal breakdown:")
            for signal_type, count in signal_types.items():
                logger.info(f"  {signal_type}: {count}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Trend analysis completed successfully',
                'processed_count': processed_count,
                'trends_stored': total_trends_stored,
                'signals_detected': total_signals_detected,
                'signal_breakdown': signal_types,
                'duration_seconds': duration,
                'timestamp': end_time.isoformat(),
                'data_utilization': '30-day optimized analysis'
            })
        }
        
    except Exception as e:
        error_msg = f"Error during trend analysis: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # Update analysis run with error
        if run_id:
            try:
                db_client.update_analysis_run(run_id, 'failed', error_message=error_msg)
            except:
                pass
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': error_msg,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        }
    
    finally:
        # Clean up database connection
        try:
            if 'db_client' in locals():
                db_client.close()
        except:
            pass 