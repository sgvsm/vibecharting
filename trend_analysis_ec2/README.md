# Trend Analysis EC2 Test Suite

This directory contains scripts to test the trend analysis functionality directly on EC2 before deploying to Lambda.

## Prerequisites

Ensure you have exported the following environment variables on your EC2 instance:

```bash
export DB_HOST=your-database-host
export DB_NAME=vibe_charting
export DB_USERNAME=your-username
export DB_PASSWORD=your-password
export DB_PORT=5432
```

## Installation

1. Install dependencies:
```bash
pip3 install -r trend_analysis_ec2/requirements.txt
```

## Testing

1. **Test Database Connection**
```bash
python3 trend_analysis_ec2/test_database_connection.py
```
This will verify that your database connection works and show basic statistics.

2. **Run Sample Analysis**
```bash
# Analyze a specific cryptocurrency
python3 trend_analysis_ec2/run_sample_analysis.py USDC

# Or analyze the first available cryptocurrency
python3 trend_analysis_ec2/run_sample_analysis.py
```
This runs the analysis on a single cryptocurrency for debugging.

3. **Run Full Analysis**
```bash
python3 trend_analysis_ec2/run_trend_analysis.py
```
This runs the complete trend analysis on all active cryptocurrencies, exactly as the Lambda function would.

## Files

- `requirements.txt` - Python package dependencies
- `test_database_connection.py` - Tests database connectivity
- `run_sample_analysis.py` - Runs analysis on a single crypto for debugging
- `run_trend_analysis.py` - Runs the full Lambda handler locally
- `README.md` - This file

## Logs

The full analysis creates a timestamped log file: `trend_analysis_YYYYMMDD_HHMMSS.log`

## Troubleshooting

1. **Import errors**: Make sure you run the scripts from the main `vibecharting` directory
2. **Database connection errors**: Verify your environment variables are set correctly
3. **Missing data**: Check that you have price data in the database using the connection test

## Expected Output

When running successfully, you should see:
- Number of cryptocurrencies processed
- Trends detected and stored
- Signals identified
- Execution time

Example:
```
TREND ANALYSIS EC2 TEST RUNNER
================================================================================
Processed: 35 cryptocurrencies
Trends stored: 70
Signals detected: 12
Duration: 15.34 seconds
```