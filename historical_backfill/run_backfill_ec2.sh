#!/bin/bash
# Historical Backfill and Trend Analysis Runner for EC2
# Script to run historical backfill on EC2

echo "🚀 Starting Historical Data Backfill for 6 Months"
echo "================================================"

# Set environment variables
export DB_HOST="vibe-charting-db.c9qmo8w2y0a1.us-east-2.rds.amazonaws.com"
export DB_NAME="vibe_charting"
export DB_USERNAME="vibecharting"
export DB_PASSWORD="your-password-here"  # Update this!
export DB_PORT="5432"
export COINGECKO_API_KEY="your-coingecko-api-key-here"  # Update this!

# Optional: Set specific date range (comment out to use default 6 months)
# export START_DATE="2024-08-01"
# export END_DATE="2025-02-01"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing requirements..."
pip install -r requirements.txt

# Run the backfill script
echo "🏛️ Running historical backfill script..."
python3 main_script.py

# Deactivate virtual environment
deactivate

echo "✅ Historical backfill completed!"